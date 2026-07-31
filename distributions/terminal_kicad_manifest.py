"""Build a KiCad-ready manifest for terminal labels and connections."""
from .terminal_kicad_export import kicad_terminal_labels


def build_kicad_terminal_manifest(terminals: list[dict], schema: dict | None = None) -> dict:
    labels = kicad_terminal_labels(terminals, schema)
    return {
        "format": "kicad-terminal-manifest-v1",
        "editable_labels": True,
        "terminals": labels,
    }
