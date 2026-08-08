"""Regressionstests für transaktionssicheres Laden und Recovery von DIN-Projekten."""
import json
from pathlib import Path

from .din_editor_project_bundle import DinProjectBundleError, recovery_path_for
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


def test_invalid_project_data_preserves_current_manager_state(tmp_path: Path):
    manager, before = _dirty_manager_with_snapshot(tmp_path)

    invalid_path = tmp_path / "invalid-project-data.json"
    invalid_path.write_text(
        json.dumps(
            {
                "version": 2,
                "session": {"version": 1, "components": "not-a-list"},
                "sync_log": [],
            }
        ),
        encoding="utf-8",
    )

    try:
        manager.load(invalid_path, discard_changes=True)
    except DinProjectBundleError as exc:
        assert "invalid DIN editor project data" in str(exc)
    else:
        raise AssertionError("invalid project data loaded without an error")

    _assert_manager_unchanged(manager, **before)


def test_successful_overwrite_preserves_previous_valid_project_for_recovery(tmp_path: Path):
    manager = _manager()
    path = manager.save(tmp_path / "anlage.json")
    assert not recovery_path_for(path).exists()

    manager.change_service.set_terminal_label(0, "Neue Version")
    manager.save()

    recovery = recovery_path_for(path)
    assert recovery.exists()

    recovered = DinEditorProjectManager()
    recovered.recover(path)
    assert recovered.path == path
    assert recovered.session.components[0]["label"] == "+24V SPS"
    assert recovered.has_unsaved_changes
    assert recovered.state()["recovered_from"] == str(recovery)


def test_recovery_restores_last_valid_state_after_main_file_corruption(tmp_path: Path):
    manager = _manager()
    path = manager.save(tmp_path / "anlage.json")
    manager.change_service.set_terminal_label(0, "Zweite Version")
    manager.save()

    recovery = recovery_path_for(path)
    expected_recovery = recovery.read_text(encoding="utf-8")
    path.write_text('{"version": 2, "session":', encoding="utf-8")

    restored = DinEditorProjectManager()
    restored.recover(path)
    assert restored.session.components[0]["label"] == "+24V SPS"
    assert restored.path == path
    assert restored.has_unsaved_changes

    restored.save()
    assert not restored.has_unsaved_changes
    assert restored.state()["recovered_from"] is None
    assert recovery.read_text(encoding="utf-8") == expected_recovery

    verified = DinEditorProjectManager()
    verified.load(path)
    assert verified.session.components[0]["label"] == "+24V SPS"


def test_missing_recovery_does_not_change_current_manager_state(tmp_path: Path):
    manager, before = _dirty_manager_with_snapshot(tmp_path)
    missing_target = tmp_path / "ohne-recovery.json"

    try:
        manager.recover(missing_target, discard_changes=True)
    except DinProjectBundleError as exc:
        assert "recovery cannot be loaded" in str(exc)
    else:
        raise AssertionError("missing recovery was accepted")

    _assert_manager_unchanged(manager, **before)


def test_semantically_invalid_recovery_does_not_change_current_manager_state(tmp_path: Path):
    manager, before = _dirty_manager_with_snapshot(tmp_path)
    target = tmp_path / "semantic-recovery.json"
    recovery = recovery_path_for(target)
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

    try:
        manager.recover(target, discard_changes=True)
    except DinProjectBundleError as exc:
        assert "recovery validation failed" in str(exc)
        assert "Terminal label missing: X5" in str(exc)
    else:
        raise AssertionError("semantically invalid recovery was accepted")

    _assert_manager_unchanged(manager, **before)


def test_semantically_invalid_main_file_does_not_replace_valid_recovery(tmp_path: Path):
    manager = _manager()
    path = manager.save(tmp_path / "anlage.json")
    manager.change_service.set_terminal_label(0, "Zweite Version")
    manager.save()

    recovery = recovery_path_for(path)
    expected_recovery = recovery.read_text(encoding="utf-8")

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

    manager.change_service.set_terminal_label(0, "Dritte Version")
    manager.save()

    assert recovery.read_text(encoding="utf-8") == expected_recovery

    restored = DinEditorProjectManager()
    restored.recover(path)
    assert restored.session.components[0]["label"] == "+24V SPS"


def test_recovery_status_reports_missing_recovery_without_side_effects(tmp_path: Path):
    manager, before = _dirty_manager_with_snapshot(tmp_path)

    status = manager.recovery_status()

    assert status == {
        "path": str(recovery_path_for(before["path"])),
        "available": False,
        "valid": None,
        "can_recover": False,
        "error": None,
    }
    _assert_manager_unchanged(manager, **before)


def test_recovery_status_reports_valid_recovery_without_loading_it(tmp_path: Path):
    manager = _manager()
    path = manager.save(tmp_path / "anlage.json")
    manager.change_service.set_terminal_label(0, "Neue Version")
    manager.save()
    manager.change_service.set_terminal_label(0, "Aktiver Entwurf")
    before = {
        "path": path,
        "state": manager._snapshot(),
        "saved_state": manager._saved_state.copy(),
        "history": manager.history.state(),
        "session": manager.session,
        "sync_log": manager.sync_log,
        "change_service": manager.change_service,
    }

    status = manager.recovery_status()

    assert status["path"] == str(recovery_path_for(path))
    assert status["available"] is True
    assert status["valid"] is True
    assert status["can_recover"] is True
    assert status["error"] is None
    assert manager.session.components[0]["label"] == "Aktiver Entwurf"
    _assert_manager_unchanged(manager, **before)


def test_recovery_status_reports_invalid_recovery_without_loading_it(tmp_path: Path):
    manager, before = _dirty_manager_with_snapshot(tmp_path)
    recovery = recovery_path_for(before["path"])
    recovery.write_text('{"version": 2, "session":', encoding="utf-8")

    status = manager.recovery_status()

    assert status["path"] == str(recovery)
    assert status["available"] is True
    assert status["valid"] is False
    assert status["can_recover"] is False
    assert "invalid JSON" in status["error"]
    _assert_manager_unchanged(manager, **before)


def test_project_state_exposes_recovery_status(tmp_path: Path):
    manager = _manager()
    path = manager.save(tmp_path / "anlage.json")
    manager.change_service.set_terminal_label(0, "Neue Version")
    manager.save()

    state = manager.state()

    assert state["recovery"] == {
        "path": str(recovery_path_for(path)),
        "available": True,
        "valid": True,
        "can_recover": True,
        "error": None,
    }


def test_new_project_state_reports_no_recovery_target():
    manager = _manager()

    assert manager.recovery_status() == {
        "path": None,
        "available": False,
        "valid": None,
        "can_recover": False,
        "error": None,
    }
    assert manager.state()["recovery"] == manager.recovery_status()
