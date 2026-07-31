"""Export terminal data in a KiCad-friendly, editable form."""
from .terminal_legend import build_terminal_legend


def export_terminal_rows(terminals: list[dict], schema: dict | None = None) -> list[dict]:
    """Return stable rows for UI/CSV/KiCad generation; custom labels are preserved."""
    return build_terminal_legend(terminals, schema)
