"""Regressionstests für ProjectOS-Benutzergewichtung, Rechteherkunft und Simulation."""
from datetime import datetime, timezone
from uuid import uuid4

import pytest

from .projectos_authorization import (
    ProjectOSAuthorizationEvaluator,
    ProjectOSPermissionAssignment,
    ProjectOSUserProfile,
)


def test_user_weight_is_visible_but_does_not_override_deny():
    user = ProjectOSUserProfile("Projektleiter", weight=900, roles=("project_lead",))
    allow = ProjectOSPermissionAssignment(
        user_id=user.user_id,
        permission="project.save",
        source_type="role",
        effect="allow",
        risk_class="high",
    )
    deny = ProjectOSPermissionAssignment(
        user_id=user.user_id,
        permission="project.save",
        source_type="deny",
        effect="deny",
        risk_class="high",
    )

    result = ProjectOSAuthorizationEvaluator([allow, deny]).evaluate(user, "project.save")

    assert result["decision"] == "deny"
    assert result["allowed"] is False
    assert result["user"]["weight"] == 900
    assert result["weight_used_for_decision"] is False
    assert {item["source_type"] for item in result["active_assignments"]} == {"role", "deny"}


def test_delegation_requires_origin_and_is_exposed_as_permission_source():
    user = ProjectOSUserProfile("Stellvertretung")
    delegator = str(uuid4())
    assignment = ProjectOSPermissionAssignment(
        user_id=user.user_id,
        permission="project.review",
        source_type="delegation",
        effect="allow",
        delegated_by_user_id=delegator,
        source_reference="Vertretung Projektleitung",
    )

    result = ProjectOSAuthorizationEvaluator([assignment]).evaluate(user, "project.review")

    assert result["allowed"] is True
    assert result["effective_sources"][0]["source_type"] == "delegation"
    assert result["effective_sources"][0]["delegated_by_user_id"] == delegator

    with pytest.raises(ValueError, match="delegation requires"):
        ProjectOSPermissionAssignment(
            user_id=user.user_id,
            permission="project.review",
            source_type="delegation",
            effect="allow",
        )


def test_scope_and_validity_are_part_of_effective_rights():
    user = ProjectOSUserProfile("Engineering")
    assignment = ProjectOSPermissionAssignment(
        user_id=user.user_id,
        permission="model.edit",
        source_type="direct",
        effect="allow",
        scope="project:alpha",
        valid_from="2026-08-01T00:00:00+00:00",
        valid_until="2026-08-31T23:59:59+00:00",
        risk_class="medium",
    )
    evaluator = ProjectOSAuthorizationEvaluator([assignment])

    active = evaluator.evaluate(
        user,
        "model.edit",
        scope="project:alpha",
        at=datetime(2026, 8, 9, tzinfo=timezone.utc),
    )
    expired_scope = evaluator.evaluate(
        user,
        "model.edit",
        scope="project:beta",
        at=datetime(2026, 8, 9, tzinfo=timezone.utc),
    )
    expired_time = evaluator.evaluate(
        user,
        "model.edit",
        scope="project:alpha",
        at=datetime(2026, 9, 1, tzinfo=timezone.utc),
    )

    assert active["allowed"] is True
    assert active["effective_sources"][0]["risk_class"] == "medium"
    assert expired_scope["decision"] == "not_granted"
    assert expired_time["decision"] == "not_granted"
    assert len(expired_time["inactive_assignments"]) == 1


def test_simulation_is_read_only_and_reports_effect_of_hypothetical_deny():
    user = ProjectOSUserProfile("Entwickler", weight=250)
    allow = ProjectOSPermissionAssignment(
        user_id=user.user_id,
        permission="schematic.edit",
        source_type="direct",
        effect="allow",
    )
    hypothetical_deny = ProjectOSPermissionAssignment(
        user_id=user.user_id,
        permission="schematic.edit",
        source_type="blacklist",
        effect="deny",
        source_reference="Temporäre Projektsperre",
        risk_class="critical",
    )
    evaluator = ProjectOSAuthorizationEvaluator([allow])

    simulation = evaluator.simulate(
        user,
        "schematic.edit",
        hypothetical_assignments=[hypothetical_deny],
    )
    after = evaluator.evaluate(user, "schematic.edit")

    assert simulation["baseline"]["decision"] == "allow"
    assert simulation["simulated"]["decision"] == "deny"
    assert simulation["decision_changed"] is True
    assert simulation["read_only"] is True
    assert after["decision"] == "allow"
    assert len(after["active_assignments"]) == 1


def test_exception_and_whitelist_are_visible_sources_without_implicit_override_rules():
    user = ProjectOSUserProfile("Sonderfreigabe")
    assignments = [
        ProjectOSPermissionAssignment(
            user_id=user.user_id,
            permission="release.approve",
            source_type="exception",
            effect="allow",
            source_reference="Freigabe AP-42",
            risk_class="critical",
        ),
        ProjectOSPermissionAssignment(
            user_id=user.user_id,
            permission="release.approve",
            source_type="whitelist",
            effect="allow",
            source_reference="Projekt-Whitelist",
            risk_class="critical",
        ),
    ]

    result = ProjectOSAuthorizationEvaluator(assignments).evaluate(user, "release.approve")

    assert result["decision"] == "allow"
    assert {item["source_type"] for item in result["effective_sources"]} == {"exception", "whitelist"}
