"""Vertrauenswürdige ProjectOS-Verwaltung für Benutzer, White-/Blacklist und Zugriffsrechte.

Die statische Z_Cockpit-Oberfläche ist ausdrücklich nicht die Sicherheitsinstanz.
Jede schreibende Operation lädt das aktive ProjectOS-Bundle neu, ermittelt den
mit ``gh`` authentifizierten GitHub-Benutzer, ordnet ihn einem ProjectOS-Profil
zu und wertet die vorhandene ProjectOS-Autorisierung fail-closed aus.
"""
from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from distributions.din_editor_project_manager import DinEditorProjectManager
from distributions.projectos_authorization import ProjectOSAuthorizationEvaluator
from distributions.projectos_user_management_change_service import ProjectOSUserManagementChangeService
from tools.check_repository_version import (
    authenticated_github_user,
    check_repository_version,
    load_authorized_developers,
)

PERMISSION_CATALOG: dict[str, str] = {
    "project.file.read": "Projektdatei lesen",
    "project.file.write": "Projektdatei ändern",
    "project.file.share": "Projekt teilen/freigeben",
    "project.file.admin": "Projektzugriff verwalten",
    "project.user.manage": "Benutzer verwalten",
    "project.permission.manage": "Rechte/White-/Blacklist verwalten",
    "cockpit.view": "Z_Cockpit-Bereich sehen",
    "cockpit.edit": "Z_Cockpit-Bereich bearbeiten",
    "github.issue.prepare": "GitHub-Fehlermeldung vorbereiten",
    "github.issue.auto_submit": "GitHub-Fehlermeldung automatisch senden",
}

SCOPE_CATALOG: dict[str, str] = {
    "project": "Gesamtes Projekt",
    "page:start": "Start",
    "page:projekt": "Projekt",
    "page:geraete": "Geräte",
    "page:bibliotheken": "Bibliotheken",
    "page:hersteller": "Hersteller",
    "page:qualitaet": "Qualität",
    "page:diagnose": "Diagnose",
    "page:sicherheit": "Sicherheit",
    "page:dokumentation": "Dokumentation",
    "page:einstellungen": "Einstellungen",
    "page:benutzer": "Benutzerverwaltung",
    "page:berechtigungen": "Berechtigungen",
    "page:fehlerbericht": "Fehler melden",
}

BOOTSTRAP_PERMISSIONS = (
    "project.file.read",
    "project.file.write",
    "project.file.share",
    "project.file.admin",
    "project.user.manage",
    "project.permission.manage",
    "github.issue.prepare",
    "github.issue.auto_submit",
)


def load_manager(path: str | Path) -> DinEditorProjectManager:
    manager = DinEditorProjectManager()
    manager.load(Path(path), discard_changes=True)
    return manager


def _repository_write_gate() -> None:
    result = check_repository_version()
    if not result.current or not result.official_remote:
        raise PermissionError(f"Repositoryzustand erlaubt keine ProjectOS-Verwaltungsänderung: {result.message}")


def authenticated_project_user(manager: DinEditorProjectManager):
    login = authenticated_github_user().strip()
    if not login:
        raise PermissionError("Kein mit gh authentifizierter GitHub-Benutzer verfügbar")
    matches = [
        user for user in manager.user_management.users
        if user.github_login and user.github_login.casefold() == login.casefold()
    ]
    if len(matches) != 1:
        raise PermissionError("Der authentifizierte GitHub-Benutzer ist keinem eindeutigen ProjectOS-Benutzer zugeordnet")
    return matches[0], login


def authorize(manager: DinEditorProjectManager, permission: str, *, scope: str = "project") -> dict[str, Any]:
    if permission not in PERMISSION_CATALOG:
        raise ValueError(f"Unbekanntes ProjectOS-Recht: {permission}")
    if scope not in SCOPE_CATALOG:
        raise ValueError(f"Unbekannter ProjectOS-Scope: {scope}")
    actor, login = authenticated_project_user(manager)
    state = manager.user_management
    result = ProjectOSAuthorizationEvaluator(
        state.permission_assignments,
        state.permission_revocations,
        state.user_deactivations,
        state.user_reactivations,
    ).evaluate(actor, permission, scope=scope)
    if not result["allowed"]:
        raise PermissionError(
            f"ProjectOS-Recht verweigert: {permission} / {scope} ({result['decision']})"
        )
    return {"actor": actor, "github_login": login, "authorization": result}


def bootstrap_admin(
    path: str | Path,
    *,
    display_name: str,
    weight: int = 1000,
) -> dict[str, Any]:
    """Legt nur bei leerem Benutzerbestand den ersten Administrator an.

    Bootstrap ist ausschließlich für einen aktuell geprüften Originalstand und einen
    GitHub-Benutzer aus ``config/authorized_developers.json`` zulässig.
    """
    _repository_write_gate()
    manager = load_manager(path)
    if manager.user_management.users:
        raise PermissionError("Bootstrap ist nur bei einer leeren ProjectOS-Benutzerverwaltung zulässig")
    login = authenticated_github_user().strip()
    if not login:
        raise PermissionError("Für den Bootstrap ist eine gh-Authentifizierung erforderlich")
    authorized = load_authorized_developers()
    if login.casefold() not in authorized:
        raise PermissionError("Der authentifizierte GitHub-Benutzer steht nicht in der Repository-Entwickler-Whitelist")
    service = ProjectOSUserManagementChangeService(manager)
    user = service.create_user(
        display_name,
        weight=weight,
        roles=("Projektadministrator",),
    )
    # GitHub-Zuordnung wird über denselben atomaren Change-Service committed.
    linked = replace(user, github_login=login)
    service._commit(
        "user_profile_changed",
        users=tuple(linked if item.user_id == user.user_id else item for item in service.state.users),
    )
    for permission in BOOTSTRAP_PERMISSIONS:
        service.command_assign_permission(
            user_id=user.user_id,
            permission=permission,
            source_type="direct",
            effect="allow",
            scope="project",
            risk_class="critical" if permission.endswith("admin") or permission.endswith("manage") else "high",
            source_reference="bootstrap:repository-developer-whitelist",
        )
    manager.save()
    return {
        "operation": "bootstrap_admin",
        "project_id": manager.project_id,
        "user_id": user.user_id,
        "display_name": linked.display_name,
        "github_login": login,
        "granted_permissions": list(BOOTSTRAP_PERMISSIONS),
    }


def create_user(
    path: str | Path,
    *,
    display_name: str,
    weight: int = 100,
    github_login: str | None = None,
) -> dict[str, Any]:
    _repository_write_gate()
    manager = load_manager(path)
    gate = authorize(manager, "project.user.manage")
    service = ProjectOSUserManagementChangeService(manager)
    user = service.create_user(display_name, weight=weight)
    if github_login:
        updated = replace(user, github_login=github_login)
        service._commit(
            "user_profile_changed",
            users=tuple(updated if item.user_id == user.user_id else item for item in service.state.users),
        )
        user = updated
    manager.save()
    return {
        "operation": "user_create",
        "actor_user_id": gate["actor"].user_id,
        "user": user.as_dict(),
    }


def update_user(
    path: str | Path,
    *,
    user_id: str,
    display_name: str,
    weight: int,
    github_login: str | None,
) -> dict[str, Any]:
    _repository_write_gate()
    manager = load_manager(path)
    gate = authorize(manager, "project.user.manage")
    service = ProjectOSUserManagementChangeService(manager)
    matches = [item for item in service.state.users if item.user_id == user_id]
    if len(matches) != 1:
        raise ValueError("Unbekannte Benutzer-ID")
    updated = replace(
        matches[0],
        display_name=display_name,
        weight=weight,
        github_login=github_login or None,
    )
    service._commit(
        "user_profile_changed",
        users=tuple(updated if item.user_id == user_id else item for item in service.state.users),
    )
    manager.save()
    return {
        "operation": "user_update",
        "actor_user_id": gate["actor"].user_id,
        "user": updated.as_dict(),
    }


def add_access_rule(
    path: str | Path,
    *,
    user_id: str,
    permission: str,
    scope: str,
    list_type: str,
    risk_class: str = "medium",
) -> dict[str, Any]:
    _repository_write_gate()
    if permission not in PERMISSION_CATALOG:
        raise ValueError("Unbekanntes ProjectOS-Recht")
    if scope not in SCOPE_CATALOG:
        raise ValueError("Unbekannter ProjectOS-Scope")
    source_type = str(list_type).strip().lower()
    if source_type not in {"whitelist", "blacklist"}:
        raise ValueError("list_type muss whitelist oder blacklist sein")
    manager = load_manager(path)
    gate = authorize(manager, "project.permission.manage")
    service = ProjectOSUserManagementChangeService(manager)
    assignment = service.command_assign_permission(
        user_id=user_id,
        permission=permission,
        source_type=source_type,
        effect="allow" if source_type == "whitelist" else "deny",
        scope=scope,
        risk_class=risk_class,
        source_reference=f"z-cockpit:{source_type}",
        metadata={"managed_by": gate["github_login"]},
    )
    manager.save()
    return {
        "operation": "rule_add",
        "actor_user_id": gate["actor"].user_id,
        "assignment": assignment.as_dict(),
    }


def revoke_access_rule(
    path: str | Path,
    *,
    assignment_id: str,
    reason: str,
) -> dict[str, Any]:
    _repository_write_gate()
    manager = load_manager(path)
    gate = authorize(manager, "project.permission.manage")
    service = ProjectOSUserManagementChangeService(manager)
    revocation = service.command_revoke_permission(
        assignment_id=assignment_id,
        revoked_at=datetime.now(timezone.utc).isoformat(),
        revoked_by_user_id=gate["actor"].user_id,
        reason=reason,
        source_reference="z-cockpit:permission-management",
        metadata={"managed_by": gate["github_login"]},
    )
    manager.save()
    return {
        "operation": "rule_revoke",
        "actor_user_id": gate["actor"].user_id,
        "revocation": revocation.as_dict(),
    }


def governance_summary(path: str | Path) -> dict[str, Any]:
    manager = load_manager(path)
    state = manager.user_management
    return {
        "project_id": manager.project_id,
        "users": [item.as_dict() for item in state.users],
        "permission_assignments": [item.as_dict() for item in state.permission_assignments],
        "permission_revocations": [item.as_dict() for item in state.permission_revocations],
        "permissions": dict(PERMISSION_CATALOG),
        "scopes": dict(SCOPE_CATALOG),
    }
