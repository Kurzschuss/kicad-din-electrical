import json
from pathlib import Path


MODEL_DIR = Path("models/Z_MCB_1P")
SCAD = MODEL_DIR / "Z_MCB_1P.scad"
MANIFEST = MODEL_DIR / "model.json"


def test_mcb_3d_reference_model_is_project_original_and_neutral() -> None:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))

    assert data["id"] == "Z_MCB_1P"
    assert data["kind"] == "manufacturer_neutral_reference_model"
    assert data["source"]["type"] == "project_original"
    assert data["source"]["traceparts_geometry_imported"] is False
    assert data["source"]["manufacturer_geometry_imported"] is False
    assert data["status"] == "Entwurf"


def test_mcb_3d_reference_dimensions_match_18_mm_module_contract() -> None:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    dimensions = data["dimensions"]

    assert dimensions["module_width"] == 18.0
    assert dimensions["body_height"] == 90.0
    assert dimensions["body_depth"] == 70.0
    assert dimensions["din_rail_nominal_width"] == 35.0


def test_mcb_3d_source_contains_no_manufacturer_branding_or_rating() -> None:
    source = SCAD.read_text(encoding="utf-8")
    lowered = source.casefold()

    assert "siemens" not in lowered
    assert "hager" not in lowered
    assert "abb" not in lowered
    assert "b16" not in lowered
    assert "10 ka" not in lowered
    assert "module_width = 18.0" in source
    assert "rail_width = 35.0" in source
