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
from .issue_report_page import (
    IssueReportSnapshot,
    RepositoryReportState,
    collect_issue_report,
    issue_report_page_html,
    load_repository_report_state,
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
from .permissions_page import (
    PermissionAssignmentView,
    PermissionsSnapshot,
    RepositoryDeveloperWhitelist,
    collect_permissions,
    load_permissions_bundle,
    load_repository_developer_whitelist,
    permissions_page_html,
)
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
    collect_user_management as _collect_user_management,
    load_user_management_bundle as _load_user_management_bundle,
    user_management_page_html as _user_management_page_html,
)

_active_permissions_snapshot: PermissionsSnapshot | None = None


def collect_user_management(state=None, *, source_label=None, at=None):
    """Hält Benutzer- und Berechtigungsansicht auf derselben ProjectOS-Quelle."""
    global _active_permissions_snapshot
    users = _collect_user_management(state, source_label=source_label, at=at)
    _active_permissions_snapshot = collect_permissions(state, source_label=source_label, at=at)
    return users


def load_user_management_bundle(path, *, at=None):
    """Lädt ein Bundle einmal logisch für beide Cockpit-Sichten."""
    global _active_permissions_snapshot
    users = _load_user_management_bundle(path, at=at)
    _active_permissions_snapshot = load_permissions_bundle(path, at=at)
    return users


def user_management_page_html(snapshot: UserManagementSnapshot | None = None) -> str:
    """Rendert Benutzer-, Berechtigungs- und Fehlerbericht-Seite im bestehenden Generatorpfad."""
    permissions = _active_permissions_snapshot
    if permissions is None or (snapshot is not None and permissions.source_label != snapshot.source_label):
        permissions = collect_permissions()
    return (
        _user_management_page_html(snapshot)
        + permissions_page_html(permissions)
        + issue_report_page_html()
    )


__all__ = [
    "DEFAULT_PAGES",
    "CockpitSettingsSnapshot",
    "DashboardTask",
    "DiagnosticEntry",
    "DiagnosticsSnapshot",
    "DocumentationEntry",
    "FootprintAssignment",
    "IssueReportSnapshot",
    "LibraryQualityResult",
    "LibrarySymbol",
    "ManufacturerSeriesView",
    "ManufacturerView",
    "NavigatorRecommendation",
    "PageSpec",
    "PermissionAssignmentView",
    "PermissionsSnapshot",
    "ProjectState",
    "QualityIssue",
    "RepositoryDeveloperWhitelist",
    "RepositoryReportState",
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
    "collect_issue_report",
    "collect_manufacturers",
    "collect_permissions",
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
    "issue_report_page_html",
    "library_health_page_html",
    "library_page_html",
    "load_footprint_mapping",
    "load_permissions_bundle",
    "load_project_state",
    "load_repository_developer_whitelist",
    "load_repository_report_state",
    "load_user_management_bundle",
    "manufacturer_page_html",
    "next_dashboard_tasks",
    "next_tasks_html",
    "page_by_id",
    "parse_library_symbols",
    "parse_symbol_reference",
    "permissions_page_html",
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
