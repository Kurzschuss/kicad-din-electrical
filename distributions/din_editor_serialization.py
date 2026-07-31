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
    if not isinstance(data, dict):
        raise ValueError("invalid DIN editor session")
    try:
        version = int(data.get("version", 1))
    except (TypeError, ValueError) as exc:
        raise ValueError("invalid DIN editor session version") from exc
    if version != 1:
        raise ValueError("unsupported DIN editor session version")
    components = data.get("components", [])
    if not isinstance(components, list) or any(not isinstance(component, dict) for component in components):
        raise ValueError("DIN editor components must be a list of objects")
    return DinEditorSession(
        components=[dict(component) for component in components],
        rails=data.get("rails", 18),
        te_per_rail=data.get("te_per_rail", 12),
    )
