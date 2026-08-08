"""Tests für die read-only Projektkorrelationsansicht von Z_Cockpit."""
from pathlib import Path
from uuid import uuid4

import pytest

from .din_editor_project_context import DinEditorProjectContext
from .din_editor_project_manager import DinEditorProjectManager
from .din_editor_session import DinEditorSession
from .projectos_message_envelope import ProjectOSMessageEnvelope
from .projectos_project_memory import ProjectOSKnowledgeElement, ProjectOSProjectMemory
from .z_cockpit_project_correlation import ZCockpitProjectCorrelationView


def _manager(label: str = "+24V SPS") -> DinEditorProjectManager:
    return DinEditorProjectManager(
        session=DinEditorSession(components=[{
            "reference": "X5",
            "component_type": "DIN_RAIL_TERMINAL_BLOCK",
            "label": label,
            "can_edit_label": True,
        }])
    )


def test_view_groups_messages_by_project_and_correlation():
    manager = _manager()
    context = DinEditorProjectContext.from_manager(manager)
    command = ProjectOSMessageEnvelope.from_project_context(context, message_type="command", name="project.save", payload={"mode": "manual"})
    event = command.child(message_type="event", name="project.saved", payload={"ok": True})
    foreign = _manager("0V SPS")
    foreign_message = ProjectOSMessageEnvelope.from_project_context(DinEditorProjectContext.from_manager(foreign), message_type="event", name="project.saved", payload={})
    state = ZCockpitProjectCorrelationView(manager, [event, foreign_message, command]).state()
    assert state["project"]["project_id"] == manager.project_id
    assert state["message_count"] == 2
    assert len(state["correlations"]) == 1
    assert state["correlations"][0]["correlation_id"] == command.correlation_id
    assert [item["message_id"] for item in state["correlations"][0]["messages"]] == [command.message_id, event.message_id]
    assert state["read_only"] is True


def test_view_can_filter_one_correlation():
    manager = _manager()
    context = DinEditorProjectContext.from_manager(manager)
    first = ProjectOSMessageEnvelope.from_project_context(context, message_type="event", name="first", payload={})
    second = ProjectOSMessageEnvelope.from_project_context(context, message_type="event", name="second", payload={})
    state = ZCockpitProjectCorrelationView(manager, [first, second]).state(first.correlation_id)
    assert state["filter"]["correlation_id"] == first.correlation_id
    assert state["message_count"] == 1
    assert state["correlations"][0]["messages"][0]["message_id"] == first.message_id


def test_view_exposes_project_scoped_legacy_audit_without_claiming_false_correlation():
    manager = _manager()
    manager.sync_log.record("X5", "DIN", "+24V SPS", "kept", project_id=manager.project_id)
    foreign = _manager("0V SPS")
    manager.sync_log.record("X5", "DIN", "0V SPS", "kept", project_id=foreign.project_id)
    state = ZCockpitProjectCorrelationView(manager).state()
    assert state["audit"]["scope"] == "project"
    assert state["audit"]["correlation_linked"] is False
    assert state["audit"]["entry_count"] == 1
    assert state["audit"]["linked_entry_count"] == 0
    assert state["audit"]["unlinked_entry_count"] == 1
    assert state["audit"]["entries"][0]["project_id"] == manager.project_id


def test_view_filters_audit_by_exact_correlation_id():
    manager = _manager()
    wanted = str(uuid4())
    other = str(uuid4())
    manager.sync_log.record("X5", "DIN", "+24V SPS", "kept", project_id=manager.project_id, correlation_id=wanted)
    manager.sync_log.record("X6", "KiCad", "0V SPS", "imported", project_id=manager.project_id, correlation_id=other)
    manager.sync_log.record("X7", "DIN", "PE", "kept", project_id=manager.project_id)
    state = ZCockpitProjectCorrelationView(manager).state(wanted)
    assert state["audit"]["scope"] == "correlation"
    assert state["audit"]["entry_count"] == 1
    assert state["audit"]["entries"][0]["correlation_id"] == wanted
    assert state["audit"]["linked_entry_count"] == 2
    assert state["audit"]["unlinked_entry_count"] == 1


def test_view_resolves_audit_causation_to_concrete_message():
    manager = _manager()
    context = DinEditorProjectContext.from_manager(manager)
    command = ProjectOSMessageEnvelope.from_project_context(context, message_type="command", name="sync.keep_din", payload={"reference": "X5"})
    manager.sync_log.record(
        "X5", "DIN", "+24V SPS", "kept",
        project_id=manager.project_id,
        correlation_id=command.correlation_id,
        causation_id=command.message_id,
    )
    manager.sync_log.record(
        "X6", "DIN", "PE", "kept",
        project_id=manager.project_id,
        correlation_id=command.correlation_id,
        causation_id=str(uuid4()),
    )
    state = ZCockpitProjectCorrelationView(manager, [command]).state(command.correlation_id)
    assert state["audit"]["causation_linked_entry_count"] == 1
    assert state["audit"]["causation_unresolved_entry_count"] == 1
    assert state["audit"]["entries"][0]["causation_id"] == command.message_id


def test_view_shows_memory_for_exact_correlation_and_resolves_message_cause():
    manager = _manager()
    context = DinEditorProjectContext.from_manager(manager)
    command = ProjectOSMessageEnvelope.from_project_context(
        context,
        message_type="command",
        name="sync.keep_din",
        payload={"reference": "X5"},
    )
    memory = ProjectOSProjectMemory(manager.project_id)
    memory.add(ProjectOSKnowledgeElement.from_message(
        command,
        knowledge_type="decision",
        title="DIN-Wert beibehalten",
        content="Der lokale Wert wurde für diesen Vorgang bewusst beibehalten.",
        evidence_status="confirmed",
    ))
    memory.add(ProjectOSKnowledgeElement.from_project_context(
        context,
        knowledge_type="open_question",
        title="Projektweite offene Frage",
        content="Dieses Wissen besitzt absichtlich keine Vorgangskorrelation.",
    ))

    state = ZCockpitProjectCorrelationView(manager, [command], memory).state(command.correlation_id)

    assert state["memory"]["scope"] == "correlation"
    assert state["memory"]["element_count"] == 1
    assert state["memory"]["elements"][0]["correlation_id"] == command.correlation_id
    assert state["memory"]["elements"][0]["causation_id"] == command.message_id
    assert state["memory"]["causation_linked_element_count"] == 1
    assert state["memory"]["causation_unresolved_element_count"] == 0


def test_view_shows_only_relations_between_visible_memory_nodes():
    manager = _manager()
    context = DinEditorProjectContext.from_manager(manager)
    correlation_id = str(uuid4())
    memory = ProjectOSProjectMemory(manager.project_id)
    requirement = memory.add(ProjectOSKnowledgeElement.from_project_context(
        context,
        knowledge_type="requirement",
        title="Anforderung",
        content="Recovery muss explizit bleiben.",
        correlation_id=correlation_id,
    ))
    decision = memory.add(ProjectOSKnowledgeElement.from_project_context(
        context,
        knowledge_type="decision",
        title="Entscheidung",
        content="Recovery wird nur bewusst ausgelöst.",
        correlation_id=correlation_id,
    ))
    project_wide = memory.add(ProjectOSKnowledgeElement.from_project_context(
        context,
        knowledge_type="insight",
        title="Projektweite Erkenntnis",
        content="Ohne Vorgangskorrelation.",
    ))
    memory.relate(requirement, decision, "justifies")
    memory.relate(decision, project_wide, "causes")

    state = ZCockpitProjectCorrelationView(manager, memory=memory).state(correlation_id)

    assert state["memory"]["element_count"] == 2
    assert state["memory"]["relation_count"] == 1
    assert state["memory"]["relations"][0]["relation_type"] == "justifies"
    assert state["memory"]["relations"][0]["source_knowledge_id"] == requirement.knowledge_id
    assert state["memory"]["relations"][0]["target_knowledge_id"] == decision.knowledge_id


def test_view_rejects_memory_from_another_project():
    manager = _manager()
    foreign = _manager("0V SPS")
    memory = ProjectOSProjectMemory(foreign.project_id)

    with pytest.raises(ValueError, match="another project"):
        ZCockpitProjectCorrelationView(manager, memory=memory)


def test_view_exposes_recovery_state_without_loading_recovery(tmp_path: Path):
    manager = _manager()
    path = manager.save(tmp_path / "anlage.json")
    manager.change_service.set_terminal_label(0, "Neue Version")
    manager.save()
    before_session = manager.session
    before_components = [dict(item) for item in manager.session.components]
    state = ZCockpitProjectCorrelationView(manager).state()
    assert state["recovery"]["available"] is True
    assert state["recovery"]["can_recover"] is True
    assert manager.path == path
    assert manager.session is before_session
    assert manager.session.components == before_components


def test_view_is_read_only_for_manager_state():
    manager = _manager()
    before = manager.state()
    state = ZCockpitProjectCorrelationView(manager).state()
    after = manager.state()
    assert state["read_only"] is True
    assert after == before