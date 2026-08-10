from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .user_management_page import UserManagementSnapshot, UserView

PROJECT_FILE_READ = "project.file.read"
PROJECT_FILE_WRITE = "project.file.write"
PROJECT_FILE_SHARE = "project.file.share"
PROJECT_FILE_ADMIN = "project.file.admin"

PROJECT_FILE_RIGHTS: tuple[tuple[str, str], ...] = (
    (PROJECT_FILE_READ, "Lesen"),
    (PROJECT_FILE_WRITE, "Ändern"),
    (PROJECT_FILE_SHARE, "Teilen"),
    (PROJECT_FILE_ADMIN, "Verwalten"),
)

PROTECTION_PRIVATE_TEAM = "private_team"
PROTECTION_RESTRICTED_LOCAL = "restricted_local"
PROTECTION_REPOSITORY_VISIBLE = "repository_visible"
PROTECTION_LEGACY_UNSPECIFIED = "legacy_unspecified"

PROTECTION_MODES = {
    PROTECTION_PRIVATE_TEAM,
    PROTECTION_RESTRICTED_LOCAL,
    PROTECTION_REPOSITORY_VISIBLE,
}

PROTECTION_LABELS = {
    PROTECTION_PRIVATE_TEAM: "Vertraulich · Team",
    PROTECTION_RESTRICTED_LOCAL: "Vertraulich · lokal",
    PROTECTION_REPOSITORY_VISIBLE: "Repository-sichtbar",
    PROTECTION_LEGACY_UNSPECIFIED: "Nicht festgelegt",
}


@dataclass(frozen=True)
class ProjectAccessRightView:
    permission: str
    label: str
    decision: str
    decision_label: str

    @property
    def allowed(self) -> bool:
        return self.decision == "allow"


@dataclass(frozen=True)
class ProjectAccessUserView:
    user_id: str
    display_name: str
    status_label: str
    rights: tuple[ProjectAccessRightView, ...]

    def decision_for(self, permission: str) -> str:
        for item in self.rights:
            if item.permission == permission:
                return item.decision
        return "not_granted"


_DECISION_LABELS = {
    "allow": "Erlaubt",
    "deny": "Verweigert",
    "not_granted": "Nicht erteilt",
    "user_deactivated": "Benutzer deaktiviert",
}


def normalize_protection_mode(value: str) -> str:
    mode = str(value).strip().lower()
    if mode not in PROTECTION_MODES:
        raise ValueError(f"Unbekannte Projektschutzklasse: {value}")
    return mode


def protection_label(value: str) -> str:
    return PROTECTION_LABELS.get(value, value)


def path_is_within(path: str | Path, root: str | Path) -> bool:
    candidate = Path(path).expanduser().resolve()
    base = Path(root).expanduser().resolve()
    try:
        candidate.relative_to(base)
    except ValueError:
        return False
    return True


def validate_project_target(
    target: str | Path,
    *,
    protection_mode: str,
    repository_root: str | Path,
) -> None:
    """Verhindert, dass vertrauliche Projekte im allgemeinen Quell-Repository landen."""
    mode = normalize_protection_mode(protection_mode)
    if mode in {PROTECTION_PRIVATE_TEAM, PROTECTION_RESTRICTED_LOCAL} and path_is_within(target, repository_root):
        raise ValueError(
            "Vertrauliche ProjectOS-Projekte dürfen nicht im allgemeinen Quell-Repository gespeichert werden. "
            "Verwende einen lokalen geschützten Ordner oder einen separaten privaten Projekt-Repository-Klon."
        )


def _right_for(user: UserView, permission: str, label: str) -> ProjectAccessRightView:
    for item in user.permissions:
        if item.permission == permission:
            return ProjectAccessRightView(
                permission=permission,
                label=label,
                decision=item.decision,
                decision_label=item.decision_label,
            )
    decision = "user_deactivated" if user.lifecycle_status == "deactivated" else "not_granted"
    return ProjectAccessRightView(
        permission=permission,
        label=label,
        decision=decision,
        decision_label=_DECISION_LABELS[decision],
    )


def collect_project_access(snapshot: UserManagementSnapshot) -> tuple[ProjectAccessUserView, ...]:
    """Liest ausschließlich vorhandene ProjectOS-Rechte; es werden keine Grants erfunden."""
    return tuple(
        ProjectAccessUserView(
            user_id=user.user_id,
            display_name=user.display_name,
            status_label=user.status_label,
            rights=tuple(_right_for(user, permission, label) for permission, label in PROJECT_FILE_RIGHTS),
        )
        for user in snapshot.users
    )
