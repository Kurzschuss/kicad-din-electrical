"""Expliziter Ausführungskontext für ProjectOS-Benutzerverwaltungs-Commands.

Der Kontext beschreibt genau einen aufrufenden Command. Er ist keine zweite fachliche
Wahrheit und wird nicht in den Benutzerverwaltungszustand persistiert. Mehrere Commands
eines Vorgangs verwenden getrennte Kontexte mit derselben correlation_id.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import UUID, uuid4


def _uuid(value: str, field_name: str) -> str:
    try:
        return str(UUID(str(value)))
    except (ValueError, TypeError, AttributeError) as exc:
        raise ValueError(f"{field_name} must be a UUID") from exc


@dataclass(frozen=True)
class ProjectOSUserManagementCommandContext:
    """Nicht persistierter Identitäts-, Akteur- und Korrelationskontext eines Commands."""

    actor_user_id: str
    correlation_id: str
    causation_id: str | None = None
    command_id: str = field(default_factory=lambda: str(uuid4()))

    def __post_init__(self) -> None:
        object.__setattr__(self, "command_id", _uuid(self.command_id, "command_id"))
        object.__setattr__(self, "actor_user_id", _uuid(self.actor_user_id, "actor_user_id"))
        object.__setattr__(self, "correlation_id", _uuid(self.correlation_id, "correlation_id"))
        if self.causation_id is not None:
            object.__setattr__(self, "causation_id", _uuid(self.causation_id, "causation_id"))

    def as_dict(self) -> dict[str, Any]:
        return {
            "command_id": self.command_id,
            "actor_user_id": self.actor_user_id,
            "correlation_id": self.correlation_id,
            "causation_id": self.causation_id,
            "persisted": False,
        }
