import json
from pathlib import Path

import pytest

from tools.z_cockpit.project_model import load_project_state


def _write_model(path: Path, *, task_states: list[str]) -> None:
    data = {
        "schema_version": 1,
        "project": {
            "name": "test",
            "display_name": "Testprojekt",
            "language": "de",
            "phase": "Entwicklung",
            "target_release": "1.0",
        },
        "milestones": [
            {
                "id": "basis",
                "title_de": "Basis",
                "tasks": [
                    {"id": f"aufgabe-{index}", "title_de": f"Aufgabe {index}", "state": state}
                    for index, state in enumerate(task_states, start=1)
                ],
            }
        ],
    }
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


def test_repository_project_model_is_valid_and_german() -> None:
    state = load_project_state()
    assert state.name == "kicad-din-electrical"
    assert state.language == "de"
    assert state.target_release == "1.0"
    assert state.milestones
    assert 0 <= state.progress_percent <= 100
    assert all(milestone.title_de for milestone in state.milestones)


def test_progress_is_calculated_from_tasks(tmp_path: Path) -> None:
    path = tmp_path / "project_state.yaml"
    _write_model(path, task_states=["done", "done", "planned", "blocked"])
    state = load_project_state(path)
    assert state.progress_percent == 50
    assert state.milestones[0].progress_percent == 50


def test_next_tasks_prioritize_work_in_progress(tmp_path: Path) -> None:
    path = tmp_path / "project_state.yaml"
    _write_model(path, task_states=["planned", "blocked", "in_progress", "done"])
    state = load_project_state(path)
    assert [task.state for task in state.next_tasks()] == ["in_progress", "planned", "blocked"]


def test_next_tasks_keep_declared_order_with_same_state(tmp_path: Path) -> None:
    path = tmp_path / "project_state.yaml"
    _write_model(path, task_states=["planned", "planned", "planned"])
    state = load_project_state(path)
    assert [task.task_id for task in state.next_tasks()] == [
        "aufgabe-1",
        "aufgabe-2",
        "aufgabe-3",
    ]


def test_invalid_task_state_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "project_state.yaml"
    _write_model(path, task_states=["unbekannt"])
    with pytest.raises(ValueError, match="ungültiger Aufgabenstatus"):
        load_project_state(path)


def test_duplicate_task_ids_are_rejected(tmp_path: Path) -> None:
    path = tmp_path / "project_state.yaml"
    data = {
        "schema_version": 1,
        "project": {
            "name": "test",
            "display_name": "Testprojekt",
            "language": "de",
            "phase": "Entwicklung",
            "target_release": "1.0",
        },
        "milestones": [
            {
                "id": "basis",
                "title_de": "Basis",
                "tasks": [
                    {"id": "doppelt", "title_de": "A", "state": "done"},
                    {"id": "doppelt", "title_de": "B", "state": "planned"},
                ],
            }
        ],
    }
    path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ValueError, match="doppelte Aufgaben-ID"):
        load_project_state(path)
