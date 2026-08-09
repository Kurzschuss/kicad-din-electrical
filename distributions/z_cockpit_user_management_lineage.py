"""Read-only Z_Cockpit-Sicht für Regrant- und Rollen-Neu-Zuweisungs-Lineage."""
from __future__ import annotations

from typing import Any

from .projectos_user_management_lineage import lineage_state


class ZCockpitUserManagementLineageView:
    """Zeigt historische Vorgänger→Lifecycle→Nachfolger-Ketten ohne Mutation."""

    def __init__(self, manager) -> None:
        self.manager = manager

    def state(self) -> dict[str, Any]:
        state = lineage_state(self.manager.user_management)
        return {
            **state,
            "traffic_light": "yellow" if state["attention_required"] else "green",
            "note": (
                "Die Lineage-Sicht ist rein lesend. Sie zeigt neue Zuweisungsidentitäten "
                "und ihre historischen Vorgänger; sie reaktiviert keine alte ID und verändert "
                "weder Rechte, Rollen, Audit noch Bus."
            ),
        }
