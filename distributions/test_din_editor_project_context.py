"""Tests für den read-only Projektkorrelationskontext."""
from pathlib import Path

from .din_editor_project_context import DinEditorProjectContext
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


def test_project_context_exposes_stable_project_identity_without_side_effects(tmp_path: Path):
    manager = _manager()
    path = manager.save(tmp_path / "anlage.json")
    before = manager.state()

    context = DinEditorProjectContext.from_manager(manager)

    assert context.project_id == manager.project_id
    assert context.project_path == str(path)
    assert context.project_identity_migration_pending is False
    assert context.recovered_from is None
    assert manager.state() == before


def test_project_context_identity_survives_save_as_load_and_recovery(tmp_path: Path):
    manager = _manager()
    project_id = manager.project_id
    first_path = manager.save(tmp_path / "anlage.json")
    second_path = manager.save(tmp_path / "anlage-kopie.json")
    assert DinEditorProjectContext.from_manager(manager).project_id == project_id
    assert DinEditorProjectContext.from_manager(manager).project_path == str(second_path)

    loaded = DinEditorProjectManager()
    loaded.load(second_path)
    assert DinEditorProjectContext.from_manager(loaded).project_id == project_id

    manager.change_service.set_terminal_label(0, "Neue Version")
    manager.save(second_path)
    recovered = DinEditorProjectManager()
    recovered.recover(second_path)
    recovery_context = DinEditorProjectContext.from_manager(recovered)
    assert recovery_context.project_id == project_id
    assert recovery_context.recovered_from is not None
    assert first_path != second_path


def test_project_context_builds_transport_neutral_correlation_metadata():
    manager = _manager()
    context = DinEditorProjectContext.from_manager(manager)

    metadata = context.correlation_metadata(
        correlation_id="operation-42",
        causation_id="message-17",
    )

    assert metadata == {
        "project_id": manager.project_id,
        "correlation_id": "operation-42",
        "causation_id": "message-17",
    }


def test_project_context_as_dict_is_ui_and_memory_friendly(tmp_path: Path):
    manager = _manager()
    path = manager.save(tmp_path / "anlage.json")

    state = DinEditorProjectContext.from_manager(manager).as_dict()

    assert state == {
        "project_id": manager.project_id,
        "project_path": str(path),
        "project_identity_migration_pending": False,
        "recovered_from": None,
    }
