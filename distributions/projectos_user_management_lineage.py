"""Validierte Lineage für Regrant und Rollen-Neu-Zuweisung.

Regrant und Neu-Zuweisung erzeugen neue bestehende Domainobjekte mit neuen IDs.
Historische Rechte-/Rollenzuweisungen sowie Widerrufe/Beendigungen bleiben unverändert.
Die Lineage wird in den bereits persistierten Metadaten der neuen Zuweisung geführt.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Iterable

from .projectos_authorization import ProjectOSPermissionAssignment
from .projectos_user_project_roles import ProjectOSUserProjectRole

PERMISSION_REGRANT_LINEAGE = "permission_regrant"
ROLE_REASSIGNMENT_LINEAGE = "project_role_reassignment"

_RESERVED_PERMISSION_KEYS = {
    "lineage_type",
    "predecessor_assignment_id",
    "predecessor_revocation_id",
    "regranted_at",
    "regranted_by_user_id",
}
_RESERVED_ROLE_KEYS = {
    "lineage_type",
    "predecessor_role_assignment_id",
    "predecessor_termination_id",
    "reassigned_at",
    "reassigned_by_user_id",
}


def _timestamp(value: str, field_name: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{field_name} must be an ISO timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{field_name} must include timezone")
    return parsed.astimezone(timezone.utc)


def _user_exists(state, user_id: str) -> None:
    if sum(1 for item in state.users if item.user_id == user_id) != 1:
        raise ValueError("lineage actor user does not exist")


def _merge_metadata(metadata: dict[str, Any] | None, reserved: Iterable[str]) -> dict[str, Any]:
    result = dict(metadata or {})
    collision = sorted(set(result) & set(reserved))
    if collision:
        raise ValueError(f"reserved lineage metadata key: {collision[0]}")
    return result


def build_permission_regrant(
    state,
    *,
    predecessor_assignment_id: str,
    regranted_at: str,
    regranted_by_user_id: str,
    valid_until: str | None = None,
    source_reference: str | None = None,
    metadata: dict[str, Any] | None = None,
    assignment_id: str | None = None,
) -> ProjectOSPermissionAssignment:
    matches = [item for item in state.permission_assignments if item.assignment_id == predecessor_assignment_id]
    if len(matches) != 1:
        raise ValueError("permission regrant predecessor is unknown or ambiguous")
    predecessor = matches[0]
    _user_exists(state, regranted_by_user_id)

    revocations = [item for item in state.permission_revocations if item.assignment_id == predecessor.assignment_id]
    if len(revocations) != 1:
        raise ValueError("permission regrant requires exactly one predecessor revocation")
    revocation = revocations[0]
    effective_at = _timestamp(regranted_at, "regranted_at")
    if not revocation.is_effective(effective_at):
        raise ValueError("permission regrant requires an effective predecessor revocation")

    if any(
        item.metadata.get("lineage_type") == PERMISSION_REGRANT_LINEAGE
        and item.metadata.get("predecessor_assignment_id") == predecessor.assignment_id
        for item in state.permission_assignments
    ):
        raise ValueError("permission assignment already has a regrant successor")
    if assignment_id is not None and str(assignment_id) == predecessor.assignment_id:
        raise ValueError("permission regrant requires a new assignment_id")

    lineage = _merge_metadata(metadata, _RESERVED_PERMISSION_KEYS)
    lineage.update({
        "lineage_type": PERMISSION_REGRANT_LINEAGE,
        "predecessor_assignment_id": predecessor.assignment_id,
        "predecessor_revocation_id": revocation.revocation_id,
        "regranted_at": effective_at.isoformat(),
        "regranted_by_user_id": regranted_by_user_id,
    })
    kwargs: dict[str, Any] = {
        "user_id": predecessor.user_id,
        "permission": predecessor.permission,
        "source_type": predecessor.source_type,
        "effect": predecessor.effect,
        "scope": predecessor.scope,
        "risk_class": predecessor.risk_class,
        "valid_from": effective_at.isoformat(),
        "valid_until": valid_until,
        "source_reference": source_reference,
        "delegated_by_user_id": (
            regranted_by_user_id if predecessor.source_type == "delegation" else predecessor.delegated_by_user_id
        ),
        "metadata": lineage,
    }
    if assignment_id is not None:
        kwargs["assignment_id"] = assignment_id
    return ProjectOSPermissionAssignment(**kwargs)


def build_role_reassignment(
    state,
    *,
    predecessor_role_assignment_id: str,
    reassigned_at: str,
    reassigned_by_user_id: str,
    valid_until: str | None = None,
    source_reference: str | None = None,
    metadata: dict[str, Any] | None = None,
    role_assignment_id: str | None = None,
    effective_termination_ids: Iterable[str] | None = None,
) -> ProjectOSUserProjectRole:
    matches = [item for item in state.project_roles if item.role_assignment_id == predecessor_role_assignment_id]
    if len(matches) != 1:
        raise ValueError("role reassignment predecessor is unknown or ambiguous")
    predecessor = matches[0]
    _user_exists(state, reassigned_by_user_id)

    terminations = [
        item for item in state.role_assignment_terminations
        if item.role_assignment_id == predecessor.role_assignment_id
    ]
    if len(terminations) != 1:
        raise ValueError("role reassignment requires exactly one predecessor termination")
    termination = terminations[0]
    effective_at = _timestamp(reassigned_at, "reassigned_at")
    if not termination.is_effective(effective_at):
        raise ValueError("role reassignment requires an effective predecessor termination")
    if effective_termination_ids is not None and termination.termination_id not in set(effective_termination_ids):
        raise ValueError("role reassignment requires approval-effective predecessor termination")

    if any(
        item.metadata.get("lineage_type") == ROLE_REASSIGNMENT_LINEAGE
        and item.metadata.get("predecessor_role_assignment_id") == predecessor.role_assignment_id
        for item in state.project_roles
    ):
        raise ValueError("role assignment already has a reassignment successor")
    if role_assignment_id is not None and str(role_assignment_id) == predecessor.role_assignment_id:
        raise ValueError("role reassignment requires a new role_assignment_id")

    lineage = _merge_metadata(metadata, _RESERVED_ROLE_KEYS)
    lineage.update({
        "lineage_type": ROLE_REASSIGNMENT_LINEAGE,
        "predecessor_role_assignment_id": predecessor.role_assignment_id,
        "predecessor_termination_id": termination.termination_id,
        "reassigned_at": effective_at.isoformat(),
        "reassigned_by_user_id": reassigned_by_user_id,
    })
    kwargs: dict[str, Any] = {
        "project_id": predecessor.project_id,
        "user_id": predecessor.user_id,
        "role_type": predecessor.role_type,
        "scope": predecessor.scope,
        "valid_from": effective_at.isoformat(),
        "valid_until": valid_until,
        "assigned_by_user_id": reassigned_by_user_id,
        "source_reference": source_reference,
        "metadata": lineage,
    }
    if role_assignment_id is not None:
        kwargs["role_assignment_id"] = role_assignment_id
    return ProjectOSUserProjectRole(**kwargs)


def lineage_state(state) -> dict[str, Any]:
    assignments = {item.assignment_id: item for item in state.permission_assignments}
    revocations = {item.revocation_id: item for item in state.permission_revocations}
    roles = {item.role_assignment_id: item for item in state.project_roles}
    terminations = {item.termination_id: item for item in state.role_assignment_terminations}
    permission_chains: list[dict[str, Any]] = []
    role_chains: list[dict[str, Any]] = []
    issues: list[dict[str, Any]] = []

    for successor in state.permission_assignments:
        if successor.metadata.get("lineage_type") != PERMISSION_REGRANT_LINEAGE:
            continue
        predecessor_id = successor.metadata.get("predecessor_assignment_id")
        revocation_id = successor.metadata.get("predecessor_revocation_id")
        predecessor = assignments.get(predecessor_id)
        revocation = revocations.get(revocation_id)
        valid = bool(
            predecessor is not None
            and revocation is not None
            and revocation.assignment_id == predecessor_id
            and predecessor.user_id == successor.user_id
            and predecessor.permission == successor.permission
            and predecessor.effect == successor.effect
            and predecessor.scope == successor.scope
        )
        row = {
            "predecessor_assignment": predecessor.as_dict() if predecessor is not None else None,
            "revocation": revocation.as_dict() if revocation is not None else None,
            "successor_assignment": successor.as_dict(),
            "valid": valid,
        }
        permission_chains.append(row)
        if not valid:
            issues.append({"type": "invalid_permission_regrant_lineage", "reference": successor.assignment_id})

    for successor in state.project_roles:
        if successor.metadata.get("lineage_type") != ROLE_REASSIGNMENT_LINEAGE:
            continue
        predecessor_id = successor.metadata.get("predecessor_role_assignment_id")
        termination_id = successor.metadata.get("predecessor_termination_id")
        predecessor = roles.get(predecessor_id)
        termination = terminations.get(termination_id)
        valid = bool(
            predecessor is not None
            and termination is not None
            and termination.role_assignment_id == predecessor_id
            and predecessor.project_id == successor.project_id
            and predecessor.user_id == successor.user_id
            and predecessor.role_type == successor.role_type
            and predecessor.scope == successor.scope
        )
        row = {
            "predecessor_role_assignment": predecessor.as_dict() if predecessor is not None else None,
            "termination": termination.as_dict() if termination is not None else None,
            "successor_role_assignment": successor.as_dict(),
            "valid": valid,
        }
        role_chains.append(row)
        if not valid:
            issues.append({"type": "invalid_role_reassignment_lineage", "reference": successor.role_assignment_id})

    return {
        "project_id": state.project_id,
        "permission_regrant_chains": permission_chains,
        "role_reassignment_chains": role_chains,
        "permission_regrant_count": len(permission_chains),
        "role_reassignment_count": len(role_chains),
        "issues": issues,
        "attention_required": bool(issues),
        "read_only": True,
        "persisted": False,
    }
