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

    def _apply(self, mutation, *, checkpoint: bool = True) -> dict:
        captured = self.history.capture()
        try:
            if checkpoint:
                self.history.checkpoint()
            return self._changed(mutation())
        except Exception:
            self.history.restore(captured)
            raise

    def move(self, index: int, rail: int, start_te: int) -> dict:
        return self._apply(lambda: self.session.move(index, rail, start_te))

    def set_terminal_label(self, index: int, label: str) -> dict:
        return self._apply(lambda: self.session.set_terminal_label(index, label))

    def replace_components(self, components: list[dict], *, checkpoint: bool = True) -> dict:
        if components == self.session.components:
            return self.session.state()

        def replace() -> dict:
            self.session.components = [dict(component) for component in components]
            return self.session.state()

        return self._apply(replace, checkpoint=checkpoint)

    def undo(self) -> dict:
        return self._apply(self.history.undo, checkpoint=False)

    def redo(self) -> dict:
        return self._apply(self.history.redo, checkpoint=False)

    def can_undo(self) -> bool:
        return self.history.can_undo()

    def can_redo(self) -> bool:
        return self.history.can_redo()
