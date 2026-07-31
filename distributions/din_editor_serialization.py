"""Serialize and restore DIN editor sessions without GUI dependencies."""
from .din_editor_session import DinEditorSession


def export_session(session: DinEditorSession) -> dict:
    return {
        "version": 1,
        "rails": session.rails,
        "te_per_rail": session.te_per_rail,
        "components": [dict(c) for c in session.components],
    }


def import_session(data: dict) -> DinEditorSession:
    if int(data.get("version", 1)) != 1:
        raise ValueError("unsupported DIN editor session version")
    return DinEditorSession(
        components=data.get("components", []),
        rails=int(data.get("rails", 18)),
        te_per_rail=int(data.get("te_per_rail", 12)),
    )
