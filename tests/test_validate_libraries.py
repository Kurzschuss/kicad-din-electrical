from pathlib import Path

from tools.validate_libraries import (
    footprint_name,
    symbol_names,
    symbol_properties,
    validate_repository,
)


def write_symbol(path: Path, *, name: str = "Switch", footprint: str = "", description: str = "Test") -> None:
    path.write_text(
        f'''(kicad_symbol_lib (version 20231120)
  (symbol "{name}"
    (property "Reference" "Q")
    (property "Value" "{name}")
    (property "Manufacturer" "")
    (property "Footprint" "{footprint}")
    (property "Datasheet" "")
    (property "Description" "{description}")
    (symbol "{name}_0_1")
  )
)\n''',
        encoding="utf-8",
    )


def test_symbol_parser_reads_top_level_name_and_properties(tmp_path: Path):
    path = tmp_path / "Z_Test.kicad_sym"
    write_symbol(path, footprint="Z_Test:Switch")

    assert symbol_names(path) == ["Switch"]
    assert symbol_properties(path)["Footprint"] == "Z_Test:Switch"
    assert symbol_properties(path)["Description"] == "Test"


def test_footprint_name_reads_declared_name(tmp_path: Path):
    path = tmp_path / "Switch.kicad_mod"
    path.write_text('(footprint "Switch" (version 20240108))\n', encoding="utf-8")

    assert footprint_name(path) == "Switch"


def test_validator_accepts_existing_qualified_footprint(tmp_path: Path):
    symbols = tmp_path / "symbols"
    footprints = tmp_path / "footprints"
    symbols.mkdir()
    pretty = footprints / "Z_Test.pretty"
    pretty.mkdir(parents=True)
    write_symbol(symbols / "Z_Test.kicad_sym", footprint="Z_Test:Switch")
    (pretty / "Switch.kicad_mod").write_text('(footprint "Switch")\n', encoding="utf-8")

    report = validate_repository(symbols, footprints)

    assert report.errors == []
    assert any(item.code == "SYM102" for item in report.warnings)
    assert any(item.code == "SYM103" for item in report.warnings)


def test_validator_rejects_missing_pretty_and_bad_footprint_reference(tmp_path: Path):
    symbols = tmp_path / "symbols"
    footprints = tmp_path / "footprints"
    symbols.mkdir()
    footprints.mkdir()
    write_symbol(symbols / "Z_Test.kicad_sym", footprint="Z_Missing:Unknown")

    report = validate_repository(symbols, footprints)

    assert {item.code for item in report.errors} == {"SYM001", "SYM003"}


def test_validator_rejects_unqualified_footprint_id(tmp_path: Path):
    symbols = tmp_path / "symbols"
    footprints = tmp_path / "footprints"
    symbols.mkdir()
    (footprints / "Z_Test.pretty").mkdir(parents=True)
    write_symbol(symbols / "Z_Test.kicad_sym", footprint="Switch")

    report = validate_repository(symbols, footprints)

    assert [item.code for item in report.errors] == ["SYM002"]


def test_validator_reports_empty_symbol_library_as_warning(tmp_path: Path):
    symbols = tmp_path / "symbols"
    footprints = tmp_path / "footprints"
    symbols.mkdir()
    (footprints / "Z_Empty.pretty").mkdir(parents=True)
    (symbols / "Z_Empty.kicad_sym").write_text("(kicad_symbol_lib)\n", encoding="utf-8")

    report = validate_repository(symbols, footprints)

    assert report.errors == []
    assert [item.code for item in report.warnings] == ["SYM100"]


def test_validator_rejects_footprint_name_mismatch(tmp_path: Path):
    symbols = tmp_path / "symbols"
    footprints = tmp_path / "footprints"
    symbols.mkdir()
    pretty = footprints / "Z_Test.pretty"
    pretty.mkdir(parents=True)
    (symbols / "Z_Test.kicad_sym").write_text("(kicad_symbol_lib)\n", encoding="utf-8")
    (pretty / "Expected.kicad_mod").write_text('(footprint "Other")\n', encoding="utf-8")

    report = validate_repository(symbols, footprints)

    assert [item.code for item in report.errors] == ["FP002"]
