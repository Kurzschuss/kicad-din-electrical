"""Integration tests for the DIN editor persistence/sync workflow."""
from pathlib import Path

from .din_editor_project_bundle import DinProjectBundleError, save_project_bundle
from .din_editor_project_io import load_project, save_project
from .din_editor_project_manager import DinEditorProjectManager
from .din_editor_session import DinEditorSession
from .din_editor_sync_service import DinEditorSyncService
from .din_editor_sync_view_model import DinEditorSyncViewModel


def _manager() -> DinEditorProjectManager:
    session = DinEditorSession(components=[
        {"reference": "X5", "component_type": "DIN_RAIL_TERMINAL_BLOCK", "label": "+24V SPS", "can_edit_label": True},
        {"reference": "X6", "component_type": "DIN_RAIL_TERMINAL_BLOCK", "label": "0V SPS", "can_edit_label": True},
    ])
    return DinEditorProjectManager(session=session)


def _actions(manager: DinEditorProjectManager):
    view_model = DinEditorSyncViewModel(DinEditorSyncService(manager.change_service))
    return manager.sync_actions(view_model)


def test_project_roundtrip_and_sync_log(tmp_path: Path):
    manager = _manager()
    actions = _actions(manager)
    actions.inspect([{"reference": "X5", "label": "Versorgung 24V"}])
    actions.use_kicad("X5")
    path = manager.save(tmp_path / "anlage.json")

    loaded = DinEditorProjectManager()
    loaded.load(path)
    assert loaded.session.components[0]["label"] == "Versorgung 24V"
    assert loaded.session.components[0]["terminal_label"] == "Versorgung 24V"
    assert len(loaded.sync_log.entries) == 1
    assert loaded.sync_log.entries[0]["reference"] == "X5"
    assert loaded.sync_log.entries[0]["source"] == "KiCad"
    assert loaded.sync_log.entries[0]["action"] == "imported"


def test_sync_action_marks_project_dirty():
    manager = _manager()
    actions = _actions(manager)
    actions.inspect([{"reference": "X5", "label": "Versorgung 24V"}])
    assert not manager.has_unsaved_changes

    actions.use_kicad("X5")
    assert manager.has_unsaved_changes
    assert len(manager.sync_log.entries) == 1


def test_sync_import_is_undoable_and_updates_dirty_state():
    manager = _manager()
    sync_service = DinEditorSyncService(manager.change_service)
    manager.save()

    sync_service.import_labels([{"reference": "X5", "label": "Versorgung 24V"}])
    assert manager.session.components[0]["label"] == "Versorgung 24V"
    assert manager.has_unsaved_changes
    assert manager.history.state()["can_undo"]

    manager.change_service.undo()
    assert manager.session.components[0]["label"] == "+24V SPS"
    assert not manager.has_unsaved_changes

    manager.change_service.redo()
    assert manager.session.components[0]["label"] == "Versorgung 24V"
    assert manager.has_unsaved_changes


def test_resolve_all_is_one_undoable_operation():
    manager = _manager()
    actions = _actions(manager)
    actions.inspect([
        {"reference": "X5", "label": "Versorgung 24V"},
        {"reference": "X6", "label": "0V Versorgung"},
    ])
    manager.save()

    actions.resolve_all("kicad")
    assert manager.session.components[0]["label"] == "Versorgung 24V"
    assert manager.session.components[1]["label"] == "0V Versorgung"
    assert len(manager.sync_log.entries) == 2
    assert manager.has_unsaved_changes

    manager.change_service.undo()
    assert manager.session.components[0]["label"] == "+24V SPS"
    assert manager.session.components[1]["label"] == "0V SPS"
    assert len(manager.sync_log.entries) == 0
    assert not manager.has_unsaved_changes

    manager.change_service.redo()
    assert manager.session.components[0]["label"] == "Versorgung 24V"
    assert manager.session.components[1]["label"] == "0V Versorgung"
    assert len(manager.sync_log.entries) == 2
    assert manager.has_unsaved_changes


def test_invalid_project_is_not_saved(tmp_path: Path):
    manager = _manager()
    manager.session.components[0]["label"] = ""
    path = tmp_path / "invalid.json"

    try:
        manager.save(path)
    except ValueError as exc:
        assert "validation failed" in str(exc)
    else:
        raise AssertionError("invalid project was saved")

    assert not path.exists()


def test_undo_redo_restores_terminal_label_and_savepoint(tmp_path: Path):
    manager = _manager()
    path = manager.save(tmp_path / "anlage.json")
    change_service = manager.change_service

    change_service.set_terminal_label(0, "Versorgung 24V")
    assert manager.has_unsaved_changes
    assert manager.history.state()["can_undo"]

    change_service.undo()
    assert manager.session.components[0]["label"] == "+24V SPS"
    assert not manager.has_unsaved_changes

    change_service.redo()
    assert manager.session.components[0]["label"] == "Versorgung 24V"
    assert manager.has_unsaved_changes

    manager.save(path)
    assert not manager.history.state()["can_undo"]
    change_service = manager.change_service
    change_service.set_terminal_label(0, "Nochmals geändert")
    change_service.undo()
    assert not manager.has_unsaved_changes
    change_service.redo()
    assert manager.has_unsaved_changes


def test_load_requires_explicit_discard_when_dirty(tmp_path: Path):
    manager = _manager()
    path = manager.save(tmp_path / "anlage.json")
    manager.change_service.set_terminal_label(0, "Geändert")

    try:
        manager.load(path)
    except RuntimeError as exc:
        assert "unsaved changes" in str(exc)
    else:
        raise AssertionError("dirty project was loaded without confirmation")

    manager.load(path, discard_changes=True)
    assert manager.session.components[0]["label"] == "+24V SPS"
    assert not manager.has_unsaved_changes


def test_corrupt_project_file_has_clear_load_error(tmp_path: Path):
    path = tmp_path / "corrupt.json"
    path.write_text('{"version": 2, "session":', encoding="utf-8")
    manager = _manager()

    try:
        manager.load(path)
    except DinProjectBundleError as exc:
        assert "invalid JSON" in str(exc)
        assert str(path) in str(exc)
    else:
        raise AssertionError("corrupt project loaded without an error")


def test_invalid_project_bundle_schema_has_clear_error():
    from .din_editor_project_bundle import import_project_bundle

    try:
        import_project_bundle({"version": 2, "session": {}, "sync_log": "broken"})
    except DinProjectBundleError as exc:
        assert "invalid DIN editor project data" in str(exc)
    else:
        raise AssertionError("invalid bundle schema was accepted")


def test_invalid_sync_log_entry_has_clear_error():
    from .din_editor_project_bundle import import_project_bundle

    invalid_entries = [
        {},
        {"timestamp": "2026-07-31T18:00:00+00:00"},
        {"timestamp": "2026-07-31T18:00:00+00:00", "reference": "X5", "source": "KiCad", "value": "24V", "action": 42},
        "not-an-entry",
    ]
    for entry in invalid_entries:
        try:
            import_project_bundle({"version": 2, "session": {"version": 1, "components": []}, "sync_log": [entry]})
        except DinProjectBundleError as exc:
            assert "invalid DIN editor project data" in str(exc)
        else:
            raise AssertionError(f"invalid sync log entry was accepted: {entry!r}")


def test_invalid_sync_log_timestamp_has_clear_error():
    from .din_editor_project_bundle import import_project_bundle

    base = {"reference": "X5", "source": "KiCad", "value": "24V", "action": "imported"}
    invalid_timestamps = [
        "not-a-timestamp",
        "2026-07-31T18:00:00",
        "2026-07-31 18:00:00",
    ]
    for timestamp in invalid_timestamps:
        try:
            import_project_bundle({
                "version": 2,
                "session": {"version": 1, "components": []},
                "sync_log": [{"timestamp": timestamp, **base}],
            })
        except DinProjectBundleError as exc:
            assert "invalid DIN editor project data" in str(exc)
        else:
            raise AssertionError(f"invalid timestamp was accepted: {timestamp!r}")


def test_sync_log_timestamp_accepts_timezone_aware_iso8601():
    from .din_editor_project_bundle import import_project_bundle

    entry = {
        "timestamp": "2026-07-31T18:00:00+00:00",
        "reference": "X5",
        "source": "KiCad",
        "value": "24V",
        "action": "imported",
    }
    _, log = import_project_bundle({
        "version": 2,
        "session": {"version": 1, "components": []},
        "sync_log": [entry],
    })
    assert log.entries == [entry]


def test_failed_replace_preserves_existing_project(monkeypatch, tmp_path: Path):
    path = tmp_path / "anlage.json"
    manager = _manager()
    manager.save(path)
    original = path.read_text(encoding="utf-8")

    def fail_replace(self, target):
        raise OSError("simulated replace failure")

    monkeypatch.setattr(Path, "replace", fail_replace)
    manager.session.components[0]["label"] = "Neue Version"

    try:
        save_project_bundle(manager.session, manager.sync_log, path)
    except DinProjectBundleError as exc:
        assert "cannot be saved" in str(exc)
        assert str(path) in str(exc)
    else:
        raise AssertionError("replace failure was not reported")

    assert path.read_text(encoding="utf-8") == original
    assert not list(tmp_path.glob(f".{path.name}.*.tmp"))


def test_legacy_project_io_preserves_session_only_format(tmp_path: Path):
    manager = _manager()
    path = save_project(manager.session, tmp_path / "legacy.json")
    raw = path.read_text(encoding="utf-8")

    assert '"version": 2' not in raw
    assert '"sync_log"' not in raw

    loaded = load_project(path)
    assert loaded.components == manager.session.components


def test_legacy_project_io_reports_corrupt_json(tmp_path: Path):
    path = tmp_path / "legacy-corrupt.json"
    path.write_text("{not-json", encoding="utf-8")

    try:
        load_project(path)
    except DinProjectBundleError as exc:
        assert "invalid JSON" in str(exc)
        assert str(path) in str(exc)
    else:
        raise AssertionError("corrupt legacy project loaded without an error")


def test_manager_save_failure_preserves_state_and_savepoint(monkeypatch, tmp_path: Path):
    manager = _manager()
    path = manager.save(tmp_path / "anlage.json")
    original_file = path.read_text(encoding="utf-8")
    original_state = manager._snapshot()
    manager.change_service.set_terminal_label(0, "Neue Version")
    assert manager.has_unsaved_changes
    original_history = manager.history.state()

    def fail_replace(self, target):
        raise OSError("simulated manager save failure")

    monkeypatch.setattr(Path, "replace", fail_replace)

    try:
        manager.save(path)
    except DinProjectBundleError as exc:
        assert "cannot be saved" in str(exc)
    else:
        raise AssertionError("manager save failure was not reported")

    assert path.read_text(encoding="utf-8") == original_file
    assert manager._snapshot() != original_state
    assert manager.has_unsaved_changes
    assert manager.history.state() == original_history
    assert manager.path == path


def test_manager_save_as_failure_keeps_previous_path_and_state(monkeypatch, tmp_path: Path):
    manager = _manager()
    original_path = manager.save(tmp_path / "anlage.json")
    manager.change_service.set_terminal_label(0, "Neue Version")
    target = tmp_path / "anlage-neu.json"
    original_state = manager._snapshot()
    original_history = manager.history.state()

    def fail_replace(self, replacement_target):
        raise OSError("simulated save-as failure")

    monkeypatch.setattr(Path, "replace", fail_replace)

    try:
        manager.save(target)
    except DinProjectBundleError as exc:
        assert str(target) in str(exc)
    else:
        raise AssertionError("save-as failure was not reported")

    assert manager.path == original_path
    assert manager._snapshot() == original_state
    assert manager.history.state() == original_history
    assert manager.has_unsaved_changes
    assert original_path.exists()
    assert not target.exists()
    assert not list(tmp_path.glob(f".{target.name}.*.tmp"))


def test_manager_save_as_failure_preserves_existing_target(monkeypatch, tmp_path: Path):
    manager = _manager()
    original_path = manager.save(tmp_path / "anlage.json")
    target = tmp_path / "anlage-neu.json"
    target.write_text("old target content\n", encoding="utf-8")
    original_target = target.read_text(encoding="utf-8")
    manager.change_service.set_terminal_label(0, "Neue Version")
    original_state = manager._snapshot()
    original_history = manager.history.state()

    def fail_replace(self, replacement_target):
        raise OSError("simulated save-as replacement failure")

    monkeypatch.setattr(Path, "replace", fail_replace)

    try:
        manager.save(target)
    except DinProjectBundleError as exc:
        assert str(target) in str(exc)
    else:
        raise AssertionError("save-as failure was not reported")

    assert target.read_text(encoding="utf-8") == original_target
    assert manager.path == original_path
    assert manager._snapshot() == original_state
    assert manager.history.state() == original_history
    assert manager.has_unsaved_changes
    assert not list(tmp_path.glob(f".{target.name}.*.tmp"))
