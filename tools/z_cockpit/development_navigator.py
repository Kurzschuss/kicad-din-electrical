from __future__ import annotations

from dataclasses import dataclass

from .project_model import MilestoneState, ProjectState


@dataclass(frozen=True)
class NavigatorRecommendation:
    milestone_id: str
    milestone_title_de: str
    progress_percent: int
    task_id: str
    task_title_de: str
    task_state: str


_STATE_PRIORITY = {"in_progress": 0, "planned": 1}


def recommended_work(state: ProjectState) -> NavigatorRecommendation | None:
    """Ermittelt die nächste tatsächlich ausführbare Arbeit.

    Blockierte Aufgaben werden bewusst nicht empfohlen. Zuerst zählt der
    Arbeitsstatus, danach der weniger weit fortgeschrittene Meilenstein. Bei
    Gleichstand gilt die deklarierte Reihenfolge aus ``project_state.yaml``.
    Dadurch kann das Projektmodell eine bewusst festgelegte Arbeitsreihenfolge
    ausdrücken, ohne sie durch alphabetische Titelreihenfolge zu verlieren.
    """
    candidates: list[tuple[int, int, int, int, MilestoneState, object]] = []
    for milestone_index, milestone in enumerate(state.milestones):
        for task_index, task in enumerate(milestone.tasks):
            if task.state not in _STATE_PRIORITY:
                continue
            candidates.append(
                (
                    _STATE_PRIORITY[task.state],
                    milestone.progress_percent,
                    milestone_index,
                    task_index,
                    milestone,
                    task,
                )
            )
    if not candidates:
        return None
    _, _, _, _, milestone, task = min(candidates)
    return NavigatorRecommendation(
        milestone_id=milestone.milestone_id,
        milestone_title_de=milestone.title_de,
        progress_percent=milestone.progress_percent,
        task_id=task.task_id,
        task_title_de=task.title_de,
        task_state=task.state,
    )


def blocked_tasks(state: ProjectState) -> tuple[str, ...]:
    return tuple(
        task.title_de
        for milestone in state.milestones
        for task in milestone.tasks
        if task.state == "blocked"
    )


def development_navigator_html(state: ProjectState) -> str:
    recommendation = recommended_work(state)
    if recommendation is None:
        recommendation_html = (
            '<p class="navigator-complete">Keine ausführbare Aufgabe offen.</p>'
        )
    else:
        state_label = "In Arbeit" if recommendation.task_state == "in_progress" else "Geplant"
        recommendation_html = (
            '<article class="navigator-recommendation">'
            '<div class="navigator-kicker">Als Nächstes empfohlen</div>'
            f'<h4>{recommendation.milestone_title_de}</h4>'
            f'<p><strong>{recommendation.task_title_de}</strong></p>'
            f'<p>{state_label} · Meilenstein {recommendation.progress_percent} %</p>'
            '</article>'
        )
    blocked = blocked_tasks(state)
    blocked_html = ""
    if blocked:
        items = "".join(f"<li>{title}</li>" for title in blocked)
        blocked_html = f'<div class="navigator-blocked"><h4>Später nach Freigabe</h4><ul>{items}</ul></div>'
    return f'<section class="development-navigator"><h3>Entwicklungsnavigator</h3>{recommendation_html}{blocked_html}</section>'
