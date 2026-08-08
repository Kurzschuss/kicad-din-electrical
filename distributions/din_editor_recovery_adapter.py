"""Read-only presentation adapter for project recovery status and explicit recovery action."""
from pathlib import Path

from .din_editor_project_manager import DinEditorProjectManager


class DinEditorRecoveryAdapter:
    """Translate recovery state into GUI-friendly German messages without owning recovery logic."""

    def __init__(self, manager: DinEditorProjectManager):
        self.manager = manager

    def state(self, path: str | Path | None = None) -> dict:
        status = self.manager.recovery_status(path)
        if not status["available"]:
            return {
                "code": "RECOVERY_NOT_AVAILABLE",
                "title": "Keine Wiederherstellung verfügbar",
                "message": "Für dieses Projekt ist kein letzter gültiger Wiederherstellungsstand vorhanden.",
                "path": status["path"],
                "available": False,
                "valid": status["valid"],
                "can_recover": False,
                "action_label": None,
                "error": status["error"],
            }
        if not status["valid"]:
            return {
                "code": "RECOVERY_INVALID",
                "title": "Wiederherstellung nicht verwendbar",
                "message": "Ein Wiederherstellungsstand ist vorhanden, hat die Validierung aber nicht bestanden.",
                "path": status["path"],
                "available": True,
                "valid": False,
                "can_recover": False,
                "action_label": None,
                "error": status["error"],
            }
        return {
            "code": "RECOVERY_AVAILABLE",
            "title": "Wiederherstellung verfügbar",
            "message": "Ein validierter letzter gültiger Projektstand kann ausdrücklich wiederhergestellt werden.",
            "path": status["path"],
            "available": True,
            "valid": True,
            "can_recover": True,
            "action_label": "Letzten gültigen Stand wiederherstellen",
            "error": None,
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
