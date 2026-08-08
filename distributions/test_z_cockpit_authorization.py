"""Tests für Z_Cockpit-Rechteherkunft und read-only Rechte-Simulation."""
from datetime import datetime, timezone
from uuid import uuid4

from .projectos_authorization import (
    ProjectOSPermissionAssignment,
    ProjectOSUserProfile,
)
from .z_cockpit_authorization import ZCockpitAuthorizationView


def test_rights_origin_exposes_deny_and_allow_sources_with_labels():
    user = ProjectOSUserProfile("Projektleiter", weight=850, roles=("project_lead",))
    role_allow = ProjectOSPermissionAssignment(
        user_id=user.user_id,
        permission="project.release",
        source_type="role",
        effect="allow",
        source_reference="Rolle Projektleiter",
        risk_class="critical",
    )
    direct_deny = ProjectOSPermissionAssignment(
        user_id=user.user_id,
        permission="project.release",
        source_type="deny",
        effect="deny",
        source_reference="Vier-Augen-Sperre",
        risk_class="critical",
    )

    state = ZCockpitAuthorizationView(user, [role_allow, direct_deny]).state("project.release")

    assert state["decision"] == "deny"
    assert state["decision_label"] == "Verweigert"
    assert state["weight"] == 850
    assert state["weight_used_for_decision"] is False
    assert state["deny_precedence"] is True
    assert {item["source_label"] for item in state["sources"]} == {"Rolle", "DENY"}
    assert [item["source_type"] for item in state["sources"] if item["effective"]] == ["deny"]
    assert "DENY hat Vorrang" in state["explanation"]


def test_delegation_origin_shows_delegator_scope_risk_and_expiry():
    user = ProjectOSUserProfile("Stellvertretung")
    delegator = str(uuid4())
    assignment = ProjectOSPermissionAssignment(
        user_id=user.user_id,
        permission="project.review",
        source_type="delegation",
        effect="allow",
        delegated_by_user_id=delegator,
        source_reference="Vertretung für Projektleitung",
        scope="project:alpha",
        risk_class="high",
        valid_until="2026-08-31T23:59:59+00:00",
    )

    state = ZCockpitAuthorizationView(user, [assignment]).state(
        "project.review",
        scope="project:alpha",
        at=datetime(2026, 8, 9, tzinfo=timezone.utc),
    )

    source = state["sources"][0]
    assert state["allowed"] is True
    assert source["source_label"] == "Delegation"
    assert source["delegated_by_user_id"] == delegator
    assert source["scope"] == "project:alpha"
    assert source["risk_label"] == "Hoch"
    assert source["valid_until"] == "2026-08-31T23:59:59+00:00"


def test_expired_right_is_visible_as_inactive_origin():
    user = ProjectOSUserProfile("Engineering")
    assignment = ProjectOSPermissionAssignment(
        user_id=user.user_id,
        permission="model.edit",
        source_type="direct",
        effect="allow",
        valid_until="2026-08-08T23:59:59+00:00",
    )

    state = ZCockpitAuthorizationView(user, [assignment]).state(
        "model.edit",
        at=datetime(2026, 8, 9, tzinfo=timezone.utc),
    )

    assert state["decision"] == "not_granted"
    assert state["active_source_count"] == 0
    assert state["inactive_source_count"] == 1
    assert state["inactive_sources"][0]["active"] is False
    assert "Gültigkeitszeitraums" in state["explanation"]


def test_simulation_reports_impact_without_changing_baseline():
    user = ProjectOSUserProfile("Entwickler", weight=300)
    allow = ProjectOSPermissionAssignment(
        user_id=user.user_id,
        permission="schematic.edit",
        source_type="role",
        effect="allow",
    )
    simulated_blacklist = ProjectOSPermissionAssignment(
        user_id=user.user_id,
        permission="schematic.edit",
        source_type="blacklist",
        effect="deny",
        source_reference="Testweise Projektsperre",
        risk_class="critical",
    )
    view = ZCockpitAuthorizationView(user, [allow])

    result = view.simulate(
        "schematic.edit",
        hypothetical_assignments=[simulated_blacklist],
    )
    baseline_after = view.state("schematic.edit")

    assert result["baseline"]["decision"] == "allow"
    assert result["simulated"]["decision"] == "deny"
    assert result["decision_changed"] is True
    assert result["impact"]["became_denied"] is True
    assert result["read_only"] is True
    assert baseline_after["decision"] == "allow"


def test_exception_and_whitelist_are_explained_without_hidden_precedence():
    user = ProjectOSUserProfile("Freigabe")
    assignments = [
        ProjectOSPermissionAssignment(
            user_id=user.user_id,
            permission="release.approve",
            source_type="exception",
            effect="allow",
            source_reference="Ausnahmefreigabe",
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

    state = ZCockpitAuthorizationView(user, assignments).state("release.approve")

    assert state["decision"] == "allow"
    assert {item["source_label"] for item in state["sources"] if item["effective"]} == {"Ausnahme", "Whitelist"}
    assert "Wirksame Herkunft" in state["explanation"]
