from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "merge_qet_kicad_libraries.py"
SPEC = importlib.util.spec_from_file_location("merge_qet_kicad_libraries", MODULE_PATH)
assert SPEC and SPEC.loader
mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = mod
SPEC.loader.exec_module(mod)


def write_lib(path: Path, symbols: list[tuple[str, str, str]]) -> None:
    lines = ["(kicad_symbol_lib (version 20231120) (generator qet_to_kicad)"]
    for name, source_path, value in symbols:
        lines.extend(
            [
                f'  (symbol "{name}"',
                f'    (property "Value" "{value}" (at 0 0 0) (effects (font (size 1 1))))',
                f'    (property "QET_Source_Path" "{source_path}" (at 0 0 0) (effects (font (size 1 1)) (hide yes)))',
                f'    (symbol "{name}_0_1"',
                "    )",
                "  )",
            ]
        )
    lines.append(")")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def test_merge_preserves_unique_symbols(tmp_path: Path):
    a = tmp_path / "electric.kicad_sym"
    b = tmp_path / "logic.kicad_sym"
    write_lib(a, [("Z_Q_A", "10_electric/a.elmt", "Elektrik")])
    write_lib(b, [("Z_Q_B", "20_logic/b.elmt", "Logik")])

    merged, report = mod.merge_libraries([a, b])

    assert report["merged_symbols"] == 2
    assert report["unique_source_paths"] == 2
    assert report["duplicate_internal_names_resolved"] == 0
    assert report["collection_counts"] == {"10_electric": 1, "20_logic": 1}
    assert merged.count('  (symbol "Z_Q_') == 2
    assert '(property "Value" "Elektrik"' in merged
    assert '(property "Value" "Logik"' in merged


def test_merge_resolves_cross_collection_internal_name_collision(tmp_path: Path):
    a = tmp_path / "electric.kicad_sym"
    b = tmp_path / "logic.kicad_sym"
    write_lib(a, [("Z_Q_same", "10_electric/a.elmt", "A")])
    write_lib(b, [("Z_Q_same", "20_logic/b.elmt", "B")])

    merged, report = mod.merge_libraries([a, b])

    assert report["duplicate_internal_names_resolved"] == 1
    assert report["renames"][0]["old_name"] == "Z_Q_same"
    assert report["renames"][0]["new_name"] == "Z_Q_20_logic__same"
    assert '  (symbol "Z_Q_same"' in merged
    assert '  (symbol "Z_Q_20_logic__same"' in merged
    assert '    (symbol "Z_Q_20_logic__same_0_1"' in merged
    assert '(property "Value" "B"' in merged


def test_merge_rejects_duplicate_qet_source_path(tmp_path: Path):
    a = tmp_path / "a.kicad_sym"
    b = tmp_path / "b.kicad_sym"
    write_lib(a, [("Z_Q_A", "10_electric/a.elmt", "A")])
    write_lib(b, [("Z_Q_B", "10_electric/a.elmt", "B")])

    with pytest.raises(ValueError, match="Duplicate QET source path"):
        mod.merge_libraries([a, b])
