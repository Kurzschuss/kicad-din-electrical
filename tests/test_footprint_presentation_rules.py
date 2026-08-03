from pathlib import Path

from tools.quality.kicad_footprint_adapter import extract_footprint_facts
from tools.quality.rule_engine import evaluate, load_rules

ROOT = Path(__file__).resolve().parents[1]
FOOTPRINT = ROOT / "footprints/Z_DIN_Module_18mm.pretty/Z_DIN_Module_18mm.kicad_mod"
RULES = (
    ROOT / "rules/z/footprints/core.json",
    ROOT / "rules/z/footprints/presentation.json",
)


def test_reference_footprint_has_standard_texts_and_fab_outline():
    facts = extract_footprint_facts(FOOTPRINT)
    assert facts["has_reference"] is True
    assert facts["has_value"] is True
    assert facts["has_fab_outline"] is True


def test_reference_footprint_passes_all_zfp_rules():
    findings = evaluate(load_rules(RULES), extract_footprint_facts(FOOTPRINT))
    assert len(findings) == 11
    assert all(finding.status == "z_conform" for finding in findings)


def test_missing_standard_elements_are_release_findings(tmp_path):
    footprint = tmp_path / "Z_Test.pretty" / "Z_Test.kicad_mod"
    footprint.parent.mkdir()
    footprint.write_text(
        '(footprint "Z_Test" (version 20240108) (generator pcbnew) '
        '(fp_rect (start -9 -45) (end 9 45) '
        '(stroke (width 0.05) (type default)) (fill none) (layer "F.CrtYd")))\n',
        encoding="utf-8",
    )
    findings = evaluate(load_rules(RULES), extract_footprint_facts(footprint))
    statuses = {finding.rule_id: finding.status for finding in findings}
    assert statuses["ZFP-009"] == "needs_rework"
    assert statuses["ZFP-010"] == "needs_rework"
    assert statuses["ZFP-011"] == "needs_rework"
