from __future__ import annotations

from dataclasses import dataclass
from html import escape

from .project_model import ProjectState, TaskState


TASK_STATE_LABELS = {
    "done": "Erledigt",
    "in_progress": "In Arbeit",
    "planned": "Geplant",
    "blocked": "Blockiert",
}


@dataclass(frozen=True)
class DashboardTask:
    title_de: str
    state: str
    state_label_de: str


def next_dashboard_tasks(project: ProjectState, limit: int = 5) -> tuple[DashboardTask, ...]:
    if limit < 0:
        raise ValueError("Die Aufgabenanzahl darf nicht negativ sein")
    return tuple(
        DashboardTask(task.title_de, task.state, TASK_STATE_LABELS[task.state])
        for task in project.next_tasks()[:limit]
    )


def progress_bar_html(percent: int, label_de: str) -> str:
    if not 0 <= percent <= 100:
        raise ValueError("Fortschritt muss zwischen 0 und 100 liegen")
    label = escape(label_de)
    return (
        f'<div class="progress-row"><div class="progress-label">'
        f'<span>{label}</span><strong>{percent} %</strong></div>'
        f'<div class="progress-track" role="progressbar" aria-label="{label}" '
        f'aria-valuemin="0" aria-valuemax="100" aria-valuenow="{percent}">'
        f'<div class="progress-fill" style="width:{percent}%"></div></div></div>'
    )


def project_progress_html(project: ProjectState) -> str:
    parts = [
        '<section class="project-progress"><h3>Projektfortschritt</h3>',
        progress_bar_html(project.progress_percent, f"Gesamtfortschritt bis Version {project.target_release}"),
        '<div class="milestone-progress">',
    ]
    for milestone in project.milestones:
        parts.append(progress_bar_html(milestone.progress_percent, milestone.title_de))
    parts.append('</div></section>')
    return "".join(parts)


def next_tasks_html(project: ProjectState, limit: int = 5) -> str:
    tasks = next_dashboard_tasks(project, limit)
    if not tasks:
        return '<section class="next-tasks"><h3>Nächste Aufgaben</h3><p>Alle erfassten Aufgaben sind erledigt.</p></section>'
    items = "".join(
        f'<li class="task-{escape(task.state)}"><strong>{escape(task.title_de)}</strong>'
        f'<span>{escape(task.state_label_de)}</span></li>'
        for task in tasks
    )
    return f'<section class="next-tasks"><h3>Nächste Aufgaben</h3><ol>{items}</ol></section>'
