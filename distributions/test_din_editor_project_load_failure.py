"""Regressionstests für transaktionssicheres Laden von DIN-Projekten."""
import json
from pathlib import Path

from .din_editor_project_bundle import DinProjectBundleError
from .din_editor_project_manager import DinEditorProjectManager
from .din_editor_session import DinEditorSession


def _manager() -> DinEditorProjectManager:
    session = DinEditorSession(components=[
        {
            "reference": "X5",
            "component_type": "DIN_RAIL_TERMINAL_BLOCK",
            "label": "+24V SPS",
            "can_edit_label": True,
        },
        {
            "reference": "X6",
            "component_type": "DIN_RAIL_TERMINAL_BLOCK",
            "label": "0V SPS",
            "can_edit_label": True,
        },
    ])
    return DinEditorProjectManager(session=session)


def _assert_manager_unchanged(
    manager: DinEditorProjectManager,
    *,
    path: Path,
    state: dict,
    saved_state: dict,
    history: dict,
    session: DinEditorSession,
    sync_log,
    change_service,
) -> None:
    assert manager.path == path
    assert manager._snapshot() == state
    assert manager._saved_state == saved_state
    assert manager.history.state() == history
    assert manager.session is session
    assert manager.sync_log is sync_log
    assert manager.change_service is change_service
    assert manager.has_unsaved_changes


def _dirty_manager_with_snapshot(tmp_path: Path):
    manager = _manager()
    original_path = manager.save(tmp_path / "anlage.json")
    manager.change_service.set_terminal_label(0, "Geändert")
    assert manager.has_unsaved_changes
    return manager, {
        "path": original_path,
        "state": manager._snapshot(),
        "saved_state": manager._saved_state.copy(),
        "history": manager.history.state(),
        "session": manager.session,
        "sync_log": manager.sync_log,
        "change_service": manager.change_service,
    }


def test_corrupt_load_preserves_current_manager_state(tmp_path: Path):
    manager, before = _dirty_manager_with_snapshot(tmp_path)

    corrupt_path = tmp_path / "corrupt.json"
    corrupt_path.write_text('{"version": 2, "session":', encoding="utf-8")

    try:
        manager.load(corrupt_path, discard_changes=True)
    except DinProjectBundleError as exc:
        assert "invalid JSON" in str(exc)
        assert str(corrupt_path) in str(exc)
    else:
        raise AssertionError("corrupt project loaded without an error")

    _assert_manager_unchanged(manager, **before)


def test_unsupported_bundle_version_preserves_current_manager_state(tmp_path: Path):
    manager, before = _dirty_manager_with_snapshot(tmp_path)

    incompatible_path = tmp_path / "future-version.json"
    incompatible_path.write_text(
        json.dumps({"version": 999, "session": {"version": 1, "components": []}, "sync_log": []}),
        encoding="utf-8",
    )

    try:
        manager.load(incompatible_path, discard_changes=True)
    except DinProjectBundleError as exc:
        assert "unsupported DIN editor project bundle version" in str(exc)
    else:
        raise AssertionError("unsupported project bundle version loaded without an error")

    _assert_manager_unchanged(manager, **before)
