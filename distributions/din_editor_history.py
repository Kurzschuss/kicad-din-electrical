"""Undo/redo support for the GUI-independent DIN editor session."""
from copy import deepcopy
from .din_editor_session import DinEditorSession


class DinEditorHistory:
    def __init__(self, session: DinEditorSession):
        self.session = session
        self._undo = []
        self._redo = []

    def _snapshot(self):
        return deepcopy(self.session.components)

    def checkpoint(self):
        snapshot = self._snapshot()
        if self._undo and self._undo[-1] == snapshot:
            return
        self._undo.append(snapshot)
        self._redo.clear()

    def undo(self) -> dict:
        if not self._undo:
            return self.session.state()
        self._redo.append(self._snapshot())
        self.session.components = self._undo.pop()
        return self.session.state()

    def redo(self) -> dict:
        if not self._redo:
            return self.session.state()
        self._undo.append(self._snapshot())
        self.session.components = self._redo.pop()
        return self.session.state()

    def clear(self) -> None:
        self._undo.clear()
        self._redo.clear()

    def state(self) -> dict:
        return {"can_undo": bool(self._undo), "can_redo": bool(self._redo), "undo_depth": len(self._undo), "redo_depth": len(self._redo)}
