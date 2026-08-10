from pathlib import Path

from tools.generate_3d_previews import (
    ThreeDPreviewSource,
    check_previews,
    generated_files,
    parse_model_reference,
    preview_source,
    render_svg,
    resolve_model_reference,
    write_previews,
)
from tools.generate_footprint_previews import FootprintRectangle
from tools.validate_device_catalog import REPO_ROOT


SAMPLE_HULL = '''(footprint "Z_Test" (version 20240108)
  (fp_rect
    (start -9 -45)
    (end 9 45)
    (stroke (width 0.1) (type default))
    (fill none)
    (layer "F.Fab")
  )
)'''

SAMPLE_MODEL = '''(footprint "Z_Test" (version 20240108)
  (model "${KICAD_Z_3DMODEL_DIR}/Z_Test.step"
    (offset (xyz 0 0 0))
    (scale (xyz 1 1 1))
    (rotate (xyz 0 0 0))
  )
)'''


def test_parses_and_resolves_repository_model_reference(tmp_path: Path) -> None:
    reference = parse_model_reference(SAMPLE_MODEL)
    assert reference == "${KICAD_Z_3DMODEL_DIR}/Z_Test.step"
    assert resolve_model_reference(reference, tmp_path) == (
        tmp_path / "3dmodels" / "Z_3DModell.3dshapes" / "Z_Test.step"
    )


def test_rejects_external_or_unsafe_model_reference(tmp_path: Path) -> None:
    assert resolve_model_reference("${KICAD8_3DMODEL_DIR}/Package.step", tmp_path) is None
    assert resolve_model_reference("${KICAD_Z_3DMODEL_DIR}/../secret.step", tmp_path) is None
    assert resolve_model_reference(None, tmp_path) is None


def test_hull_preview_is_not_counted_as_real_3d_model() -> None:
    source = ThreeDPreviewSource(
        footprint_name="Z_Test",
        rectangles=(FootprintRectangle(-9, -45, 9, 45, "F.Fab"),),
        model_reference=None,
        model_file=None,
        model_available=False,
    )
    assert source.status == "Hüllkörper"
    assert source.preview_available is True
    svg = render_svg(source)
    assert "Technischer Hüllkörper aus F.Fab" in svg
    assert '<polygon points=' in svg


def test_missing_geometry_gets_explicit_missing_state() -> None:
    source = ThreeDPreviewSource("Z_Empty", (), None, None, False)
    assert source.status == "Fehlt"
    assert source.preview_available is False
    assert "Keine 3D-Geometrie verfügbar" in render_svg(source)


def test_existing_model_reference_is_detected_without_fake_mesh(tmp_path: Path) -> None:
    footprint = tmp_path / "footprints" / "Z_Test.pretty" / "Z_Test.kicad_mod"
    footprint.parent.mkdir(parents=True)
    footprint.write_text(SAMPLE_MODEL, encoding="utf-8")
    model = tmp_path / "3dmodels" / "Z_3DModell.3dshapes" / "Z_Test.step"
    model.parent.mkdir(parents=True)
    model.write_text("ISO-10303-21;", encoding="utf-8")

    source = preview_source(footprint, tmp_path)

    assert source.model_available is True
    assert source.status == "Modell"
    assert source.model_file == model
    assert "KiCad-3D-Modell: Z_Test.step" in render_svg(source)


def test_generated_files_are_deterministic_and_checkable(tmp_path: Path) -> None:
    footprint = tmp_path / "footprints" / "Z_Test.pretty" / "Z_Test.kicad_mod"
    footprint.parent.mkdir(parents=True)
    footprint.write_text(SAMPLE_HULL, encoding="utf-8")
    output = tmp_path / "site" / "3d-previews"

    files = generated_files(tmp_path / "footprints", output, tmp_path)
    assert list(files) == [output / "Z_Test.svg"]
    assert "3D-Vorschau: Z_Test" in files[output / "Z_Test.svg"]
    assert check_previews(files, output) is False
    write_previews(files)
    assert check_previews(files, output) is True
    (output / "unexpected.svg").write_text("<svg/>\n", encoding="utf-8")
    assert check_previews(files, output) is False


def test_repository_3d_previews_match_generator() -> None:
    files = generated_files()
    assert files
    assert check_previews(files) is True
    assert REPO_ROOT / "docs" / "site" / "3d-previews" / "Z_DIN_Module_18mm.svg" in files
