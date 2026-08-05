"""Gemeinsame Bausteine für das Z_Cockpit."""

from .pages import DEFAULT_PAGES, PageSpec, page_by_id
from .project_status import StatusItem, collect_project_status
from .security_status import SecurityItem, collect_security_status

__all__ = [
    "DEFAULT_PAGES",
    "PageSpec",
    "SecurityItem",
    "StatusItem",
    "collect_project_status",
    "collect_security_status",
    "page_by_id",
]
