from pathlib import Path

from tools.validate_libraries import (
    footprint_name,
    footprint_policy,
    symbol_names,
    symbol_properties,
    validate_repository,
)


def write_symbol(
    path: Path,
    *,
    name: str = "Switch",
    footprint: str = "",
    description: str = "Test",
    policy: str | None = None,
) -> None:
    policy_line = f'    (property "Z_Footprint_Policy" "{policy}")\n' if policy is not None else ""
    path.write_text(
        f'''(kicad_symbol_lib (version 20231120)
  (symbol "{name}"
    (property "Reference" "Q")
    (property "Value" "{name}")
    (property "Manufacturer" "")
    (property "Footprint" "{footprint}")
    (property "Datasheet" "")
    (property "Description" "{description}")
{policy_line}    (symbol "{name}_0_1")
  )
)\n''',
        encoding="utf-8",
    )


def prepare_library(tmp_path: Path) -> tuple[Path, Path, Path]:
    symbols = tmp_path / "symbols"
    footprints = tmp_path / "footprints"
    symbols.mkdir()
    pretty = footprints / "Z_Test.pretty"
    pretty.mkdir(parents=True)
    return symbols, footprints, pretty


def test_symbol_parser_reads_top_level_name_and_properties(tmp_path: Path):
    path = tmp_path / "Z_Test.kicad_sym"
    write_symbol(path, footprint="Z_Test:Switch", policy="required")

    assert symbol_names(path) == ["Switch"]
    assert symbol_properties(path)["Footprint"] == "Z_Test:Switch"
    assert symbol_properties(path)["Description"] == "Test"
    assert symbol_properties(path)["Z_Footprint_Policy"] == "required"
    assert footprint_policy(symbol_properties(path)) == "required"


def test_footprint_policy_defaults_to_optional():
    assert footprint_policy({}) == "optional"
    assert footprint_policy({"Z_Footprint_Policy": ""}) == "optional"


def test_footprint_policy_prefers_z_property_and_keeps_legacy_readable():
    assert footprint_policy({"Footprint Policy": "required"}) == "required"
    assert footprint_policy({
        "Footprint Policy": "required",
        "Z_Footprint_Policy": "none",
    }) == "none"


def test_footprint_name_reads_declared_name(tmp_path: Path):
    path = tmp_path / "Switch.kicad_mod"
    path.write_text('(footprint "Switch" (version 20240108))\n', encoding="utf-8")

    assert footprint_name(path) == "Switch"


def test_validator_accepts_existing_qualified_footprint(tmp_path: Path):
    symbols, footprints, pretty = prepare_library(tmp_path)
    write_symbol(symbols / "Z_Test.kicad_sym", footprint="Z_Test:Switch", policy="required")
    (pretty / "Switch.kicad_mod").write_text('(footprint "Switch")\n', encoding="utf-8")

    report = validate_repository(symbols, footprints)

    assert report.errors == []
    assert any(item.code == "SYM102" for item in report.warnings)
    assert any(item.code == "SYM103" for item in report.warnings)


def test_validator_allows_empty_optional_footprint_without_warning(tmp_path: Path):
    symbols, footprints, _ = prepare_library(tmp_path)
    write_symbol(symbols / "Z_Test.kicad_sym", footprint="")

    report = validate_repository(symbols, footprints)

    assert report.errors == []
    assert not any(item.code in {"SYM104", "SYM005"} for item in report.warnings)


def test_validator_allows_none_policy_without_footprint(tmp_path: Path):
    symbols, footprints, _ = prepare_library(tmp_path)
    write_symbol(symbols / "Z_Test.kicad_sym", footprint="", policy="none")

    report = validate_repository(symbols, footprints)

    assert report.errors == []


def test_validator_requires_footprint_for_required_policy(tmp_path: Path):
    symbols, footprints, _ = prepare_library(tmp_path)
    write_symbol(symbols / "Z_Test.kicad_sym", footprint="", policy="required")

    report = validate_repository(symbols, footprints)

    assert [item.code for item in report.errors] == ["SYM005"]


def test_validator_rejects_footprint_when_policy_is_none(tmp_path: Path):
    symbols, footprints, pretty = prepare_library(tmp_path)
    write_symbol(symbols / "Z_Test.kicad_sym", footprint="Z_Test:Switch", policy="none")
    (pretty / "Switch.kicad_mod").write_text('(footprint "Switch")\n', encoding="utf-8")

    report = validate_repository(symbols, footprints)

    assert [item.code for item in report.errors] == ["SYM006"]


def test_validator_rejects_invalid_footprint_policy(tmp_path: Path):
    symbols, footprints, _ = prepare_library(tmp_path)
    write_symbol(symbols / "Z_Test.kicad_sym", policy="always")

    report = validate_repository(symbols, footprints)

    assert [item.code for item in report.errors] == ["SYM004"]


def test_validator_rejects_missing_pretty_and_bad_footprint_reference(tmp_path: Path):
    symbols = tmp_path / "symbols"
    footprints = tmp_path / "footprints"
    symbols.mkdir()
    footprints.mkdir()
    write_symbol(symbols / "Z_Test.kicad_sym", footprint="Z_Missing:Unknown")

    report = validate_repository(symbols, footprints)

    assert {item.code for item in report.errors} == {"SYM001", "SYM003"}


def test_validator_rejects_unqualified_footprint_id(tmp_path: Path):
    symbols, footprints, _ = prepare_library(tmp_path)
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
    symbols, footprints, pretty = prepare_library(tmp_path)
    (symbols / "Z_Test.kicad_sym").write_text("(kicad_symbol_lib)\n", encoding="utf-8")
    (pretty / "Expected.kicad_mod").write_text('(footprint "Other")\n', encoding="utf-8")

    report = validate_repository(symbols, footprints)

    assert [item.code for item in report.errors] == ["FP002"]
