"""Read-only project correlation context for cross-cutting ProjectOS consumers."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .din_editor_project_manager import DinEditorProjectManager


@dataclass(frozen=True)
class DinEditorProjectContext:
    """Stable project context shared by audit, future bus/memory and Z_Cockpit consumers."""

    project_id: str
    project_path: str | None
    project_identity_migration_pending: bool
    recovered_from: str | None

    @classmethod
    def from_manager(cls, manager: DinEditorProjectManager) -> "DinEditorProjectContext":
        return cls(
            project_id=manager.project_id,
            project_path=str(manager.path) if manager.path is not None else None,
            project_identity_migration_pending=manager.project_identity_migration_pending,
            recovered_from=str(manager._recovered_from) if manager._recovered_from is not None else None,
        )

    def as_dict(self) -> dict:
        return {
            "project_id": self.project_id,
            "project_path": self.project_path,
            "project_identity_migration_pending": self.project_identity_migration_pending,
            "recovered_from": self.recovered_from,
        }

    def correlation_metadata(
        self,
        *,
        correlation_id: str | None = None,
        causation_id: str | None = None,
    ) -> dict:
        """Return transport-neutral correlation metadata without creating side effects."""
        metadata = {"project_id": self.project_id}
        if correlation_id is not None:
            metadata["correlation_id"] = str(correlation_id)
        if causation_id is not None:
            metadata["causation_id"] = str(causation_id)
        return metadata
