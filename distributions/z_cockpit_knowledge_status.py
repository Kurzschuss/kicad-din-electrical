"""Read-only Z_Cockpit-Adapter für Wissensstatus, Widersprüche und Ablösungen."""
from __future__ import annotations

from .projectos_knowledge_status import ProjectOSKnowledgeStatusService
from .projectos_project_memory import ProjectOSProjectMemory


class ZCockpitKnowledgeStatusView:
    """Bereitet explizite Wissenskonflikte und Ablöseketten für Z_Cockpit auf."""

    def __init__(self, memory: ProjectOSProjectMemory) -> None:
        self.memory = memory
        self._service = ProjectOSKnowledgeStatusService(memory)

    def explain(
        self,
        knowledge_id: str,
        *,
        correlation_id: str | None = None,
    ) -> dict:
        result = self._service.analyze(knowledge_id, correlation_id=correlation_id)
        result["read_only"] = True
        result["status_text"] = self._status_text(result)
        return result

    @staticmethod
    def _status_text(state: dict) -> str:
        if state.get("supersession_cycle_detected"):
            return "Die explizite Ablösekette enthält einen Zyklus. Ein aktueller Nachfolger kann nicht eindeutig bestimmt werden."
        if state.get("supersession_ambiguous"):
            replacements = ", ".join(item["title"] for item in state.get("terminal_successors", []))
            return f"Die Ablösekette ist mehrdeutig. Mehrere aktuelle Nachfolger sind explizit gespeichert: {replacements}."
        if state.get("current_successor") is not None and state["is_superseded"]:
            chain = state.get("supersession_chains", [])
            titles = [node["title"] for node in chain[0]["nodes"]] if len(chain) == 1 else []
            chain_text = " → ".join(titles)
            current = state["current_successor"]["title"]
            if chain_text:
                return f"Dieses Wissen wurde über die Ablösekette {chain_text} ersetzt. Aktueller expliziter Nachfolger: {current}."
            return f"Dieses Wissen wurde ersetzt. Aktueller expliziter Nachfolger: {current}."
        if state["is_superseded"]:
            replacements = ", ".join(item["other"]["title"] for item in state["superseded_by"])
            return f"Dieses Wissen wurde explizit ersetzt durch: {replacements}."
        if state["has_conflicts"]:
            conflicts = ", ".join(item["other"]["title"] for item in state["conflicts"])
            return f"Zu diesem Wissen bestehen explizite Widersprüche oder Widerlegungen: {conflicts}."
        return "Für dieses Wissen ist im sichtbaren Graphen keine explizite Ablösung oder Widerlegung gespeichert."