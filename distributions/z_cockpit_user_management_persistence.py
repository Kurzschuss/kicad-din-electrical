"""Read-only Persistenz- und Migrationsstatus der ProjectOS-Benutzerverwaltung."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .din_editor_project_manager import DinEditorProjectManager
from .projectos_project_bundle_v4 import CURRENT_PROJECTOS_BUNDLE_VERSION
from .projectos_user_management_persistence import DERIVED_NOT_PERSISTED, USER_MANAGEMENT_PERSISTENCE_VERSION


class ZCockpitUserManagementPersistenceView:
    def __init__(self, manager: DinEditorProjectManager) -> None:
        self.manager = manager

    def _persisted_versions(self) -> tuple[int | None, int | None]:
        path = self.manager.path
        if path is None:
            return None, None
        source = Path(path)
        if not source.exists():
            return None, None
        try:
            raw = json.loads(source.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            return None, None
        if not isinstance(raw, dict):
            return None, None
        try:
            bundle_version = int(raw.get("version"))
        except (TypeError, ValueError):
            bundle_version = None
        user_management_version = None
        user_management = raw.get("user_management")
        if isinstance(user_management, dict):
            try:
                user_management_version = int(user_management.get("version"))
            except (TypeError, ValueError):
                user_management_version = None
        return bundle_version, user_management_version

    def state(self) -> dict[str, Any]:
        user_management = self.manager.user_management
        persisted_version, persisted_user_management_version = self._persisted_versions()
        bundle_migration_pending = bool(self.manager.project_identity_migration_pending)
        user_management_migration_pending = bool(
            persisted_user_management_version is not None
            and persisted_user_management_version != USER_MANAGEMENT_PERSISTENCE_VERSION
        )
        migration_pending = bundle_migration_pending or user_management_migration_pending
        counts = {
            "users": len(user_management.users),
            "user_deactivations": len(user_management.user_deactivations),
            "user_reactivations": len(user_management.user_reactivations),
            "permission_assignments": len(user_management.permission_assignments),
            "permission_revocations": len(user_management.permission_revocations),
            "project_roles": len(user_management.project_roles),
            "role_assignment_terminations": len(user_management.role_assignment_terminations),
            "activations": len(user_management.activations),
            "deactivations": len(user_management.deactivations),
            "approval_requests": len(user_management.approval_requests),
            "approvals": len(user_management.approvals),
            "post_reviews": len(user_management.post_reviews),
        }
        return {
            "project_id": self.manager.project_id,
            "project_path": str(self.manager.path) if self.manager.path else None,
            "current_bundle_version": CURRENT_PROJECTOS_BUNDLE_VERSION,
            "persisted_bundle_version": persisted_version,
            "bundle_v4_persisted": persisted_version == CURRENT_PROJECTOS_BUNDLE_VERSION,
            "bundle_migration_pending": bundle_migration_pending,
            "migration_pending": migration_pending,
            "migration_target_version": CURRENT_PROJECTOS_BUNDLE_VERSION if bundle_migration_pending else None,
            "current_user_management_persistence_version": USER_MANAGEMENT_PERSISTENCE_VERSION,
            "persisted_user_management_version": persisted_user_management_version,
            "user_management_persistence_version": user_management.as_dict()["version"],
            "user_management_migration_pending": user_management_migration_pending,
            "user_management_migration_target_version": (
                USER_MANAGEMENT_PERSISTENCE_VERSION if user_management_migration_pending else None
            ),
            "has_unsaved_changes": self.manager.has_unsaved_changes,
            "persisted_counts": counts,
            "persisted_object_count": sum(counts.values()),
            "derived_not_persisted": list(DERIVED_NOT_PERSISTED),
            "derived_not_persisted_count": len(DERIVED_NOT_PERSISTED),
            "note": (
                "Persistiert werden ausschließlich fachliche Benutzer- und Lifecycle-Daten einschließlich "
                "Deaktivierungen und Reaktivierungen derselben user_id. Ältere Benutzerverwaltungs-Versionen "
                "bleiben lesbar und werden erst beim expliziten Speichern aktualisiert. Evaluator-Ergebnisse "
                "und Z_Cockpit-Ableitungen werden reproduzierbar neu gebildet."
            ),
            "read_only": True,
        }
