from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

RCD_2P_FOOTPRINT = ROOT / "footprints" / "Z_RCD.pretty" / "Z_RCD_2P_36mm.kicad_mod"
RCD_4P_FOOTPRINT = ROOT / "footprints" / "Z_RCD.pretty" / "Z_RCD_4P_72mm.kicad_mod"
RCD_2P_TESTBOARD = ROOT / "projects" / "Z_RCD_reference" / "RCD_2P_36mm_testboard.kicad_pcb"
RCD_4P_TESTBOARD = ROOT / "projects" / "Z_RCD_reference" / "RCD_4P_72mm_testboard.kicad_pcb"

EXPECTED_SCALE = "(scale (xyz 0.3940 0.3940 0.3940))"


def test_rcd_2p_footprint_uses_visual_correction_factor() -> None:
    content = RCD_2P_FOOTPRINT.read_text(encoding="utf-8")
    assert EXPECTED_SCALE in content


def test_rcd_4p_footprint_uses_visual_correction_factor() -> None:
    content = RCD_4P_FOOTPRINT.read_text(encoding="utf-8")
    assert EXPECTED_SCALE in content


def test_rcd_2p_testboard_uses_visual_correction_factor() -> None:
    content = RCD_2P_TESTBOARD.read_text(encoding="utf-8")
    assert EXPECTED_SCALE in content


def test_rcd_4p_testboard_uses_visual_correction_factor() -> None:
    content = RCD_4P_TESTBOARD.read_text(encoding="utf-8")
    assert EXPECTED_SCALE in content
