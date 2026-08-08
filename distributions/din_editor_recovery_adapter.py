"""Read-only presentation adapter for project recovery status and explicit recovery action."""
from pathlib import Path

from .din_editor_project_manager import DinEditorProjectManager


class DinEditorRecoveryAdapter:
    """Translate recovery state into GUI-friendly German messages without owning recovery logic."""

    def __init__(self, manager: DinEditorProjectManager):
        self.manager = manager

    @staticmethod
    def _base_state(status: dict) -> dict:
        return {
            "path": status["path"],
            "available": status["available"],
            "valid": status["valid"],
            "can_recover": status["can_recover"],
            "metadata": status.get("metadata"),
            "error": status["error"],
        }

    def state(self, path: str | Path | None = None) -> dict:
        status = self.manager.recovery_status(path)
        base = self._base_state(status)
        if not status["available"]:
            return {
                **base,
                "code": "RECOVERY_NOT_AVAILABLE",
                "title": "Keine Wiederherstellung verfügbar",
                "message": "Für dieses Projekt ist kein letzter gültiger Wiederherstellungsstand vorhanden.",
                "can_recover": False,
                "action_label": None,
            }
        if not status["valid"]:
            return {
                **base,
                "code": "RECOVERY_INVALID",
                "title": "Wiederherstellung nicht verwendbar",
                "message": "Ein Wiederherstellungsstand ist vorhanden, hat die Validierung aber nicht bestanden.",
                "can_recover": False,
                "action_label": None,
            }
        return {
            **base,
            "code": "RECOVERY_AVAILABLE",
            "title": "Wiederherstellung verfügbar",
            "message": "Ein validierter letzter gültiger Projektstand kann ausdrücklich wiederhergestellt werden.",
            "can_recover": True,
            "action_label": "Letzten gültigen Stand wiederherstellen",
        }

    def recover(
        self,
        path: str | Path | None = None,
        *,
        discard_changes: bool = False,
    ):
        state = self.state(path)
        if not state["can_recover"]:
            raise RuntimeError("Wiederherstellung ist für den aktuellen Projektstand nicht freigegeben.")
        return self.manager.recover(path, discard_changes=discard_changes)