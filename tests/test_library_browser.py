from pathlib import Path

import pytest

from tools.z_cockpit.library_browser import (
    collect_symbol_libraries,
    parse_library_symbols,
)


def write_library(root: Path, name: str, symbols: list[str]) -> Path:
    path = root / "symbols" / f"{name}.kicad_sym"
    path.parent.mkdir(parents=True, exist_ok=True)
    body = "\n".join(f'  (symbol "{symbol}"\n  )' for symbol in symbols)
    path.write_text(f"(kicad_symbol_lib\n{body}\n)\n", encoding="utf-8")
    return path


def write_mapping(root: Path, content: str) -> None:
    path = root / "metadata" / "footprint_mapping.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_footprint(root: Path, name: str) -> None:
    path = root / "footprints" / f"{name}.pretty" / f"{name}.kicad_mod"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f'(footprint "{name}")', encoding="utf-8")


def write_preview(root: Path, folder: str, *parts: str) -> None:
    path = root / "docs" / "site" / folder / Path(*parts)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("<svg/>", encoding="utf-8")


def test_parse_library_symbols_reads_only_top_level_symbols(tmp_path: Path):
    path = tmp_path / "symbols.kicad_sym"
    path.write_text(
        '(kicad_symbol_lib\n  (symbol "Main"\n    (symbol "Main_0_1")\n  )\n)\n',
        encoding="utf-8",
    )
    assert parse_library_symbols(path) == ("Main",)


def test_parse_library_symbols_rejects_duplicates(tmp_path: Path):
    path = write_library(tmp_path, "Z_Test", ["A", "A"])
    with pytest.raises(ValueError):
        parse_library_symbols(path)


def test_collects_library_symbol_device_footprint_and_preview_status(tmp_path: Path):
    write_library(tmp_path, "Z_Test", ["A", "B"])
    write_mapping(tmp_path, "Symbol,Footprint\nA,Z_DIN_Module_18mm\n")
    write_footprint(tmp_path, "Z_DIN_Module_18mm")
    write_preview(tmp_path, "symbol-previews", "Z_Test", "A.svg")
    write_preview(tmp_path, "footprint-previews", "Z_DIN_Module_18mm.svg")
    devices = [
        {"id": "device.a1", "symbol": "Z_Test:A"},
        {"id": "device.a2", "symbol": "Z_Test:A"},
    ]

    libraries = collect_symbol_libraries(tmp_path, devices)

    assert len(libraries) == 1
    library = libraries[0]
    assert library.name == "Z_Test"
    assert library.symbol_count == 2
    assert library.device_count == 2
    assert library.footprint_count == 1
    assert library.complete_preview_count == 1

    symbol_a = library.symbols[0]
    assert symbol_a.reference == "Z_Test:A"
    assert symbol_a.device_ids == ("device.a1", "device.a2")
    assert symbol_a.device_count == 2
    assert symbol_a.symbol_preview_available is True
    assert symbol_a.footprint_name == "Z_DIN_Module_18mm"
    assert symbol_a.footprint_available is True
    assert symbol_a.footprint_preview_available is True

    symbol_b = library.symbols[1]
    assert symbol_b.device_count == 0
    assert symbol_b.symbol_preview_available is False
    assert symbol_b.footprint_name is None
    assert symbol_b.footprint_available is False
    assert symbol_b.footprint_preview_available is False


def test_collects_libraries_in_stable_name_order(tmp_path: Path):
    write_library(tmp_path, "Z_B", ["B"])
    write_library(tmp_path, "Z_A", ["A"])
    assert [item.name for item in collect_symbol_libraries(tmp_path, [])] == ["Z_A", "Z_B"]
