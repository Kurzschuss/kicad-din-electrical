"""Failure-path integration regressions for issue #5."""
from copy import deepcopy
from pathlib import Path

import pytest

from . import kicad_sch_export
from .din_editor_project_manager import DinEditorProjectManager
from .din_editor_session import DinEditorSession
from .din_editor_sync_service import DinEditorSyncService
from .din_editor_sync_view_model import DinEditorSyncViewModel
from .kicad_sch_export import KiCadSchematicExportError, write_kicad_sch


def _manager() -> DinEditorProjectManager:
    return DinEditorProjectManager(
        session=DinEditorSession(
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
    )


def _actions(manager: DinEditorProjectManager):
    view_model = DinEditorSyncViewModel(DinEditorSyncService(manager.change_service))
    return manager.sync_actions(view_model)


def test_failed_kicad_replace_preserves_existing_export_and_cleans_temp(
    monkeypatch, tmp_path: Path
):
    target = tmp_path / "anlage.kicad_sch"
    target.write_text("previous valid schematic\n", encoding="utf-8")
    previous = target.read_bytes()

    def fail_replace(self, replacement_target):
        raise OSError("simulated KiCad export replace failure")

    monkeypatch.setattr(Path, "replace", fail_replace)

    with pytest.raises(KiCadSchematicExportError, match="cannot be exported safely") as exc:
        write_kicad_sch(target, {"components": [], "terminals": []})

    assert str(target) in str(exc.value)
    assert target.read_bytes() == previous
    assert not list(tmp_path.glob(f".{target.name}.*.tmp"))


def test_failed_kicad_build_preserves_existing_export_without_partial_file(
    monkeypatch, tmp_path: Path
):
    target = tmp_path / "anlage.kicad_sch"
    target.write_text("previous valid schematic\n", encoding="utf-8")
    previous = target.read_bytes()

    def fail_build(plan, connections=None):
        raise ValueError("simulated inconsistent KiCad export state")

    monkeypatch.setattr(kicad_sch_export, "build_kicad_sch", fail_build)

    with pytest.raises(KiCadSchematicExportError, match="cannot be exported safely"):
        write_kicad_sch(target, {"components": [], "terminals": []})

    assert target.read_bytes() == previous
    assert not list(tmp_path.glob(f".{target.name}.*.tmp"))


def test_invalid_manifest_import_is_atomic_at_project_boundary(tmp_path: Path):
    manager = _manager()
    manager.save(tmp_path / "anlage.json")
    actions = _actions(manager)

    session_before = deepcopy(manager.session.state())
    history_before = deepcopy(manager.history.state())
    log_before = deepcopy(manager.sync_log.entries)
    path_before = manager.path

    with pytest.raises(ValueError, match="symbols must be a list"):
        actions.import_manifest({"symbols": {"X5": "broken"}})

    assert manager.session.state() == session_before
    assert manager.history.state() == history_before
    assert manager.sync_log.entries == log_before
    assert manager.path == path_before
    assert not manager.has_unsaved_changes


def test_missing_and_unknown_kicad_references_are_clean_noops(tmp_path: Path):
    manager = _manager()
    manager.save(tmp_path / "anlage.json")
    actions = _actions(manager)

    session_before = deepcopy(manager.session.state())
    history_before = deepcopy(manager.history.state())

    manifest = {
        "symbols": [
            {"reference": "", "label": "missing reference", "user_editable_label": True},
            {"reference": "X99", "label": "unknown reference", "user_editable_label": True},
            {"label": "no reference key", "user_editable_label": True},
        ]
    }
    first = actions.import_manifest(manifest)
    second = actions.import_manifest(manifest)

    assert first == second == manager.session.state()
    assert manager.session.state() == session_before
    assert manager.history.state() == history_before
    assert manager.sync_log.entries == []
    assert not manager.has_unsaved_changes
