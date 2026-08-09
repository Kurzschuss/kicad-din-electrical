"""Read-only Persistenz- und Migrationsstatus der ProjectOS-Benutzerverwaltung."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .din_editor_project_manager import DinEditorProjectManager
from .projectos_project_bundle_v4 import CURRENT_PROJECTOS_BUNDLE_VERSION
from .projectos_user_management_persistence import DERIVED_NOT_PERSISTED


class ZCockpitUserManagementPersistenceView:
    """Erklärt gespeicherten Benutzerverwaltungszustand ohne ihn zu verändern."""

    def __init__(self, manager: DinEditorProjectManager) -> None:
        self.manager = manager

    def _persisted_bundle_version(self) -> int | None:
        path = self.manager.path
        if path is None:
            return None
        source = Path(path)
        if not source.exists():
            return None
        try:
            raw = json.loads(source.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            return None
        if not isinstance(raw, dict):
            return None
        try:
            return int(raw.get("version"))
        except (TypeError, ValueError):
            return None

    def state(self) -> dict[str, Any]:
        user_management = self.manager.user_management
        persisted_version = self._persisted_bundle_version()
        migration_pending = bool(self.manager.project_identity_migration_pending)
        counts = {
            "users": len(user_management.users),
            "permission_assignments": len(user_management.permission_assignments),
            "permission_revocations": len(user_management.permission_revocations),
            "project_roles": len(user_management.project_roles),
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
            "migration_pending": migration_pending,
            "migration_target_version": CURRENT_PROJECTOS_BUNDLE_VERSION if migration_pending else None,
            "has_unsaved_changes": self.manager.has_unsaved_changes,
            "user_management_persistence_version": user_management.as_dict()["version"],
            "persisted_counts": counts,
            "persisted_object_count": sum(counts.values()),
            "derived_not_persisted": list(DERIVED_NOT_PERSISTED),
            "derived_not_persisted_count": len(DERIVED_NOT_PERSISTED),
            "note": (
                "Persistiert werden ausschließlich fachliche Benutzer-, Rechte-, Rechtewiderrufs-, Rollen-, "
                "Aktivierungs-, Rückgabe-, Freigabe- und Nachprüfungsdaten. Evaluator-Ergebnisse, Simulationen "
                "und Z_Cockpit-Ableitungen werden reproduzierbar neu gebildet und nicht gespeichert."
            ),
            "read_only": True,
        }
