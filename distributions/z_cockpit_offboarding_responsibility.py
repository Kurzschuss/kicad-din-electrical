"""Read-only Z_Cockpit-Sicht auf offene ProjectOS-Offboarding-Verantwortungen."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Mapping

from .projectos_offboarding_responsibility_diagnostics import (
    ProjectOSOffboardingResponsibilityDiagnostic,
)


class ZCockpitOffboardingResponsibilityView:
    def __init__(
        self,
        manager,
        *,
        role_risk_class_map: Mapping[str, str] | None = None,
    ) -> None:
        self.manager = manager
        self.role_risk_class_map = dict(role_risk_class_map or {})

    def state(
        self,
        user_id: str,
        *,
        scope: str = "project",
        at: datetime | None = None,
    ) -> dict[str, Any]:
        diagnostic = ProjectOSOffboardingResponsibilityDiagnostic(
            self.manager.user_management,
            role_risk_class_map=self.role_risk_class_map,
        ).state(user_id, scope=scope, at=at)
        return {
            **diagnostic,
            "view": "offboarding_responsibility",
            "title": "Offboarding-Verantwortungsdiagnostik",
            "attention_required": diagnostic["resolution_required"],
            "read_only": True,
            "persisted": False,
        }
