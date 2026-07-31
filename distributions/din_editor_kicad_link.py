"""Link DIN editor projects to the existing KiCad schematic export path."""
from pathlib import Path
from .din_editor_session import DinEditorSession
from .din_editor_project_io import load_project, save_project
from .kicad_sch_export import write_kicad_sch


def save_din_project(session: DinEditorSession, path: str | Path) -> Path:
    return save_project(session, path)


def load_din_project(path: str | Path) -> DinEditorSession:
    return load_project(path)


def export_session_to_kicad(session: DinEditorSession, path: str | Path, connections: list[dict] | None = None) -> Path:
    plan = {
        "components": [dict(c) for c in session.components],
        "rails": session.rails,
        "te_per_rail": session.te_per_rail,
    }
    return write_kicad_sch(path, plan, connections)
