from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SYMBOLS = ROOT / "symbols" / "Z_MCB.kicad_sym"
FP2 = ROOT / "footprints" / "Z_MCB.pretty" / "Z_MCB_2P_36mm.kicad_mod"
FP4 = ROOT / "footprints" / "Z_MCB.pretty" / "Z_MCB_4P_72mm.kicad_mod"
SCAD2 = ROOT / "models" / "Z_MCB_2P" / "Z_MCB_2P.scad"
SCAD4 = ROOT / "models" / "Z_MCB_4P" / "Z_MCB_4P.scad"
BOARD2 = ROOT / "projects" / "Z_MCB_reference" / "MCB_2P_36mm_testboard.kicad_pcb"
BOARD4 = ROOT / "projects" / "Z_MCB_reference" / "MCB_4P_72mm_testboard.kicad_pcb"
FAMILY_BAT = ROOT / "tools" / "windows" / "export_z_mcb_family_3d.bat"
SCALE = "(scale (xyz 0.3940 0.3940 0.3940))"


def test_mcb_symbols_include_2p_and_4p_with_correct_footprints() -> None:
    text = SYMBOLS.read_text(encoding="utf-8")
    assert '(symbol "MCB_2P"' in text
    assert '(symbol "MCB_4P"' in text
    assert 'Z_MCB:Z_MCB_2P_36mm' in text
    assert 'Z_MCB:Z_MCB_4P_72mm' in text


def test_mcb_2p_footprint_contract() -> None:
    text = FP2.read_text(encoding="utf-8")
    assert '(start -18 -52)' in text and '(end 18 52)' in text
    for pad in ('(at -9 -47)', '(at 9 -47)', '(at -9 47)', '(at 9 47)'):
        assert pad in text
    assert text.count('(size 6 6)') == 4
    assert text.count('(drill 4)') == 4
    assert 'Z_MCB_2P/generated/Z_MCB_2P.wrl' in text
    assert SCALE in text


def test_mcb_4p_footprint_contract() -> None:
    text = FP4.read_text(encoding="utf-8")
    assert '(start -36 -52)' in text and '(end 36 52)' in text
    for x in (-27, -9, 9, 27):
        assert f'(at {x} -47)' in text
        assert f'(at {x} 47)' in text
    assert text.count('(size 6 6)') == 8
    assert text.count('(drill 4)') == 8
    assert 'Z_MCB_4P/generated/Z_MCB_4P.wrl' in text
    assert SCALE in text


def test_mcb_2p_4p_share_parametric_source() -> None:
    assert 'include <../Z_MCB_common/Z_MCB_module.scad>' in SCAD2.read_text(encoding="utf-8")
    assert 'mcb_poles(2);' in SCAD2.read_text(encoding="utf-8")
    assert 'include <../Z_MCB_common/Z_MCB_module.scad>' in SCAD4.read_text(encoding="utf-8")
    assert 'mcb_poles(4);' in SCAD4.read_text(encoding="utf-8")


def test_mcb_testboards_use_confirmed_scale_and_board_sizes() -> None:
    board2 = BOARD2.read_text(encoding="utf-8")
    board4 = BOARD4.read_text(encoding="utf-8")
    assert '(start 82 48)' in board2 and '(end 118 152)' in board2
    assert '(start 64 48)' in board4 and '(end 136 152)' in board4
    assert SCALE in board2
    assert SCALE in board4


def test_mcb_family_export_contains_all_four_variants() -> None:
    text = FAMILY_BAT.read_text(encoding="utf-8")
    for variant in ("MCB-1P", "MCB-2P", "MCB-3P", "MCB-4P"):
        assert variant in text
    assert 'export_z_mcb_2p_3d.py' in text
    assert 'export_z_mcb_4p_3d.py' in text
    assert 'FERTIG - MCB-1P/2P/3P/4P 3D-EXPORT ABGESCHLOSSEN' in text
