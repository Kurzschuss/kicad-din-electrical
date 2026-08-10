from pathlib import Path

from tools.z_cockpit.three_d_preview import three_d_preview_assignment


def _write_mapping(root: Path, footprint: str) -> None:
    path = root / "metadata" / "footprint_mapping.csv"
    path.parent.mkdir(parents=True)
    path.write_text(f"Symbol,Footprint\nTest,{footprint}\n", encoding="utf-8")


def _write_footprint(root: Path, name: str, body: str) -> Path:
    path = root / "footprints" / f"{name}.pretty" / f"{name}.kicad_mod"
    path.parent.mkdir(parents=True)
    path.write_text(f'(footprint "{name}" (version 20240108)\n{body}\n)\n', encoding="utf-8")
    return path


def test_unmapped_symbol_has_no_3d_preview(tmp_path: Path) -> None:
    state = three_d_preview_assignment("Z_Test:Test", tmp_path)
    assert state.footprint_name is None
    assert state.model_available is False
    assert state.preview_available is False
    assert state.preview_status == "Nicht zugeordnet"


def test_fab_geometry_becomes_hull_preview_only_when_generated_file_exists(tmp_path: Path) -> None:
    _write_mapping(tmp_path, "Z_Test_FP")
    _write_footprint(
        tmp_path,
        "Z_Test_FP",
        '  (fp_rect (start -9 -45) (end 9 45) (stroke (width 0.1) (type default)) (fill none) (layer "F.Fab"))',
    )
    state_without_file = three_d_preview_assignment("Z_Test:Test", tmp_path)
    assert state_without_file.preview_status == "Hüllkörper"
    assert state_without_file.model_available is False
    assert state_without_file.preview_available is False

    preview = tmp_path / "docs" / "site" / "3d-previews" / "Z_Test_FP.svg"
    preview.parent.mkdir(parents=True)
    preview.write_text("<svg/>\n", encoding="utf-8")
    state = three_d_preview_assignment("Z_Test:Test", tmp_path)
    assert state.preview_available is True
    assert state.preview_relative_url == "3d-previews/Z_Test_FP.svg"
    assert state.preview_status == "Hüllkörper"


def test_real_repository_model_is_reported_separately_from_preview(tmp_path: Path) -> None:
    _write_mapping(tmp_path, "Z_Test_FP")
    _write_footprint(
        tmp_path,
        "Z_Test_FP",
        '  (model "${KICAD_Z_3DMODEL_DIR}/Z_Test.step" (offset (xyz 0 0 0)) (scale (xyz 1 1 1)) (rotate (xyz 0 0 0)))',
    )
    model = tmp_path / "3dmodels" / "Z_3DModell.3dshapes" / "Z_Test.step"
    model.parent.mkdir(parents=True)
    model.write_text("ISO-10303-21;", encoding="utf-8")
    preview = tmp_path / "docs" / "site" / "3d-previews" / "Z_Test_FP.svg"
    preview.parent.mkdir(parents=True)
    preview.write_text("<svg/>\n", encoding="utf-8")

    state = three_d_preview_assignment("Z_Test:Test", tmp_path)

    assert state.model_available is True
    assert state.model_reference == "${KICAD_Z_3DMODEL_DIR}/Z_Test.step"
    assert state.preview_available is True
    assert state.preview_status == "Modell"
