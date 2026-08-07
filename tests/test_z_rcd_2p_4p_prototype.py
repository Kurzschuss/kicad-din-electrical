from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SYMBOL = ROOT / "symbols/Z_RCD.kicad_sym"
FP2 = ROOT / "footprints/Z_RCD.pretty/Z_RCD_2P_36mm.kicad_mod"
FP4 = ROOT / "footprints/Z_RCD.pretty/Z_RCD_4P_72mm.kicad_mod"
COMMON = ROOT / "models/Z_RCD_common/Z_RCD_module.scad"
BAT = ROOT / "tools/windows/export_z_rcd_family_3d.bat"


def test_rcd_symbol_library_contains_2p_and_4p_variants() -> None:
    text = SYMBOL.read_text(encoding="utf-8")
    assert '(symbol "RCD_2P"' in text
    assert '(symbol "RCD_4P"' in text
    assert 'Z_RCD:Z_RCD_2P_36mm' in text
    assert 'Z_RCD:Z_RCD_4P_72mm' in text


def test_rcd_2p_footprint_contract() -> None:
    text = FP2.read_text(encoding="utf-8")
    assert '(start -18 -52)' in text and '(end 18 52)' in text
    for point in ('(at -9 -47)', '(at 9 -47)', '(at -9 47)', '(at 9 47)'):
        assert point in text
    assert text.count('(drill 4)') == 4
    assert text.count('(size 6 6)') == 4
    assert '${Z_PROJECTOS_3DMODEL_DIR}/Z_RCD_2P/generated/Z_RCD_2P.wrl' in text


def test_rcd_4p_footprint_contract() -> None:
    text = FP4.read_text(encoding="utf-8")
    assert '(start -36 -52)' in text and '(end 36 52)' in text
    for x in (-27, -9, 9, 27):
        assert f'(at {x} -47)' in text
        assert f'(at {x} 47)' in text
    assert text.count('(drill 4)') == 8
    assert text.count('(size 6 6)') == 8
    assert '${Z_PROJECTOS_3DMODEL_DIR}/Z_RCD_4P/generated/Z_RCD_4P.wrl' in text


def test_rcd_common_geometry_and_family_export_contract() -> None:
    common = COMMON.read_text(encoding="utf-8")
    bat = BAT.read_text(encoding="utf-8")
    assert 'rcd_module_width = 18.0;' in common
    assert 'rcd_device_length = 84.0;' in common
    assert 'rcd_test_button' in common
    assert 'RCD-2P Geometrie' in bat
    assert 'RCD-4P Geometrie' in bat
    assert 'FERTIG - RCD-2P/4P 3D-EXPORT ABGESCHLOSSEN' in bat
