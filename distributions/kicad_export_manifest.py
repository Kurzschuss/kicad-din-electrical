"""Convert a DIN plan into a KiCad-oriented export manifest.

This is deliberately format-neutral: it prepares references, labels and
terminal metadata without writing a .kicad_sch file yet.
"""


def _ref(prefix: str, index: int) -> str:
    return f"{prefix}{index}"


def build_export_manifest(plan: dict) -> dict:
    components = []
    for index, item in enumerate(plan.get("components", []), 1):
        component = dict(item)
        component["reference"] = component.get("reference") or _ref("Q", index)
        component["value"] = component.get("value") or component.get("part_number") or component.get("component_type", "DIN_DEVICE")
        components.append(component)

    terminals = []
    for index, item in enumerate(plan.get("terminals", []), 1):
        terminal = dict(item)
        terminal["reference"] = terminal.get("reference") or _ref("X", index)
        terminal["label"] = terminal.get("label") or terminal.get("terminal_label") or f"X{index}"
        terminals.append(terminal)

    return {
        "format": "kicad-din-export-manifest",
        "name": plan.get("name", "DIN-Verteiler"),
        "capacity_te": plan.get("capacity_te", 216),
        "rails": plan.get("rails", 18),
        "te_per_rail": plan.get("te_per_rail", 12),
        "components": components,
        "terminals": terminals,
    }
