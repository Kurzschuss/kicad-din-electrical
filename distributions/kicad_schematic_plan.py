"""Create a deterministic KiCad-oriented schematic placement plan."""
from .kicad_netlist_builder import build_netlist
from .kicad_symbol_resolver import resolve_components


def build_schematic_plan(plan: dict, connections: list[dict] | None = None) -> dict:
    netlist = build_netlist(plan, connections)
    components = resolve_components(plan.get("components", []))
    terminals = resolve_components(plan.get("terminals", []))
    return {
        "format": "kicad-din-schematic-plan",
        "name": plan.get("name", "DIN-Verteiler"),
        "symbols": components + terminals,
        "nets": netlist["nets"],
        "valid": netlist["valid"],
        "errors": netlist["errors"],
    }
