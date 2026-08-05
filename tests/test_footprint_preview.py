from pathlib import Path

import pytest

from tools.z_cockpit.footprint_preview import (
    footprint_assignment,
    load_footprint_mapping,
)


def write_mapping(root: Path, content: str) -> None:
    path = root / "metadata" / "footprint_mapping.csv"
    path.parent.mkdir(parents=True)
    path.write_text(content, encoding="utf-8")


def test_loads_central_footprint_mapping(tmp_path: Path):
    write_mapping(tmp_path, "Symbol,Footprint\nMCB,Z_DIN_Module_45mm\n")
    assert load_footprint_mapping(tmp_path) == {"MCB": "Z_DIN_Module_45mm"}


def test_missing_mapping_file_is_empty(tmp_path: Path):
    assert load_footprint_mapping(tmp_path) == {}


def test_rejects_invalid_mapping_header(tmp_path: Path):
    write_mapping(tmp_path, "Symbol,Wrong\nMCB,Z_DIN_Module_45mm\n")
    with pytest.raises(ValueError):
        load_footprint_mapping(tmp_path)


def test_rejects_duplicate_mapping(tmp_path: Path):
    write_mapping(
        tmp_path,
        "Symbol,Footprint\nMCB,Z_DIN_Module_45mm\nMCB,Z_DIN_Module_90mm\n",
    )
    with pytest.raises(ValueError):
        load_footprint_mapping(tmp_path)


def test_assignment_detects_existing_footprint_and_missing_preview(tmp_path: Path):
    write_mapping(tmp_path, "Symbol,Footprint\nMCB,Z_DIN_Module_45mm\n")
    footprint = (
        tmp_path
        / "footprints"
        / "Z_DIN_Module_45mm.pretty"
        / "Z_DIN_Module_45mm.kicad_mod"
    )
    footprint.parent.mkdir(parents=True)
    footprint.write_text("(footprint \"Z_DIN_Module_45mm\")", encoding="utf-8")

    result = footprint_assignment("Z_MCB:MCB", tmp_path)

    assert result.mapped is True
    assert result.footprint_name == "Z_DIN_Module_45mm"
    assert result.footprint_available is True
    assert result.preview_available is False


def test_assignment_marks_unmapped_symbol(tmp_path: Path):
    write_mapping(tmp_path, "Symbol,Footprint\nMCB,Z_DIN_Module_45mm\n")
    result = footprint_assignment("Z_CONTACTOR:Contactor", tmp_path)
    assert result.mapped is False
    assert result.footprint_name is None
    assert result.footprint_available is False
    assert result.preview_available is False
