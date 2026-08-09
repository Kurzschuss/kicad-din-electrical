"""Tests für den transportneutralen ProjectOS-Nachrichtenumschlag."""
from datetime import datetime, timezone
from uuid import UUID

import pytest

from .din_editor_project_context import DinEditorProjectContext
from .din_editor_project_manager import DinEditorProjectManager
from .projectos_message_envelope import ProjectOSMessageEnvelope


def _context() -> DinEditorProjectContext:
    return DinEditorProjectContext.from_manager(DinEditorProjectManager())


def test_envelope_uses_stable_project_context_and_unique_message_identity():
    context = _context()

    envelope = ProjectOSMessageEnvelope.from_project_context(
        context,
        message_type="event",
        name="project.saved",
        payload={"result": "ok"},
    )

    UUID(envelope.message_id)
    UUID(envelope.correlation_id)
    UUID(envelope.project_id)
    assert envelope.project_id == context.project_id
    assert envelope.causation_id is None
    assert envelope.payload == {"result": "ok"}


def test_child_message_keeps_correlation_and_sets_causation():
    parent = ProjectOSMessageEnvelope.from_project_context(
        _context(),
        message_type="command",
        name="project.save",
    )

    child = parent.child(
        message_type="event",
        name="project.saved",
        payload={"success": True},
    )

    assert child.project_id == parent.project_id
    assert child.correlation_id == parent.correlation_id
    assert child.causation_id == parent.message_id
    assert child.message_id != parent.message_id


def test_envelope_normalizes_timestamp_to_utc():
    context = _context()
    envelope = ProjectOSMessageEnvelope.from_project_context(
        context,
        message_type="notification",
        name="project.notice",
        timestamp=datetime(2026, 8, 8, 21, 0, tzinfo=timezone.utc),
    )

    assert envelope.timestamp == "2026-08-08T21:00:00+00:00"


def test_envelope_rejects_invalid_message_type():
    with pytest.raises(ValueError, match="unsupported message_type"):
        ProjectOSMessageEnvelope.from_project_context(
            _context(),
            message_type="unknown",
            name="bad.message",
        )


def test_envelope_rejects_invalid_project_id():
    with pytest.raises(ValueError, match="project_id must be a UUID"):
        ProjectOSMessageEnvelope(
            message_type="event",
            name="project.saved",
            project_id="not-a-uuid",
            payload={},
        )


def test_envelope_dict_is_transport_neutral():
    envelope = ProjectOSMessageEnvelope.from_project_context(
        _context(),
        message_type="request",
        name="project.status.requested",
        payload={"include_recovery": True},
    )

    state = envelope.as_dict()

    assert state["schema_version"] == 1
    assert state["message_type"] == "request"
    assert state["name"] == "project.status.requested"
    assert state["payload"] == {"include_recovery": True}
    assert "broker" not in state
    assert "topic" not in state
    assert "transport" not in state
