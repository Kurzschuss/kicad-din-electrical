"""Auditierte projektbezogene Autorisierungsentscheidungen und Handlungsausführungen."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Generic, TypeVar

from .audit import AuditEntry
from .identifiers import BusinessId, CorrelationId, ObjectId
from .project_authorization import ProjectActionAuthorizationResult, ProjectActionAuthorizationService
from .sqlite_audit import SQLiteAuditRepository

T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class AuditedProjectActionResult(Generic[T]):
    """Ergebnis einer auditierten Autorisierungsentscheidung und optionalen Handlung."""

    authorization: ProjectActionAuthorizationResult
    audit_entry: AuditEntry
    executed: bool
    value: T | None = None


class AuditedProjectActionService:
    """Auditiert jede Entscheidung und führt nur erlaubte Handlungen aus.

    Die aufrufende ``SQLiteUnitOfWork`` bildet die Transaktionsgrenze. Damit werden
    Audit-Eintrag und fachliche Nebenwirkung gemeinsam bestätigt oder zurückgerollt.
    """

    def __init__(
        self,
        authorization: ProjectActionAuthorizationService,
        audit: SQLiteAuditRepository,
    ) -> None:
        self._authorization = authorization
        self._audit = audit

    def execute(
        self,
        project_id: BusinessId,
        permission: BusinessId,
        *,
        at: datetime,
        audit_id: BusinessId,
        correlation_id: CorrelationId,
        project_object_id: ObjectId,
        action: str,
        reason: str,
        operation: Callable[[], T],
        unavailable_user_ids: frozenset[BusinessId] = frozenset(),
        previous_values: Mapping[str, object] | None = None,
        new_values: Mapping[str, object] | None = None,
    ) -> AuditedProjectActionResult[T]:
        """Prüft, auditiert und führt eine projektbezogene Handlung atomar aus."""
        if at.tzinfo is None:
            raise ValueError("Der Ausführungszeitpunkt benötigt einen Zeitzonenbezug.")
        instant = at.astimezone(timezone.utc)
        normalized_action = action.strip()
        normalized_reason = reason.strip()
        if not normalized_action:
            raise ValueError("Eine Projekthandlung benötigt eine Aktion.")
        if not normalized_reason:
            raise ValueError("Eine Projekthandlung benötigt eine Begründung.")

        decision = self._authorization.authorize(
            project_id,
            permission,
            at=instant,
            unavailable_user_ids=unavailable_user_ids,
        )
        actor = decision.authority.authorized_user.user_id
        responsibility_id = decision.authority.source.value.replace("_", "-")
        acting_role = BusinessId(f"PRJROLE-{responsibility_id}")
        audit_entry = AuditEntry(
            audit_id=audit_id,
            occurred_at=instant,
            actor_id=actor,
            acting_role=acting_role,
            permission_id=permission,
            object_id=project_object_id,
            object_business_id=project_id,
            action=normalized_action,
            reason=normalized_reason,
            correlation_id=correlation_id,
            previous_values={
                **dict(previous_values or {}),
                "authorization_allowed": decision.allowed,
                "project_grant_match": decision.project_grant_match,
                "authority_source": decision.authority.source.value,
            },
            new_values={
                **dict(new_values or {}),
                "execution_status": "EXECUTED" if decision.allowed else "DENIED",
                "authorization_reason": decision.reason,
            },
            previous_hash=self._audit.last_hash(),
        )
        self._audit.append(audit_entry)

        if not decision.allowed:
            return AuditedProjectActionResult(
                authorization=decision,
                audit_entry=audit_entry,
                executed=False,
            )

        value = operation()
        return AuditedProjectActionResult(
            authorization=decision,
            audit_entry=audit_entry,
            executed=True,
            value=value,
        )
