"""Kontextsensitive, read-only Folgeziele für aufgelöste Z_Cockpit-Detailansichten."""
from __future__ import annotations

from typing import Any

from .z_cockpit_navigation import ZCockpitNavigationTarget
from .z_cockpit_navigation_context import ZCockpitNavigationContext
from .z_cockpit_navigation_resolver import ZCockpitNavigationResolver


class ZCockpitDetailActionsView:
    """Erzeugt ausschließlich belegbare Folgeziele aus einem aktuellen Navigationskontext."""

    def __init__(self, resolver: ZCockpitNavigationResolver) -> None:
        self.resolver = resolver

    def state(self, context: ZCockpitNavigationContext) -> dict[str, Any]:
        resolved = self.resolver.resolve_context(context)
        target = context.current
        payload = resolved["payload"]
        actions: list[dict[str, Any]] = []

        if target.view == "knowledge_element":
            element = payload["element"]
            knowledge_id = element["knowledge_id"]
            correlation_id = element.get("correlation_id") or target.correlation_id

            actions.append(self._action(
                "knowledge_origin",
                "Herkunft anzeigen",
                ZCockpitNavigationTarget(
                    view="knowledge_origin",
                    project_id=target.project_id,
                    correlation_id=correlation_id,
                    knowledge_ids=(knowledge_id,),
                ),
            ))
            actions.append(self._action(
                "knowledge_diagnostics",
                "Wissensdiagnose anzeigen",
                ZCockpitNavigationTarget(
                    view="knowledge_diagnostics",
                    project_id=target.project_id,
                    correlation_id=correlation_id,
                    knowledge_ids=(knowledge_id,),
                ),
            ))
            if correlation_id is not None:
                actions.append(self._action(
                    "correlation",
                    "Vorgang öffnen",
                    ZCockpitNavigationTarget(
                        view="correlation",
                        project_id=target.project_id,
                        correlation_id=correlation_id,
                    ),
                ))
                actions.append(self._action(
                    "audit",
                    "Audit des Vorgangs anzeigen",
                    ZCockpitNavigationTarget(
                        view="audit",
                        project_id=target.project_id,
                        correlation_id=correlation_id,
                        audit_filter="all",
                    ),
                ))

            related_ids = []
            for relation in payload.get("relations", []):
                other = (
                    relation["target_knowledge_id"]
                    if relation["source_knowledge_id"] == knowledge_id
                    else relation["source_knowledge_id"]
                )
                if other not in related_ids:
                    related_ids.append(other)
            for related_id in related_ids:
                actions.append(self._action(
                    "knowledge_element",
                    "Verbundenes Wissen öffnen",
                    ZCockpitNavigationTarget(
                        view="knowledge_element",
                        project_id=target.project_id,
                        correlation_id=correlation_id,
                        knowledge_ids=(related_id,),
                    ),
                ))

        elif target.view in {"knowledge_path", "knowledge_origin"}:
            for knowledge_id in target.knowledge_ids:
                actions.append(self._action(
                    "knowledge_element",
                    "Wissensknoten öffnen",
                    ZCockpitNavigationTarget(
                        view="knowledge_element",
                        project_id=target.project_id,
                        correlation_id=target.correlation_id,
                        knowledge_ids=(knowledge_id,),
                    ),
                ))
            if target.correlation_id is not None:
                actions.append(self._action(
                    "correlation",
                    "Vorgang öffnen",
                    ZCockpitNavigationTarget(
                        view="correlation",
                        project_id=target.project_id,
                        correlation_id=target.correlation_id,
                    ),
                ))

        elif target.view == "correlation":
            actions.append(self._action(
                "audit",
                "Audit des Vorgangs anzeigen",
                ZCockpitNavigationTarget(
                    view="audit",
                    project_id=target.project_id,
                    correlation_id=target.correlation_id,
                    audit_filter="all",
                ),
            ))
            if self.resolver.memory is not None:
                actions.append(self._action(
                    "knowledge_diagnostics",
                    "Wissensdiagnose des Vorgangs anzeigen",
                    ZCockpitNavigationTarget(
                        view="knowledge_diagnostics",
                        project_id=target.project_id,
                        correlation_id=target.correlation_id,
                    ),
                ))

        if target.view != "project_overview":
            actions.append(self._action(
                "project_overview",
                "Zur Projektübersicht",
                ZCockpitNavigationTarget(
                    view="project_overview",
                    project_id=target.project_id,
                ),
            ))

        return {
            "project_id": target.project_id,
            "current_view": target.view,
            "action_count": len(actions),
            "actions": actions,
            "return_target": context.return_target.as_dict() if context.return_target else None,
            "read_only": True,
            "note": (
                "Folgeziele werden ausschließlich aus tatsächlich vorhandenen IDs, Beziehungen und dem aktuellen Scope erzeugt. "
                "Die Sicht verändert weder Projektzustand noch Navigationsverlauf."
            ),
        }

    @staticmethod
    def _action(code: str, label: str, target: ZCockpitNavigationTarget) -> dict[str, Any]:
        return {"code": code, "label": label, "target": target.as_dict()}
