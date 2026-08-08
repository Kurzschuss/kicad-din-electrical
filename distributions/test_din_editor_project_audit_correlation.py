"""Tests für die project_id als Korrelationsschlüssel im Synchronisationsaudit."""
from pathlib import Path
from uuid import UUID

from .din_editor_project_bundle import load_project_bundle
from .din_editor_project_manager import DinEditorProjectManager
from .din_editor_session import DinEditorSession


def _manager() -> DinEditorProjectManager:
    return DinEditorProjectManager(
        session=DinEditorSession(
            components=[
                {
                    "reference": "X5",
                    "component_type": "DIN_RAIL_TERMINAL_BLOCK",
                    "label": "+24V SPS",
                    "can_edit_label": True,
                }
            ]
        )
    )


def test_sync_audit_entry_accepts_and_normalizes_project_id():
    manager = _manager()

    entry = manager.sync_log.record(
        "X5",
        "DIN",
        "+24V SPS",
        "kept",
        project_id=manager.project_id,
    )

    assert entry["project_id"] == manager.project_id
    UUID(entry["project_id"])


def test_project_id_in_sync_audit_survives_bundle_save_and_load(tmp_path: Path):
    manager = _manager()
    manager.sync_log.record(
        "X5",
        "DIN",
        "+24V SPS",
        "kept",
        project_id=manager.project_id,
    )

    path = manager.save(tmp_path / "anlage.json")
    _, restored_log = load_project_bundle(path)

    assert restored_log.entries[0]["project_id"] == manager.project_id


def test_legacy_sync_audit_entry_without_project_id_remains_supported(tmp_path: Path):
    manager = _manager()
    manager.sync_log.record("X5", "DIN", "+24V SPS", "kept")

    path = manager.save(tmp_path / "anlage.json")
    _, restored_log = load_project_bundle(path)

    assert "project_id" not in restored_log.entries[0]
