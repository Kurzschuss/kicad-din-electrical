import json
from pathlib import Path

import pytest

from tools.quality.rule_engine import evaluate, findings_to_json, load_rules, should_fail


RULES = Path("rules/z/symbols/naming.json")
GEOMETRY_RULES = Path("rules/z/symbols/geometry.json")


def test_loads_rules_deterministically():
    rules = load_rules([RULES])
    assert [rule.id for rule in rules] == ["ZSYM-001", "ZSYM-002"]


def test_loads_geometry_rules_deterministically():
    rules = load_rules([GEOMETRY_RULES])
    assert [rule.id for rule in rules] == ["ZSYM-003", "ZSYM-004", "ZSYM-005", "ZSYM-006"]


def test_valid_z_symbol_is_z_conform():
    findings = evaluate(
        load_rules([RULES]),
        {
            "element": "symbols/Z_MCB.kicad_sym – Z_MCB:MCB",
            "library_name": "Z_MCB",
            "footprint_policy_valid": True,
        },
    )
    assert {finding.status for finding in findings} == {"z_conform"}


def test_z_symbol_geometry_is_z_conform():
    findings = evaluate(
        load_rules([GEOMETRY_RULES]),
        {
            "element": "symbols/Z_MCB.kicad_sym – Z_MCB:MCB",
            "connection_grid_mil": 100,
            "pin_length_mil": 100,
            "line_width_mil": 10,
            "text_size_mil": 50,
        },
    )
    assert {finding.status for finding in findings} == {"z_conform"}


def test_geometry_deviation_reports_expected_and_actual():
    findings = evaluate(
        load_rules([GEOMETRY_RULES]),
        {
            "element": "symbols/Z_MCB.kicad_sym – Z_MCB:MCB",
            "connection_grid_mil": 50,
            "pin_length_mil": 150,
            "line_width_mil": 10,
            "text_size_mil": 50,
        },
    )
    assert findings[0].status == "needs_rework"
    assert findings[0].expected == 100
    assert findings[0].actual == 50
    assert findings[1].status == "needs_rework"
    assert findings[1].expected == 100
    assert findings[1].actual == 150


def test_undocumented_deviation_needs_rework():
    findings = evaluate(
        load_rules([RULES]),
        {
            "element": "symbols/MCB.kicad_sym – MCB:MCB",
            "library_name": "MCB",
            "footprint_policy_valid": True,
        },
    )
    assert findings[0].status == "needs_rework"
    assert findings[0].expected == "Z_"
    assert findings[0].actual == "MCB"


def test_exception_remains_visible():
    findings = evaluate(
        load_rules([RULES]),
        {
            "element": "symbols/legacy/MCB.kicad_sym",
            "library_name": "MCB",
            "footprint_policy_valid": True,
        },
        exceptions=[
            {
                "id": "EXC-001",
                "rule_id": "ZSYM-001",
                "element": "symbols/legacy/*",
                "status": "temporarily_accepted",
                "reason": "Migration ist bis zum nächsten Prüftermin dokumentiert.",
            }
        ],
    )
    assert findings[0].status == "temporarily_accepted"
    assert findings[0].exception_id == "EXC-001"


def test_json_contains_required_explanation_fields():
    finding = evaluate(
        load_rules([RULES]),
        {
            "element": "symbols/MCB.kicad_sym",
            "library_name": "MCB",
            "footprint_policy_valid": False,
        },
    )[0]
    payload = json.loads(findings_to_json([finding]))[0]
    assert payload["rule_id"] == "ZSYM-001"
    assert payload["expected"] == "Z_"
    assert payload["actual"] == "MCB"
    assert payload["explanation"]
    assert payload["recommendation"]


def test_profiles_control_ci_effect_without_hiding_results():
    findings = evaluate(
        load_rules([RULES]),
        {
            "element": "symbols/MCB.kicad_sym",
            "library_name": "MCB",
            "footprint_policy_valid": False,
        },
    )
    development = json.loads(Path("rules/profiles/development.json").read_text())
    release = json.loads(Path("rules/profiles/release.json").read_text())
    assert should_fail(findings, development) is False
    assert should_fail(findings, release) is True


def test_rejects_unknown_check_type(tmp_path):
    invalid = tmp_path / "invalid.json"
    invalid.write_text(
        json.dumps(
            {
                "id": "ZSYM-999",
                "title": "Ungültig",
                "scope": "symbol",
                "category": "test",
                "severity": "error",
                "status": "active",
                "version": "1.0",
                "description": "test",
                "recommendation": "test",
                "references": [],
                "check": {"type": "python_eval", "expression": "1 + 1"},
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="Unknown or invalid check type"):
        load_rules([invalid])
