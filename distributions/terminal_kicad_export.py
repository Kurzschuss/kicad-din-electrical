"""Prepare terminal labels for KiCad symbol/label generation."""
from .terminal_export import export_terminal_rows


def kicad_terminal_labels(terminals: list[dict], schema: dict | None = None) -> list[dict]:
    rows = export_terminal_rows(terminals, schema)
    return [
        {
            "reference": row["terminal"],
            "value": row.get("function") or "Terminal",
            "label": row["terminal"],
            "circuit": row.get("circuit"),
            "phase": row.get("phase"),
            "fi_group": row.get("fi_group"),
            "n_group": row.get("n_group"),
            "row": row.get("row"),
            "te": row.get("te"),
        }
        for row in rows
    ]
