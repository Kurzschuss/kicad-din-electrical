"""Transportneutraler Navigationsvertrag für read-only Z_Cockpit-Ziele."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import UUID


_ALLOWED_VIEWS = {
    "project_overview",
    "correlation",
    "audit",
    "knowledge_diagnostics",
    "knowledge_element",
    "knowledge_path",
    "knowledge_origin",
    "recovery",
}


def _normalize_optional_uuid(value: str | None, field_name: str) -> str | None:
    if value is None:
        return None
    try:
        return str(UUID(str(value)))
    except (ValueError, AttributeError, TypeError) as exc:
        raise ValueError(f"{field_name} must be a UUID") from exc


def _normalize_uuid_list(values: list[str] | tuple[str, ...] | None, field_name: str) -> tuple[str, ...]:
    result = []
    for value in values or ():
        normalized = _normalize_optional_uuid(value, field_name)
        if normalized is not None and normalized not in result:
            result.append(normalized)
    return tuple(result)


@dataclass(frozen=True)
class ZCockpitNavigationTarget:
    """UI-unabhängiges, validiertes Ziel für Z_Cockpit-Detailnavigation."""

    view: str
    project_id: str
    correlation_id: str | None = None
    knowledge_ids: tuple[str, ...] = field(default_factory=tuple)
    relation_ids: tuple[str, ...] = field(default_factory=tuple)
    message_ids: tuple[str, ...] = field(default_factory=tuple)
    audit_filter: str | None = None
    recovery_path: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        view = str(self.view).strip()
        if view not in _ALLOWED_VIEWS:
            raise ValueError(f"unsupported navigation view: {view}")
        object.__setattr__(self, "view", view)
        object.__setattr__(self, "project_id", _normalize_optional_uuid(self.project_id, "project_id"))
        object.__setattr__(self, "correlation_id", _normalize_optional_uuid(self.correlation_id, "correlation_id"))
        object.__setattr__(self, "knowledge_ids", _normalize_uuid_list(self.knowledge_ids, "knowledge_id"))
        object.__setattr__(self, "relation_ids", _normalize_uuid_list(self.relation_ids, "relation_id"))
        object.__setattr__(self, "message_ids", _normalize_uuid_list(self.message_ids, "message_id"))
        if not isinstance(self.metadata, dict):
            raise ValueError("navigation metadata must be an object")
        object.__setattr__(self, "metadata", dict(self.metadata))
        self._validate_view_contract()

    def _validate_view_contract(self) -> None:
        if self.view == "knowledge_element" and len(self.knowledge_ids) != 1:
            raise ValueError("knowledge_element navigation requires exactly one knowledge_id")
        if self.view == "knowledge_path" and len(self.knowledge_ids) != 2:
            raise ValueError("knowledge_path navigation requires exactly two knowledge_ids")
        if self.view == "knowledge_origin" and len(self.knowledge_ids) != 1:
            raise ValueError("knowledge_origin navigation requires exactly one knowledge_id")
        if self.view == "recovery" and self.recovery_path is not None and not str(self.recovery_path).strip():
            raise ValueError("recovery_path must not be empty")

    def as_dict(self) -> dict[str, Any]:
        return {
            "view": self.view,
            "project_id": self.project_id,
            "correlation_id": self.correlation_id,
            "knowledge_ids": list(self.knowledge_ids),
            "relation_ids": list(self.relation_ids),
            "message_ids": list(self.message_ids),
            "audit_filter": self.audit_filter,
            "recovery_path": self.recovery_path,
            "metadata": dict(self.metadata),
        }
