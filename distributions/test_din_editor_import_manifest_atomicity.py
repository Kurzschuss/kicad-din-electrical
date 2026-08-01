"""Failure-path test for atomic manifest synchronization actions."""
from pathlib import Path

from .din_editor_project_manager import DinEditorProjectManager
from .din_editor_session import DinEditorSession
from .din_editor_sync_service import DinEditorSyncService
from .din_editor_sync_view_model import DinEditorSyncViewModel


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


def test_manifest_second_log_failure_rolls_back_all_changes(monkeypatch, tmp_path: Path):
    manager = _manager()
    manager.save(tmp_path / "anlage.json")
    actions = manager.sync_actions(
        DinEditorSyncViewModel(DinEditorSyncService(manager.change_service))
    )
    original_history = manager.history.state()
    original_record = manager.sync_log.record
    calls = 0

    def fail_second_record(*args, **kwargs):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise RuntimeError("simulated second sync-log failure")
        return original_record(*args, **kwargs)

    monkeypatch.setattr(manager.sync_log, "record", fail_second_record)

    manifest = {"symbols": [
        {
            "reference": "X5",
            "label": "Versorgung 24V",
            "user_editable_label": True,
        },
        {
            "reference": "X6",
            "label": "0V Versorgung",
            "user_editable_label": True,
        },
    ]}

    try:
        actions.import_manifest(manifest)
    except RuntimeError as exc:
        assert "second sync-log failure" in str(exc)
    else:
        raise AssertionError("sync-log failure was not reported")

    assert [component["label"] for component in manager.session.components] == [
        "+24V SPS",
        "0V SPS",
    ]
    assert manager.sync_log.entries == []
    assert manager.history.state() == original_history
    assert not manager.has_unsaved_changes
