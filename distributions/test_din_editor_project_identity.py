"""Tests für stabile Projektidentität und Migration alter Bundle-Dateien."""
import json
from pathlib import Path
from uuid import UUID

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


def test_new_project_has_stable_uuid_and_bundle_v3(tmp_path: Path):
    manager = _manager()
    project_id = manager.project_id
    UUID(project_id)

    path = manager.save(tmp_path / "anlage.json")
    data = json.loads(path.read_text(encoding="utf-8"))

    assert data["version"] == 3
    assert data["project_id"] == project_id
    assert manager.state()["project_id"] == project_id
    assert manager.state()["project_identity_migration_pending"] is False


def test_project_id_survives_save_load_and_recovery(tmp_path: Path):
    manager = _manager()
    project_id = manager.project_id
    path = manager.save(tmp_path / "anlage.json")

    manager.change_service.set_terminal_label(0, "Neue Version")
    manager.save()

    loaded = DinEditorProjectManager()
    loaded.load(path)
    assert loaded.project_id == project_id
    assert loaded.has_unsaved_changes is False

    recovered = DinEditorProjectManager()
    recovered.recover(path)
    assert recovered.project_id == project_id
    assert recovered.has_unsaved_changes is True


def test_save_as_preserves_project_identity(tmp_path: Path):
    manager = _manager()
    project_id = manager.project_id
    first_path = manager.save(tmp_path / "anlage.json")
    second_path = manager.save(tmp_path / "anlage-kopie.json")

    assert first_path != second_path
    assert manager.project_id == project_id
    assert json.loads(second_path.read_text(encoding="utf-8"))["project_id"] == project_id


def test_legacy_v2_load_generates_identity_without_rewriting_file(tmp_path: Path):
    path = tmp_path / "legacy.json"
    legacy = {
        "version": 2,
        "session": {
            "version": 1,
            "rails": 18,
            "te_per_rail": 12,
            "components": [
                {
                    "reference": "X5",
                    "component_type": "DIN_RAIL_TERMINAL_BLOCK",
                    "label": "+24V SPS",
                    "can_edit_label": True,
                }
            ],
        },
        "sync_log": [],
    }
    original = json.dumps(legacy, indent=2) + "\n"
    path.write_text(original, encoding="utf-8")

    manager = DinEditorProjectManager()
    manager.load(path)

    UUID(manager.project_id)
    assert manager.project_identity_migration_pending is True
    assert manager.has_unsaved_changes is True
    assert path.read_text(encoding="utf-8") == original


def test_legacy_v2_identity_becomes_persistent_after_explicit_save(tmp_path: Path):
    path = tmp_path / "legacy.json"
    path.write_text(
        json.dumps(
            {
                "version": 2,
                "session": {
                    "version": 1,
                    "components": [
                        {
                            "reference": "X5",
                            "component_type": "DIN_RAIL_TERMINAL_BLOCK",
                            "label": "+24V SPS",
                            "can_edit_label": True,
                        }
                    ],
                },
                "sync_log": [],
            }
        ),
        encoding="utf-8",
    )

    manager = DinEditorProjectManager()
    manager.load(path)
    generated_id = manager.project_id

    manager.save()
    migrated = json.loads(path.read_text(encoding="utf-8"))

    assert migrated["version"] == 3
    assert migrated["project_id"] == generated_id
    assert manager.project_identity_migration_pending is False
    assert manager.has_unsaved_changes is False

    reloaded = DinEditorProjectManager()
    reloaded.load(path)
    assert reloaded.project_id == generated_id
    assert reloaded.project_identity_migration_pending is False
    assert reloaded.has_unsaved_changes is False


def test_new_project_creates_new_project_identity():
    manager = _manager()
    first_id = manager.project_id

    manager.new_project(discard_changes=True)

    assert manager.project_id != first_id
    UUID(manager.project_id)
    assert manager.project_identity_migration_pending is False