"""Gemeinsame Bausteine für das Z_Cockpit."""

from .development_navigator import (
    NavigatorRecommendation,
    blocked_tasks,
    development_navigator_html,
    recommended_work,
)
from .footprint_preview import (
    FootprintAssignment,
    footprint_assignment,
    load_footprint_mapping,
)
from .library_browser import (
    LibrarySymbol,
    SymbolLibrary,
    collect_symbol_libraries,
    parse_library_symbols,
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
from .security_page import security_page_html, security_state_label, security_table_html
from .security_status import SecurityItem, collect_security_status
from .symbol_preview import SymbolPreview, parse_symbol_reference, symbol_preview

__all__ = [
    "DEFAULT_PAGES",
    "DashboardTask",
    "FootprintAssignment",
    "LibrarySymbol",
    "NavigatorRecommendation",
    "PageSpec",
    "ProjectState",
    "SecurityItem",
    "StatusItem",
    "SymbolLibrary",
    "SymbolPreview",
    "blocked_tasks",
    "collect_project_status",
    "collect_security_status",
    "collect_symbol_libraries",
    "development_navigator_html",
    "footprint_assignment",
    "load_footprint_mapping",
    "load_project_state",
    "next_dashboard_tasks",
    "next_tasks_html",
    "page_by_id",
    "parse_library_symbols",
    "parse_symbol_reference",
    "progress_bar_html",
    "project_progress_html",
    "recommended_work",
    "security_page_html",
    "security_state_label",
    "security_table_html",
    "symbol_preview",
]
