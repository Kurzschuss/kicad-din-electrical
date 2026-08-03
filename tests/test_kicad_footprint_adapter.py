from pathlib import Path

from tools.quality.kicad_footprint_adapter import extract_footprint_facts
from tools.quality.rule_engine import evaluate, load_rules

ROOT = Path(__file__).resolve().parents[1]
FOOTPRINT = ROOT / "footprints/Z_DIN_Module_18mm.pretty/Z_DIN_Module_18mm.kicad_mod"
RULES = ROOT / "rules/z/footprints/core.json"


def test_extract_real_footprint_facts():
    facts = extract_footprint_facts(FOOTPRINT)
    assert facts["element"] == "Z_DIN_Module_18mm:Z_DIN_Module_18mm"
    assert facts["generator"] == "pcbnew"
    assert facts["format_version"] == 20240108
    assert facts["has_courtyard"] is True
    assert facts["courtyard_closed"] is True
    assert facts["courtyard_width_mm"] == 18.0
    assert facts["courtyard_height_mm"] == 90.0
    assert facts["courtyard_line_width_mm"] == 0.05


def test_real_footprint_is_z_conform():
    findings = evaluate(load_rules([RULES]), extract_footprint_facts(FOOTPRINT))
    statuses = {finding.rule_id: finding.status for finding in findings}
    assert statuses == {
        "ZFP-001": "z_conform",
        "ZFP-002": "z_conform",
        "ZFP-003": "z_conform",
        "ZFP-004": "z_conform",
        "ZFP-005": "z_conform",
        "ZFP-006": "z_conform",
        "ZFP-007": "z_conform",
        "ZFP-008": "z_conform",
    }


def test_file_and_internal_name_mismatch_is_detected(tmp_path):
    footprint = tmp_path / "Z_Test.pretty" / "Z_File.kicad_mod"
    footprint.parent.mkdir()
    footprint.write_text('(footprint "Z_Internal" (version 20240108) (generator pcbnew))\n', encoding="utf-8")
    findings = evaluate(load_rules([RULES]), extract_footprint_facts(footprint))
    mismatch = next(item for item in findings if item.rule_id == "ZFP-003")
    assert mismatch.status == "needs_rework"
    assert mismatch.expected == "Z_File"
    assert mismatch.actual == "Z_Internal"


def test_wrong_courtyard_width_is_detected(tmp_path):
    footprint = tmp_path / "Z_Test.pretty" / "Z_Test.kicad_mod"
    footprint.parent.mkdir()
    footprint.write_text(
        '(footprint "Z_Test" (version 20240108) (generator pcbnew) '
        '(fp_rect (start -10 -45) (end 10 45) '
        '(stroke (width 0.05) (type default)) (fill none) (layer "F.CrtYd")))\n',
        encoding="utf-8",
    )
    findings = evaluate(load_rules([RULES]), extract_footprint_facts(footprint))
    width = next(item for item in findings if item.rule_id == "ZFP-007")
    assert width.status == "needs_rework"
    assert width.expected == 18.0
    assert width.actual == 20.0
