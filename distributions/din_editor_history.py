"""Undo/redo support for the complete DIN editor state."""
from copy import deepcopy
from .din_editor_session import DinEditorSession


class DinEditorHistory:
    def __init__(self, session: DinEditorSession, sync_log=None):
        self.session = session
        self.sync_log = sync_log
        self._undo = []
        self._redo = []

    def _snapshot(self):
        state = {"components": deepcopy(self.session.components)}
        if self.sync_log is not None:
            state["sync_log"] = deepcopy(self.sync_log.entries)
        return state

    def _restore(self, state: dict) -> dict:
        self.session.components = deepcopy(state["components"])
        if self.sync_log is not None:
            self.sync_log.entries = deepcopy(state.get("sync_log", []))
        return self.session.state()

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
        return self._restore(self._undo.pop())

    def redo(self) -> dict:
        if not self._redo:
            return self.session.state()
        self._undo.append(self._snapshot())
        return self._restore(self._redo.pop())

    def clear(self) -> None:
        self._undo.clear()
        self._redo.clear()

    def state(self) -> dict:
        return {"can_undo": bool(self._undo), "can_redo": bool(self._redo), "undo_depth": len(self._undo), "redo_depth": len(self._redo)}
