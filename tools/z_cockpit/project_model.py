from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from tools.validate_device_catalog import REPO_ROOT

PROJECT_STATE_PATH = REPO_ROOT / "project_state.yaml"
ALLOWED_TASK_STATES = {"done", "in_progress", "planned", "blocked"}


@dataclass(frozen=True)
class TaskState:
    task_id: str
    title_de: str
    state: str


@dataclass(frozen=True)
class MilestoneState:
    milestone_id: str
    title_de: str
    tasks: tuple[TaskState, ...]

    @property
    def progress_percent(self) -> int:
        if not self.tasks:
            return 0
        finished = sum(task.state == "done" for task in self.tasks)
        return round(finished * 100 / len(self.tasks))


@dataclass(frozen=True)
class ProjectState:
    name: str
    display_name: str
    language: str
    phase: str
    target_release: str
    milestones: tuple[MilestoneState, ...]

    @property
    def progress_percent(self) -> int:
        tasks = [task for milestone in self.milestones for task in milestone.tasks]
        if not tasks:
            return 0
        finished = sum(task.state == "done" for task in tasks)
        return round(finished * 100 / len(tasks))

    def next_tasks(self) -> tuple[TaskState, ...]:
        """Liefert offene Aufgaben nach Status und deklarierter Projekt-Reihenfolge.

        Die Sortierung ist absichtlich stabil: bei gleichem Status bleibt die
        Reihenfolge aus ``project_state.yaml`` erhalten. Damit kann das zentrale
        Projektmodell eine bewusst festgelegte Arbeitsreihenfolge ausdrücken.
        """
        priority = {"in_progress": 0, "planned": 1, "blocked": 2, "done": 3}
        tasks = [
            task
            for milestone in self.milestones
            for task in milestone.tasks
            if task.state != "done"
        ]
        return tuple(sorted(tasks, key=lambda task: priority[task.state]))


def _required_text(mapping: dict[str, Any], key: str) -> str:
    value = mapping.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Projektmodell: '{key}' muss ein nicht leerer Text sein")
    return value.strip()


def load_project_state(path: Path = PROJECT_STATE_PATH) -> ProjectState:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"Projektmodell fehlt: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"Projektmodell ist ungültig: {exc}") from exc

    if data.get("schema_version") != 1:
        raise ValueError("Projektmodell: nicht unterstützte schema_version")

    project = data.get("project")
    milestones_data = data.get("milestones")
    if not isinstance(project, dict) or not isinstance(milestones_data, list):
        raise ValueError("Projektmodell: project und milestones fehlen oder sind ungültig")

    milestones: list[MilestoneState] = []
    milestone_ids: set[str] = set()
    task_ids: set[str] = set()
    for milestone_data in milestones_data:
        if not isinstance(milestone_data, dict):
            raise ValueError("Projektmodell: Meilenstein muss ein Objekt sein")
        milestone_id = _required_text(milestone_data, "id")
        if milestone_id in milestone_ids:
            raise ValueError(f"Projektmodell: doppelte Meilenstein-ID '{milestone_id}'")
        milestone_ids.add(milestone_id)
        tasks_data = milestone_data.get("tasks")
        if not isinstance(tasks_data, list):
            raise ValueError(f"Projektmodell: tasks für '{milestone_id}' muss eine Liste sein")
        tasks: list[TaskState] = []
        for task_data in tasks_data:
            if not isinstance(task_data, dict):
                raise ValueError("Projektmodell: Aufgabe muss ein Objekt sein")
            task_id = _required_text(task_data, "id")
            if task_id in task_ids:
                raise ValueError(f"Projektmodell: doppelte Aufgaben-ID '{task_id}'")
            task_ids.add(task_id)
            state = _required_text(task_data, "state")
            if state not in ALLOWED_TASK_STATES:
                raise ValueError(f"Projektmodell: ungültiger Aufgabenstatus '{state}'")
            tasks.append(TaskState(task_id, _required_text(task_data, "title_de"), state))
        milestones.append(MilestoneState(milestone_id, _required_text(milestone_data, "title_de"), tuple(tasks)))

    return ProjectState(
        name=_required_text(project, "name"),
        display_name=_required_text(project, "display_name"),
        language=_required_text(project, "language"),
        phase=_required_text(project, "phase"),
        target_release=_required_text(project, "target_release"),
        milestones=tuple(milestones),
    )
