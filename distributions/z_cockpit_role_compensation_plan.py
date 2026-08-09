"""Read-only Z_Cockpit-Sicht für den Rollen-Kompensationsplan."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from .projectos_role_compensation_plan import ProjectOSRoleCompensationPlanner


class ZCockpitRoleCompensationPlanView:
    """Bereitet den Simulation-First-Rollenplan ohne Mutation für Z_Cockpit auf."""

    def __init__(self, runtime) -> None:
        self.runtime = runtime
        self.planner = ProjectOSRoleCompensationPlanner(runtime)

    def state(
        self,
        *,
        role_assignment_id: str,
        actor_user_id: str,
        at: datetime | None = None,
    ) -> dict[str, Any]:
        plan = self.planner.plan(
            role_assignment_id=role_assignment_id,
            actor_user_id=actor_user_id,
            at=at,
        )
        attention = bool(
            not plan["actor_authorized"]
            or plan["configuration_required"]
            or plan["requires_multistep_lifecycle"]
            or plan["post_review_required"]
        )
        ready = bool(
            plan["synchronous_compensation_possible"]
            or plan["compensation_completed"]
        )
        return {
            **plan,
            "traffic_light": "yellow" if attention else "green",
            "attention_required": attention,
            "ready_or_completed": ready,
            "note": (
                "Die Kompensationsplanung ist rein lesend. Sie legt weder eine "
                "Rollenzuweisungs-Beendigung noch einen Approval-Auftrag oder eine "
                "Neu-Zuweisung an und aktiviert kein generisches Rollen-Undo."
            ),
        }
