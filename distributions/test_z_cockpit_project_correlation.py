"""Tests für die read-only Projektkorrelationsansicht von Z_Cockpit."""
from pathlib import Path
from uuid import uuid4

from .din_editor_project_context import DinEditorProjectContext
from .din_editor_project_manager import DinEditorProjectManager
from .din_editor_session import DinEditorSession
from .projectos_message_envelope import ProjectOSMessageEnvelope
from .z_cockpit_project_correlation import ZCockpitProjectCorrelationView


def _manager(label: str = "+24V SPS") -> DinEditorProjectManager:
    return DinEditorProjectManager(
        session=DinEditorSession(
            components=[
                {
                    "reference": "X5",
                    "component_type": "DIN_RAIL_TERMINAL_BLOCK",
                    "label": label,
                    "can_edit_label": True,
                }
            ]
        )
    )


def test_view_groups_messages_by_project_and_correlation():
    manager = _manager()
    context = DinEditorProjectContext.from_manager(manager)
    command = ProjectOSMessageEnvelope.from_project_context(
        context,
        message_type="command",
        name="project.save",
        payload={"mode": "manual"},
    )
    event = command.child(
        message_type="event",
        name="project.saved",
        payload={"ok": True},
    )

    foreign = _manager("0V SPS")
    foreign_message = ProjectOSMessageEnvelope.from_project_context(
        DinEditorProjectContext.from_manager(foreign),
        message_type="event",
        name="project.saved",
        payload={},
    )

    state = ZCockpitProjectCorrelationView(
        manager,
        [event, foreign_message, command],
    ).state()

    assert state["project"]["project_id"] == manager.project_id
    assert state["message_count"] == 2
    assert len(state["correlations"]) == 1
    assert state["correlations"][0]["correlation_id"] == command.correlation_id
    assert [item["message_id"] for item in state["correlations"][0]["messages"]] == [
        command.message_id,
        event.message_id,
    ]
    assert state["read_only"] is True


def test_view_can_filter_one_correlation():
    manager = _manager()
    context = DinEditorProjectContext.from_manager(manager)
    first = ProjectOSMessageEnvelope.from_project_context(
        context, message_type="event", name="first", payload={}
    )
    second = ProjectOSMessageEnvelope.from_project_context(
        context, message_type="event", name="second", payload={}
    )

    state = ZCockpitProjectCorrelationView(manager, [first, second]).state(first.correlation_id)

    assert state["filter"]["correlation_id"] == first.correlation_id
    assert state["message_count"] == 1
    assert state["correlations"][0]["messages"][0]["message_id"] == first.message_id


def test_view_exposes_project_scoped_legacy_audit_without_claiming_false_correlation():
    manager = _manager()
    manager.sync_log.record(
        "X5",
        "DIN",
        "+24V SPS",
        "kept",
        project_id=manager.project_id,
    )
    foreign = _manager("0V SPS")
    manager.sync_log.record(
        "X5",
        "DIN",
        "0V SPS",
        "kept",
        project_id=foreign.project_id,
    )

    state = ZCockpitProjectCorrelationView(manager).state()

    assert state["audit"]["scope"] == "project"
    assert state["audit"]["correlation_linked"] is False
    assert state["audit"]["entry_count"] == 1
    assert state["audit"]["linked_entry_count"] == 0
    assert state["audit"]["unlinked_entry_count"] == 1
    assert state["audit"]["entries"][0]["project_id"] == manager.project_id
    assert "correlation_id" in state["audit"]["note"]


def test_view_filters_audit_by_exact_correlation_id():
    manager = _manager()
    wanted = str(uuid4())
    other = str(uuid4())
    manager.sync_log.record(
        "X5", "DIN", "+24V SPS", "kept",
        project_id=manager.project_id,
        correlation_id=wanted,
    )
    manager.sync_log.record(
        "X6", "KiCad", "0V SPS", "imported",
        project_id=manager.project_id,
        correlation_id=other,
    )
    manager.sync_log.record(
        "X7", "DIN", "PE", "kept",
        project_id=manager.project_id,
    )

    state = ZCockpitProjectCorrelationView(manager).state(wanted)

    assert state["audit"]["scope"] == "correlation"
    assert state["audit"]["correlation_linked"] is True
    assert state["audit"]["entry_count"] == 1
    assert state["audit"]["entries"][0]["correlation_id"] == wanted
    assert state["audit"]["linked_entry_count"] == 2
    assert state["audit"]["unlinked_entry_count"] == 1


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