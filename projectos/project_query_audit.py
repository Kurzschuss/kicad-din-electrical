"""Persistente Auditierung sicherheitsrelevanter ProjectOS-Query-Zugriffe."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import NAMESPACE_URL, uuid5

from .application import Query
from .audit import AuditEntry
from .authorization import AuthorizationContext
from .identifiers import BusinessId, ObjectId
from .project_queries import (
    QUERY_COMMAND_DIAGNOSTIC,
    QUERY_COMMAND_LIFECYCLE,
    QUERY_COMMAND_SEARCH,
)
from .project_query_authorization import (
    AuthorizedProjectQueryPipeline,
    AuthorizedProjectQueryResult,
    PERM_PROJECT_COMMAND_DIAGNOSTIC_READ,
    PERM_PROJECT_COMMAND_LIFECYCLE_READ,
    PERM_PROJECT_COMMAND_SEARCH,
)
from .results import Result
from .sqlite_audit import SQLiteAuditRepository

PERM_PROJECT_QUERY_UNMAPPED = BusinessId("PERM-PROJECT-QUERY-UNMAPPED")

_QUERY_PERMISSIONS = {
    QUERY_COMMAND_LIFECYCLE: PERM_PROJECT_COMMAND_LIFECYCLE_READ,
    QUERY_COMMAND_SEARCH: PERM_PROJECT_COMMAND_SEARCH,
    QUERY_COMMAND_DIAGNOSTIC: PERM_PROJECT_COMMAND_DIAGNOSTIC_READ,
}


@dataclass(frozen=True, slots=True)
class AuditedProjectQueryResult:
    """Ergebnis einer Query einschließlich persistentem Audit-Nachweis."""

    execution: AuthorizedProjectQueryResult
    audit_entry: AuditEntry


class AuditedProjectQueryPipeline:
    """Auditiert erfolgreiche und abgelehnte sicherheitsrelevante Lesezugriffe."""

    def __init__(
        self,
        pipeline: AuthorizedProjectQueryPipeline,
        audit: SQLiteAuditRepository,
    ) -> None:
        self._pipeline = pipeline
        self._audit = audit

    def execute(
        self,
        query: Query,
        *,
        context: AuthorizationContext,
        acting_role: BusinessId,
        audit_id: BusinessId,
        reason: str,
    ) -> Result[AuditedProjectQueryResult]:
        reason = reason.strip()
        if not reason:
            raise ValueError("Ein auditierter Query-Zugriff benötigt eine Begründung.")
        if acting_role not in context.role_ids:
            raise PermissionError("ERR-AUTH-0002: Die handelnde Rolle ist im Kontext nicht aktiv.")

        executed = self._pipeline.execute(query, context=context)
        permission = _QUERY_PERMISSIONS.get(query.query_type, PERM_PROJECT_QUERY_UNMAPPED)
        allowed = executed.is_success
        audit_entry = AuditEntry(
            audit_id=audit_id,
            occurred_at=query.requested_at,
            actor_id=context.user_id,
            acting_role=acting_role,
            permission_id=permission,
            object_id=_query_object_id(query),
            object_business_id=context.project_id or query.query_id,
            action="project_query_accessed" if allowed else "project_query_denied",
            reason=reason,
            correlation_id=query.correlation_id,
            previous_values={},
            new_values={
                "query_id": str(query.query_id),
                "query_type": query.query_type,
                "project_id": str(context.project_id) if context.project_id else None,
                "allowed": allowed,
                "message_codes": tuple(str(message.code) for message in executed.messages),
            },
            previous_hash=self._audit.last_hash(),
        )
        self._audit.append(audit_entry)

        if not executed.is_success:
            return Result.failure(*executed.messages, correlation_id=query.correlation_id)
        assert executed.value is not None
        return Result.success(
            AuditedProjectQueryResult(executed.value, audit_entry),
            correlation_id=query.correlation_id,
        )


def _query_object_id(query: Query) -> ObjectId:
    """Erzeugt eine stabile technische Referenz für den unveränderlichen Query-Vorgang."""
    return ObjectId(uuid5(NAMESPACE_URL, f"projectos-query:{query.query_id}"))
