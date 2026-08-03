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


def test_extracts_explicit_z_footprint_policy():
    facts = extract_symbol_facts(MCB)
    assert facts["footprint_policy"] == "optional"
    assert facts["footprint_policy_valid"] is True
    assert facts["footprint_value"] == ""


def test_z_mcb_geometry_is_z_conform():
    facts = extract_symbol_facts(MCB)
    findings = evaluate(load_rules([GEOMETRY_RULES]), facts)
    assert {finding.status for finding in findings} == {"z_conform"}


def test_z_mcb_reference_package_is_z_conform():
    facts = extract_symbol_facts(MCB)
    findings = evaluate(load_rules([NAMING_RULES, GEOMETRY_RULES]), facts)
    assert {finding.status for finding in findings} == {"z_conform"}
    assert {finding.rule_id for finding in findings} == {
        "ZSYM-001",
        "ZSYM-002",
        "ZSYM-003",
        "ZSYM-004",
        "ZSYM-005",
        "ZSYM-006",
    }
