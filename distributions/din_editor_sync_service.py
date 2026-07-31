"""Conflict-aware bidirectional synchronization for DIN/KiCad terminal labels."""
from .din_kicad_sync import apply_kicad_terminal_labels, export_terminal_labels, terminal_sync_report
from .din_editor_change_service import DinEditorChangeService


class DinEditorSyncService:
    def __init__(self, change_service: DinEditorChangeService):
        self.change_service = change_service

    @property
    def session(self):
        return self.change_service.session

    def report(self) -> dict:
        return terminal_sync_report(self.session.components)

    def export_labels(self) -> list[dict]:
        return export_terminal_labels(self.session.components)

    def import_labels(self, fields: list[dict], overwrite: bool = True) -> dict:
        before = [dict(c) for c in self.session.components]
        after = apply_kicad_terminal_labels(before, fields, overwrite=overwrite)
        if after == before:
            return self.session.state()
        self.session.components = after
        if self.change_service.on_change is not None:
            self.change_service.on_change()
        return self.session.state()
