"""User-workflow regression for DIN editor issue #6."""
from copy import deepcopy
from pathlib import Path

from .din_editor_project_manager import DinEditorProjectManager
from .din_editor_session import DinEditorSession
from .din_editor_workflow_view_model import DinEditorWorkflowViewModel


def _workflow() -> DinEditorWorkflowViewModel:
    session = DinEditorSession(
        components=[
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
        ]
    )
    return DinEditorWorkflowViewModel(DinEditorProjectManager(session=session))


def test_issue_6_user_workflow_save_sync_reload_and_feedback(tmp_path: Path):
    workflow = _workflow()
    manager = workflow.manager
    original_path = tmp_path / "anlage.json"
    save_as_path = tmp_path / "anlage-kicad.json"

    state = workflow.state()
    assert state["save_as_required"]
    assert not state["actions"]["can_save"]
    assert state["actions"]["can_save_as"]
    assert state["actions"]["can_sync"]
    assert state["error"] is None

    # Edit and a failed plain Save: Save-As remains the explicit recovery action,
    # while the valid in-memory project is preserved.
    state = workflow.set_terminal_label(0, "Versorgung DIN")
    assert state["dirty"]
    assert state["actions"]["can_undo"]

    before_failed_save = deepcopy(manager.session.components)
    state = workflow.save()
    assert state["error"]["operation"] == "save"
    assert state["error"]["type"] == "ValueError"
    assert "project path is not set" in state["error"]["message"]
    assert state["dirty"]
    assert state["save_as_required"]
    assert state["actions"]["can_save_as"]
    assert state["actions"]["can_sync"]
    assert manager.session.components == before_failed_save

    # Save-As establishes the current project path and clears failure feedback.
    state = workflow.save_as(original_path)
    assert state["error"] is None
    assert state["last_operation"] == "save_as"
    assert state["message"] == f"Project saved as: {original_path}"
    assert state["path"] == str(original_path)
    assert not state["dirty"]
    assert not state["save_as_required"]
    assert state["actions"]["can_save"]
    project_id = state["project_id"]

    # A malformed sync request becomes understandable UI feedback without
    # changing session, history, log or the available workflow actions.
    before_components = deepcopy(manager.session.components)
    before_history = deepcopy(manager.history.state())
    before_log = deepcopy(manager.sync_log.entries)
    state = workflow.inspect_sync("broken")  # type: ignore[arg-type]
    assert state["error"]["operation"] == "sync_inspect"
    assert state["error"]["type"] == "ValueError"
    assert "KiCad fields must be a list" in state["error"]["message"]
    assert not state["dirty"]
    assert state["actions"]["can_sync"]
    assert state["actions"]["can_save"]
    assert manager.session.components == before_components
    assert manager.history.state() == before_history
    assert manager.sync_log.entries == before_log

    # A real KiCad conflict is visible and can be explicitly accepted.
    state = workflow.inspect_sync(
        [{"reference": "X5", "label": "Versorgung KiCad"}]
    )
    assert state["error"] is None
    assert state["sync_conflict_count"] == 1
    assert state["conflicts"][0]["reference"] == "X5"
    assert state["actions"]["can_resolve_conflicts"]

    before_failed_resolution = deepcopy(manager.session.components)
    state = workflow.use_kicad("X99")
    assert state["error"]["operation"] == "sync_use_kicad"
    assert state["error"]["type"] == "KeyError"
    assert state["sync_conflict_count"] == 1
    assert state["actions"]["can_resolve_conflicts"]
    assert state["actions"]["can_sync"]
    assert not state["dirty"]
    assert manager.session.components == before_failed_resolution
    assert manager.sync_log.entries == []

    state = workflow.use_kicad("X5")
    assert state["error"] is None
    assert state["last_operation"] == "sync_use_kicad"
    assert state["sync_conflict_count"] == 0
    assert manager.session.components[0]["label"] == "Versorgung KiCad"
    assert manager.session.components[0]["terminal_label"] == "Versorgung KiCad"
    assert state["dirty"]
    assert len(manager.sync_log.entries) == 1
    assert manager.sync_log.entries[0]["reference"] == "X5"
    assert manager.sync_log.entries[0]["source"] == "KiCad"
    assert manager.sync_log.entries[0]["action"] == "imported"

    # Save-As after synchronization preserves the first save and makes the
    # synchronized target current.
    state = workflow.save_as(save_as_path)
    assert state["path"] == str(save_as_path)
    assert not state["dirty"]
    assert state["actions"]["can_save"]

    original = DinEditorProjectManager()
    original.load(original_path)
    assert original.session.components[0]["label"] == "Versorgung DIN"
    assert original.sync_log.entries == []

    # Reload through the workflow rebinds synchronization to the new manager
    # state and starts with fresh history, matching issue #3.
    old_sync_actions = workflow.sync_actions
    state = workflow.open_project(save_as_path)
    assert state["error"] is None
    assert state["project_id"] == project_id
    assert state["path"] == str(save_as_path)
    assert not state["dirty"]
    assert not state["actions"]["can_undo"]
    assert not state["actions"]["can_redo"]
    assert workflow.sync_actions is not old_sync_actions
    assert workflow.sync_actions.inspect([])["conflicts"] == []

    # Undo/redo after reload applies only to new post-reload changes.
    state = workflow.set_terminal_label(0, "Nach Reload")
    assert state["dirty"]
    assert state["actions"]["can_undo"]

    state = workflow.undo()
    assert manager.session.components[0]["label"] == "Versorgung KiCad"
    assert manager.session.components[0]["terminal_label"] == "Versorgung KiCad"
    assert not state["dirty"]
    assert state["actions"]["can_redo"]

    state = workflow.redo()
    assert manager.session.components[0]["label"] == "Nach Reload"
    assert manager.session.components[0]["terminal_label"] == "Nach Reload"
    assert state["dirty"]
    assert state["actions"]["can_undo"]

    # A failed Open while dirty leaves the active project and edit state
    # untouched; Save, Save-As and Sync stay available for recovery.
    before_failed_open = deepcopy(manager.session.components)
    state = workflow.open_project(original_path)
    assert state["error"]["operation"] == "open"
    assert state["error"]["type"] == "RuntimeError"
    assert "unsaved changes" in state["error"]["message"]
    assert state["path"] == str(save_as_path)
    assert state["dirty"]
    assert state["actions"]["can_save"]
    assert state["actions"]["can_save_as"]
    assert state["actions"]["can_sync"]
    assert manager.session.components == before_failed_open
