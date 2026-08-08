"""Tests für den einheitlichen Z_Cockpit-Navigationsvertrag."""
from uuid import uuid4

import pytest

from .z_cockpit_navigation import ZCockpitNavigationTarget


def test_navigation_target_normalizes_ids_and_serializes_transport_neutral():
    project_id = str(uuid4())
    correlation_id = str(uuid4())
    knowledge_id = str(uuid4())
    relation_id = str(uuid4())

    target = ZCockpitNavigationTarget(
        view="knowledge_diagnostics",
        project_id=project_id,
        correlation_id=correlation_id,
        knowledge_ids=(knowledge_id, knowledge_id),
        relation_ids=(relation_id,),
        metadata={"diagnostic_code": "SUPERSESSION_CONFLICT"},
    ).as_dict()

    assert target["view"] == "knowledge_diagnostics"
    assert target["project_id"] == project_id
    assert target["correlation_id"] == correlation_id
    assert target["knowledge_ids"] == [knowledge_id]
    assert target["relation_ids"] == [relation_id]
    assert "route" not in target
    assert "url" not in target


def test_navigation_rejects_unknown_view_and_invalid_uuid():
    with pytest.raises(ValueError, match="unsupported navigation view"):
        ZCockpitNavigationTarget(view="unknown", project_id=str(uuid4()))

    with pytest.raises(ValueError, match="project_id must be a UUID"):
        ZCockpitNavigationTarget(view="audit", project_id="not-a-uuid")


def test_knowledge_element_requires_exactly_one_knowledge_id():
    project_id = str(uuid4())
    with pytest.raises(ValueError, match="exactly one"):
        ZCockpitNavigationTarget(view="knowledge_element", project_id=project_id)

    target = ZCockpitNavigationTarget(
        view="knowledge_element",
        project_id=project_id,
        knowledge_ids=(str(uuid4()),),
    )
    assert len(target.knowledge_ids) == 1


def test_knowledge_path_and_origin_require_knowledge_ids():
    project_id = str(uuid4())
    for view in ("knowledge_path", "knowledge_origin"):
        with pytest.raises(ValueError, match="requires knowledge_ids"):
            ZCockpitNavigationTarget(view=view, project_id=project_id)


def test_audit_and_recovery_targets_keep_specific_filter_context():
    project_id = str(uuid4())
    correlation_id = str(uuid4())

    audit = ZCockpitNavigationTarget(
        view="audit",
        project_id=project_id,
        correlation_id=correlation_id,
        audit_filter="unresolved_causation",
    ).as_dict()
    recovery = ZCockpitNavigationTarget(
        view="recovery",
        project_id=project_id,
        recovery_path="/tmp/project.projectos.recovery",
    ).as_dict()

    assert audit["audit_filter"] == "unresolved_causation"
    assert audit["correlation_id"] == correlation_id
    assert recovery["recovery_path"].endswith(".recovery")
