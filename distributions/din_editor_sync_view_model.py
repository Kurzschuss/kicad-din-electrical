"""GUI-ready view model for DIN/KiCad synchronization conflicts."""
from .din_editor_conflicts import build_conflict_list, resolve_conflicts
from .din_editor_sync_service import DinEditorSyncService


class DinEditorSyncViewModel:
    def __init__(self, sync_service: DinEditorSyncService):
        self.sync_service = sync_service
        self._kicad_fields: list[dict] = []

    def refresh(self, kicad_fields: list[dict] | None = None) -> dict:
        if kicad_fields is not None:
            self._kicad_fields = [dict(field) for field in kicad_fields]
        conflicts = build_conflict_list(self.sync_service.session.components, self._kicad_fields)
        report = self.sync_service.report()
        return {"valid": not conflicts and report["valid"], "conflicts": conflicts, "report": report}

    def choose(self, reference: str, choice: str) -> dict:
        conflicts = build_conflict_list(self.sync_service.session.components, self._kicad_fields)
        selected = [c for c in conflicts if str(c.get("reference")) == str(reference)]
        if not selected:
            raise KeyError(f"no synchronization conflict for {reference}")
        self.sync_service.session.components = resolve_conflicts(self.sync_service.session.components, selected, choice=choice)
        return self.refresh()
