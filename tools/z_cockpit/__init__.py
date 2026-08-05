"""Gemeinsame Bausteine für das Z_Cockpit."""

from .development_navigator import (
    NavigatorRecommendation,
    blocked_tasks,
    development_navigator_html,
    recommended_work,
)
from .pages import DEFAULT_PAGES, PageSpec, page_by_id
from .project_dashboard import (
    DashboardTask,
    next_dashboard_tasks,
    next_tasks_html,
    progress_bar_html,
    project_progress_html,
)
from .project_model import ProjectState, load_project_state
from .project_status import StatusItem, collect_project_status
from .security_status import SecurityItem, collect_security_status

__all__ = [
    "DEFAULT_PAGES",
    "DashboardTask",
    "NavigatorRecommendation",
    "PageSpec",
    "ProjectState",
    "SecurityItem",
    "StatusItem",
    "blocked_tasks",
    "collect_project_status",
    "collect_security_status",
    "development_navigator_html",
    "load_project_state",
    "next_dashboard_tasks",
    "next_tasks_html",
    "page_by_id",
    "progress_bar_html",
    "project_progress_html",
    "recommended_work",
]
