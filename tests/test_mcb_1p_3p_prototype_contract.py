from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SYMBOLS = ROOT / "symbols/Z_MCB.kicad_sym"
COMMON = ROOT / "models/Z_MCB_common/Z_MCB_module.scad"
MODEL_1P = ROOT / "models/Z_MCB_1P/Z_MCB_1P.scad"
MODEL_3P = ROOT / "models/Z_MCB_3P/Z_MCB_3P.scad"
EXPORT_3P = ROOT / "tools/export_z_mcb_3p_3d.py"
FAMILY_BAT = ROOT / "tools/windows/export_z_mcb_family_3d.bat"


def test_symbol_library_contains_1p_and_3p_mcb() -> None:
    content = SYMBOLS.read_text(encoding="utf-8")
    assert '(symbol "MCB"' in content
    assert '(symbol "MCB_3P"' in content
    assert 'Z_MCB:Z_MCB_1P_18mm' in content
    assert 'Z_MCB:Z_MCB_3P_54mm' in content
    for pin in ('number "1"', 'number "2"', 'number "3"', 'number "4"', 'number "5"', 'number "6"'):
        assert pin in content


def test_shared_3d_geometry_uses_18mm_grid_and_84mm_length() -> None:
    common = COMMON.read_text(encoding="utf-8")
    one = MODEL_1P.read_text(encoding="utf-8")
    three = MODEL_3P.read_text(encoding="utf-8")

    assert 'mcb_module_width = 18.0;' in common
    assert 'mcb_module_length = 84.0;' in common
    assert 'mcb_poles(1);' in one
    assert 'mcb_poles(3);' in three
    assert 'mcb_module_width' in common


def test_3p_export_checks_54x84_geometry() -> None:
    content = EXPORT_3P.read_text(encoding="utf-8")
    assert 'EXPECTED_WIDTH_MM = 54.0' in content
    assert 'EXPECTED_LENGTH_MM = 84.0' in content
    assert '--check-geometry' in content


def test_windows_family_export_generates_both_variants() -> None:
    content = FAMILY_BAT.read_text(encoding="utf-8")
    assert 'export_z_mcb_3d.py --check-geometry' in content
    assert 'export_z_mcb_3p_3d.py --check-geometry' in content
    assert 'models\\Z_MCB_1P\\generated\\Z_MCB_1P.wrl' in content
    assert 'models\\Z_MCB_3P\\generated\\Z_MCB_3P.wrl' in content
