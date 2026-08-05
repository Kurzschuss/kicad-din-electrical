"""Gemeinsame Bausteine für das Z_Cockpit."""

from .pages import DEFAULT_PAGES, PageSpec, page_by_id
from .project_status import StatusItem, collect_project_status

__all__ = [
    "DEFAULT_PAGES",
    "PageSpec",
    "StatusItem",
    "collect_project_status",
    "page_by_id",
]
