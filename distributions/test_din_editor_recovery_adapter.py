"""Tests für den read-only Recovery-Präsentationsadapter."""
import json
from pathlib import Path

from .din_editor_project_bundle import recovery_path_for
from .din_editor_project_manager import DinEditorProjectManager
from .din_editor_recovery_adapter import DinEditorRecoveryAdapter
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


def test_adapter_reports_missing_recovery_in_german(tmp_path: Path):
    manager = _manager()
    path = manager.save(tmp_path / "anlage.json")
    adapter = DinEditorRecoveryAdapter(manager)

    state = adapter.state()

    assert state["code"] == "RECOVERY_NOT_AVAILABLE"
    assert state["title"] == "Keine Wiederherstellung verfügbar"
    assert state["available"] is False
    assert state["valid"] is None
    assert state["can_recover"] is False
    assert state["action_label"] is None
    assert state["path"] == str(recovery_path_for(path))


def test_adapter_reports_valid_recovery_and_offers_explicit_action(tmp_path: Path):
    manager = _manager()
    path = manager.save(tmp_path / "anlage.json")
    manager.change_service.set_terminal_label(0, "Neue Version")
    manager.save()
    adapter = DinEditorRecoveryAdapter(manager)

    state = adapter.state()

    assert state["code"] == "RECOVERY_AVAILABLE"
    assert state["title"] == "Wiederherstellung verfügbar"
    assert state["available"] is True
    assert state["valid"] is True
    assert state["can_recover"] is True
    assert state["action_label"] == "Letzten gültigen Stand wiederherstellen"
    assert state["error"] is None


def test_adapter_reports_invalid_recovery_without_action(tmp_path: Path):
    manager = _manager()
    path = manager.save(tmp_path / "anlage.json")
    recovery = recovery_path_for(path)
    recovery.write_text(
        json.dumps(
            {
                "version": 2,
                "session": {
                    "version": 1,
                    "components": [
                        {
                            "reference": "X5",
                            "component_type": "DIN_RAIL_TERMINAL_BLOCK",
                            "label": "",
                            "can_edit_label": True,
                        }
                    ],
                },
                "sync_log": [],
            }
        ),
        encoding="utf-8",
    )
    adapter = DinEditorRecoveryAdapter(manager)

    state = adapter.state()

    assert state["code"] == "RECOVERY_INVALID"
    assert state["title"] == "Wiederherstellung nicht verwendbar"
    assert state["available"] is True
    assert state["valid"] is False
    assert state["can_recover"] is False
    assert state["action_label"] is None
    assert "Terminal label missing: X5" in state["error"]


def test_adapter_status_is_read_only(tmp_path: Path):
    manager = _manager()
    path = manager.save(tmp_path / "anlage.json")
    manager.change_service.set_terminal_label(0, "Neue Version")
    manager.save()
    manager.change_service.set_terminal_label(0, "Ungespeicherte Änderung")
    before = {
        "path": manager.path,
        "snapshot": manager._snapshot(),
        "saved_state": manager._saved_state.copy(),
        "history": manager.history.state(),
        "session": manager.session,
        "sync_log": manager.sync_log,
        "change_service": manager.change_service,
    }
    adapter = DinEditorRecoveryAdapter(manager)

    state = adapter.state()

    assert state["can_recover"] is True
    assert manager.path == before["path"]
    assert manager._snapshot() == before["snapshot"]
    assert manager._saved_state == before["saved_state"]
    assert manager.history.state() == before["history"]
    assert manager.session is before["session"]
    assert manager.sync_log is before["sync_log"]
    assert manager.change_service is before["change_service"]
    assert manager.has_unsaved_changes


def test_adapter_blocks_recovery_when_status_does_not_allow_it(tmp_path: Path):
    manager = _manager()
    manager.save(tmp_path / "anlage.json")
    adapter = DinEditorRecoveryAdapter(manager)

    try:
        adapter.recover()
    except RuntimeError as exc:
        assert "nicht freigegeben" in str(exc)
    else:
        raise AssertionError("Recovery wurde trotz can_recover=False ausgeführt")


def test_adapter_executes_explicit_recovery_only_when_allowed(tmp_path: Path):
    manager = _manager()
    path = manager.save(tmp_path / "anlage.json")
    manager.change_service.set_terminal_label(0, "Neue Version")
    manager.save()
    adapter = DinEditorRecoveryAdapter(manager)

    adapter.recover()

    assert manager.path == path
    assert manager.session.components[0]["label"] == "+24V SPS"
    assert manager.has_unsaved_changes
    assert manager.state()["recovered_from"] == str(recovery_path_for(path))
