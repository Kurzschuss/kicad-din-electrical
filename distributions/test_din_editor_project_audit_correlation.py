"""Tests für Projekt-, Vorgangs- und Kausalitätsschlüssel im Synchronisationsaudit."""
from pathlib import Path
from uuid import UUID, uuid4

import pytest

from .din_editor_project_bundle import load_project_bundle
from .din_editor_project_manager import DinEditorProjectManager
from .din_editor_session import DinEditorSession


def _manager() -> DinEditorProjectManager:
    return DinEditorProjectManager(
        session=DinEditorSession(components=[{
            "reference": "X5",
            "component_type": "DIN_RAIL_TERMINAL_BLOCK",
            "label": "+24V SPS",
            "can_edit_label": True,
        }])
    )


def test_sync_audit_entry_accepts_project_correlation_and_causation_ids():
    manager = _manager()
    correlation_id = str(uuid4())
    causation_id = str(uuid4())
    entry = manager.sync_log.record(
        "X5", "DIN", "+24V SPS", "kept",
        project_id=manager.project_id,
        correlation_id=correlation_id,
        causation_id=causation_id,
    )
    assert entry["project_id"] == manager.project_id
    assert entry["correlation_id"] == correlation_id
    assert entry["causation_id"] == causation_id
    UUID(entry["project_id"]); UUID(entry["correlation_id"]); UUID(entry["causation_id"])


def test_sync_audit_rejects_invalid_causation_id_without_partial_entry():
    manager = _manager()
    with pytest.raises(ValueError, match="causation_id must be a UUID"):
        manager.sync_log.record(
            "X5", "DIN", "+24V SPS", "kept",
            project_id=manager.project_id,
            correlation_id=str(uuid4()),
            causation_id="kein-uuid",
        )
    assert manager.sync_log.entries == []


def test_all_correlation_ids_survive_bundle_save_and_load(tmp_path: Path):
    manager = _manager()
    correlation_id = str(uuid4())
    causation_id = str(uuid4())
    manager.sync_log.record(
        "X5", "DIN", "+24V SPS", "kept",
        project_id=manager.project_id,
        correlation_id=correlation_id,
        causation_id=causation_id,
    )
    path = manager.save(tmp_path / "anlage.json")
    _, restored_log = load_project_bundle(path)
    entry = restored_log.entries[0]
    assert entry["project_id"] == manager.project_id
    assert entry["correlation_id"] == correlation_id
    assert entry["causation_id"] == causation_id


def test_legacy_sync_audit_entry_without_correlation_metadata_remains_supported(tmp_path: Path):
    manager = _manager()
    manager.sync_log.record("X5", "DIN", "+24V SPS", "kept")
    path = manager.save(tmp_path / "anlage.json")
    _, restored_log = load_project_bundle(path)
    entry = restored_log.entries[0]
    assert "project_id" not in entry
    assert "correlation_id" not in entry
    assert "causation_id" not in entry