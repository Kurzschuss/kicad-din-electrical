from pathlib import Path

import pytest

from tools.export_z_mcb_3d import (
    Bounds,
    EXPECTED_MODULE_LENGTH_MM,
    EXPECTED_MODULE_WIDTH_MM,
    GEOMETRY_TOLERANCE_MM,
    measure_wrl,
    validate_geometry,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
EXPORT_TOOL = REPO_ROOT / "tools/export_z_mcb_3d.py"
SCAD_1P = REPO_ROOT / "models/Z_MCB_1P/Z_MCB_1P.scad"
SCAD_COMMON = REPO_ROOT / "models/Z_MCB_common/Z_MCB_module.scad"


def test_mcb_source_declares_18x84mm_module_geometry() -> None:
    one_pole = SCAD_1P.read_text(encoding="utf-8")
    common = SCAD_COMMON.read_text(encoding="utf-8")

    assert "include <../Z_MCB_common/Z_MCB_module.scad>" in one_pole
    assert "mcb_module_width = 18.0;" in common
    assert "mcb_module_length = 84.0;" in common
    assert EXPECTED_MODULE_WIDTH_MM == 18.0
    assert EXPECTED_MODULE_LENGTH_MM == 84.0


def test_geometry_check_is_available_without_overwriting_generated_assets() -> None:
    content = EXPORT_TOOL.read_text(encoding="utf-8")
    assert '"--check-geometry"' in content
    assert 'TemporaryDirectory(prefix="projectos-z-mcb-geometry-")' in content
    assert "validate_geometry(step_bounds" in content
    assert "validate_geometry(wrl_bounds" in content


def test_measure_wrl_reads_coordinate_extents(tmp_path: Path) -> None:
    wrl = tmp_path / "sample.wrl"
    wrl.write_text(
        """#VRML V2.0 utf8
Shape { geometry IndexedFaceSet { coord Coordinate { point [
  -9 0 0,
   9 70 90,
   0 -18 45
] } } }
""",
        encoding="utf-8",
    )

    bounds = measure_wrl(wrl)

    assert bounds == Bounds(x=18.0, y=88.0, z=90.0)


def test_geometry_validation_accepts_tolerance() -> None:
    validate_geometry(
        Bounds(
            x=EXPECTED_MODULE_WIDTH_MM + GEOMETRY_TOLERANCE_MM,
            y=EXPECTED_MODULE_LENGTH_MM - GEOMETRY_TOLERANCE_MM,
            z=80.0,
        ),
        label="TEST",
    )


def test_geometry_validation_rejects_wrong_width() -> None:
    with pytest.raises(RuntimeError, match="nicht maßhaltig"):
        validate_geometry(
            Bounds(x=36.0, y=EXPECTED_MODULE_LENGTH_MM, z=80.0),
            label="TEST",
        )


def test_geometry_validation_rejects_wrong_length() -> None:
    with pytest.raises(RuntimeError, match="nicht maßhaltig"):
        validate_geometry(
            Bounds(x=EXPECTED_MODULE_WIDTH_MM, y=104.0, z=80.0),
            label="TEST",
        )
