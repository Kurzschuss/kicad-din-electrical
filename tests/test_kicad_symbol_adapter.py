from pathlib import Path

from tools.quality.kicad_symbol_adapter import extract_symbol_facts
from tools.quality.rule_engine import evaluate, load_rules


MCB = Path("symbols/Z_MCB.kicad_sym")
NAMING_RULES = Path("rules/z/symbols/naming.json")
GEOMETRY_RULES = Path("rules/z/symbols/geometry.json")


def test_extracts_z_mcb_reference_geometry():
    facts = extract_symbol_facts(MCB)
    assert facts["library_name"] == "Z_MCB"
    assert facts["connection_grid_mil"] == 100
    assert facts["pin_length_mil"] == 100
    assert facts["line_width_mil"] == 10
    assert facts["text_size_mil"] == 50


def test_z_mcb_geometry_is_z_conform():
    facts = extract_symbol_facts(MCB)
    findings = evaluate(load_rules([GEOMETRY_RULES]), facts)
    assert {finding.status for finding in findings} == {"z_conform"}


def test_z_mcb_missing_footprint_policy_remains_visible():
    facts = extract_symbol_facts(MCB)
    findings = evaluate(load_rules([NAMING_RULES]), facts)
    status_by_rule = {finding.rule_id: finding.status for finding in findings}
    assert status_by_rule["ZSYM-001"] == "z_conform"
    assert status_by_rule["ZSYM-002"] == "needs_rework"
