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
        self.session.components[:] = deepcopy(state["components"])
        if self.sync_log is not None:
            self.sync_log.entries[:] = deepcopy(state.get("sync_log", []))
        return self.session.state()

    def checkpoint(self):
        snapshot = self._snapshot()
        if self._undo and self._undo[-1] == snapshot:
            return
        if self._undo:
            self._undo.append(deepcopy(self._undo[-1]))
        else:
            self._undo.append(snapshot)
        self._redo.clear()

    def undo(self) -> dict:
        if len(self._undo) <= 1:
            return self.session.state()
        current = self._snapshot()
        self._redo.append(current)
        self._undo.pop()
        return self._restore(self._undo[-1])

    def redo(self) -> dict:
        if not self._redo:
            return self.session.state()
        current = self._snapshot()
        target = self._redo.pop()
        self._undo.append(current)
        return self._restore(target)

    def clear(self) -> None:
        self._undo.clear()
        self._redo.clear()

    def state(self) -> dict:
        return {"can_undo": len(self._undo) > 1, "can_redo": bool(self._redo), "undo_depth": max(0, len(self._undo) - 1), "redo_depth": len(self._redo)}
