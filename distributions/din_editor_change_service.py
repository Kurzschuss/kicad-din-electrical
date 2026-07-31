"""Atomic editor changes with history checkpoints."""
from .din_editor_history import DinEditorHistory
from .din_editor_session import DinEditorSession


class DinEditorChangeService:
    def __init__(self, session: DinEditorSession):
        self.session = session
        self.history = DinEditorHistory(session)

    def move(self, index: int, rail: int, start_te: int) -> dict:
        self.history.checkpoint()
        return self.session.move(index, rail, start_te)

    def set_terminal_label(self, index: int, label: str) -> dict:
        self.history.checkpoint()
        return self.session.set_terminal_label(index, label)

    def undo(self) -> dict:
        return self.history.undo()

    def redo(self) -> dict:
        return self.history.redo()
