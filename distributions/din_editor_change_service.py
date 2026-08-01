"""Atomic editor changes with history checkpoints."""
from .din_editor_history import DinEditorHistory
from .din_editor_session import DinEditorSession


class DinEditorChangeService:
    def __init__(self, session: DinEditorSession, history: DinEditorHistory | None = None, on_change=None):
        self.session = session
        self.history = history or DinEditorHistory(session)
        self.on_change = on_change

    def _changed(self, state: dict) -> dict:
        if self.on_change is not None:
            self.on_change()
        return state

    def move(self, index: int, rail: int, start_te: int) -> dict:
        self.history.checkpoint()
        return self._changed(self.session.move(index, rail, start_te))

    def set_terminal_label(self, index: int, label: str) -> dict:
        self.history.checkpoint()
        return self._changed(self.session.set_terminal_label(index, label))

    def replace_components(self, components: list[dict], *, checkpoint: bool = True) -> dict:
        if components == self.session.components:
            return self.session.state()
        if checkpoint:
            self.history.checkpoint()
        self.session.components = [dict(component) for component in components]
        return self._changed(self.session.state())

    def undo(self) -> dict:
        state = self.history.undo()
        return self._changed(state)

    def redo(self) -> dict:
        state = self.history.redo()
        return self._changed(state)

    def can_undo(self) -> bool:
        return self.history.can_undo()

    def can_redo(self) -> bool:
        return self.history.can_redo()
