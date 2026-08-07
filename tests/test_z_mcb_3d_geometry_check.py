from pathlib import Path

import pytest

from tools.export_z_mcb_3d import (
    Bounds,
    EXPECTED_MODULE_WIDTH_MM,
    GEOMETRY_TOLERANCE_MM,
    measure_wrl,
    validate_module_width,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
EXPORT_TOOL = REPO_ROOT / "tools/export_z_mcb_3d.py"
SCAD = REPO_ROOT / "models/Z_MCB_1P/Z_MCB_1P.scad"


def test_mcb_source_declares_18mm_module_width() -> None:
    content = SCAD.read_text(encoding="utf-8")
    assert "module_width = 18.0;" in content
    assert EXPECTED_MODULE_WIDTH_MM == 18.0


def test_geometry_check_is_available_without_overwriting_generated_assets() -> None:
    content = EXPORT_TOOL.read_text(encoding="utf-8")
    assert '"--check-geometry"' in content
    assert 'TemporaryDirectory(prefix="projectos-z-mcb-geometry-")' in content
    assert "validate_module_width(step_bounds" in content
    assert "validate_module_width(wrl_bounds" in content


def test_measure_wrl_reads_coordinate_extents(tmp_path: Path) -> None:
    wrl = tmp_path / "sample.wrl"
    wrl.write_text(
        """#VRML V2.0 utf8\n"
        "Shape { geometry IndexedFaceSet { coord Coordinate { point [\n"
        "  -9 0 0,\n"
        "   9 70 90,\n"
        "   0 -18 45\n"
        "] } } }\n""",
        encoding="utf-8",
    )

    bounds = measure_wrl(wrl)

    assert bounds == Bounds(x=18.0, y=88.0, z=90.0)


def test_module_width_validation_accepts_tolerance() -> None:
    validate_module_width(
        Bounds(x=EXPECTED_MODULE_WIDTH_MM + GEOMETRY_TOLERANCE_MM, y=1.0, z=1.0),
        label="TEST",
    )


def test_module_width_validation_rejects_wrong_scale() -> None:
    with pytest.raises(RuntimeError, match="nicht maßhaltig"):
        validate_module_width(Bounds(x=36.0, y=1.0, z=1.0), label="TEST")
