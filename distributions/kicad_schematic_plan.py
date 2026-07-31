"""Create a deterministic KiCad-oriented schematic placement plan."""
from .kicad_symbol_manifest import build_symbol_manifest
from .kicad_netlist_builder import build_netlist


def build_schematic_plan(plan: dict, connections: list[dict] | None = None) -> dict:
    symbols = build_symbol_manifest(plan)
    netlist = build_netlist(plan, connections)
    return {
        "format": "kicad-din-schematic-plan",
        "name": plan.get("name", "DIN-Verteiler"),
        "symbols": symbols["symbols"],
        "nets": netlist["nets"],
        "valid": netlist["valid"],
        "errors": netlist["errors"],
    }
