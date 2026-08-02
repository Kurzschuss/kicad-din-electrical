from collections import Counter
from pathlib import Path

from tools.generate_quality_report import collect_statistics, render_quality_report


def write_symbol(path: Path, *, name: str | None, policy: str = "", footprint: str = "") -> None:
    if name is None:
        path.write_text("(kicad_symbol_lib)\n", encoding="utf-8")
        return
    policy_property = f'(property "Footprint Policy" "{policy}")' if policy else ""
    path.write_text(
        f'''(kicad_symbol_lib
  (symbol "{name}"
    (property "Footprint" "{footprint}")
    (property "Description" "Test")
    (property "Manufacturer" "")
    (property "Datasheet" "")
    {policy_property}
    (symbol "{name}_0_1")
  )
)\n''',
        encoding="utf-8",
    )


def test_collect_statistics_counts_libraries_symbols_and_policies(tmp_path: Path):
    symbols = tmp_path / "symbols"
    footprints = tmp_path / "footprints"
    symbols.mkdir()
    footprints.mkdir()

    write_symbol(symbols / "Z_Empty.kicad_sym", name=None)
    write_symbol(symbols / "Z_Optional.kicad_sym", name="Optional")
    write_symbol(symbols / "Z_None.kicad_sym", name="None", policy="none")
    write_symbol(symbols / "Z_Required.kicad_sym", name="Required", policy="required", footprint="Z_Required:Device")

    for name in ("Z_Empty", "Z_Optional", "Z_None", "Z_Required"):
        (footprints / f"{name}.pretty").mkdir()
    (footprints / "Z_Required.pretty" / "Device.kicad_mod").write_text(
        '(footprint "Device")\n', encoding="utf-8"
    )

    stats = collect_statistics(symbols, footprints)

    assert stats["symbol_libraries"] == 4
    assert stats["filled_symbol_libraries"] == 3
    assert stats["empty_symbol_libraries"] == 1
    assert stats["symbols"] == 3
    assert stats["footprint_libraries"] == 4
    assert stats["footprints"] == 1
    assert stats["policies"] == Counter({"optional": 1, "none": 1, "required": 1})
    assert stats["assigned_footprints"] == 1
    assert stats["unassigned_footprints"] == 2
    assert stats["errors"] == []


def test_render_quality_report_explains_optional_footprints():
    text = render_quality_report(
        {
            "symbol_libraries": 2,
            "filled_symbol_libraries": 1,
            "empty_symbol_libraries": 1,
            "symbols": 1,
            "footprint_libraries": 2,
            "footprints": 0,
            "policies": Counter({"optional": 1}),
            "assigned_footprints": 0,
            "unassigned_footprints": 1,
            "errors": [],
            "warnings": [],
        }
    )

    assert "✅ keine blockierenden Fehler" in text
    assert "| `optional` | 1 |" in text
    assert "Ein fehlender Footprint ist kein Qualitätsfehler" in text
    assert "vorbereitetes Symbol" in text
