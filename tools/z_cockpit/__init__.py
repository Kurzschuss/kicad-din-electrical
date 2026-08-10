"""Gemeinsame Bausteine für das Z_Cockpit."""

from .development_navigator import (
    NavigatorRecommendation,
    blocked_tasks,
    development_navigator_html,
    recommended_work,
)
from .diagnostics_page import (
    DiagnosticEntry,
    DiagnosticsSnapshot,
    collect_diagnostics,
    diagnostics_page_html,
)
from .documentation_page import (
    DocumentationEntry,
    collect_documentation,
    documentation_page_html,
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
from .library_health_page import library_health_page_html
from .library_page import library_page_html
from .manufacturer_page import (
    ManufacturerSeriesView,
    ManufacturerView,
    collect_manufacturers,
    manufacturer_page_html,
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
from .quality_engine import (
    LibraryQualityResult,
    QualityIssue,
    evaluate_libraries,
    evaluate_library,
)
from .security_page import security_page_html, security_state_label, security_table_html
from .security_status import SecurityItem, collect_security_status
from .settings_page import CockpitSettingsSnapshot, collect_settings, settings_page_html
from .symbol_preview import SymbolPreview, parse_symbol_reference, symbol_preview
from .user_management_page import (
    UserManagementSnapshot,
    UserPermissionView,
    UserView,
    collect_user_management,
    load_user_management_bundle,
    user_management_page_html,
)

__all__ = [
    "DEFAULT_PAGES",
    "CockpitSettingsSnapshot",
    "DashboardTask",
    "DiagnosticEntry",
    "DiagnosticsSnapshot",
    "DocumentationEntry",
    "FootprintAssignment",
    "LibraryQualityResult",
    "LibrarySymbol",
    "ManufacturerSeriesView",
    "ManufacturerView",
    "NavigatorRecommendation",
    "PageSpec",
    "ProjectState",
    "QualityIssue",
    "SecurityItem",
    "StatusItem",
    "SymbolLibrary",
    "SymbolPreview",
    "UserManagementSnapshot",
    "UserPermissionView",
    "UserView",
    "blocked_tasks",
    "collect_diagnostics",
    "collect_documentation",
    "collect_manufacturers",
    "collect_project_status",
    "collect_security_status",
    "collect_settings",
    "collect_symbol_libraries",
    "collect_user_management",
    "development_navigator_html",
    "diagnostics_page_html",
    "documentation_page_html",
    "evaluate_libraries",
    "evaluate_library",
    "footprint_assignment",
    "library_health_page_html",
    "library_page_html",
    "load_footprint_mapping",
    "load_project_state",
    "load_user_management_bundle",
    "manufacturer_page_html",
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
    "settings_page_html",
    "symbol_preview",
    "user_management_page_html",
]
