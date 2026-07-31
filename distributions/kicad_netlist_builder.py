"""Build a validated logical netlist from DIN device-terminal connections."""
from .din_connection_manifest import validate_connections


def build_netlist(plan: dict, connections: list[dict] | None = None) -> dict:
    connections = [dict(c) for c in (connections or [])]
    errors = validate_connections(connections)
    nets: dict[str, list[dict]] = {}
    for item in connections:
        nets.setdefault(item["net"], []).extend([
            {"reference": item["source_ref"], "pin": item["source_pin"]},
            {"reference": item["target_ref"], "pin": item["target_pin"]},
        ])
    return {
        "format": "kicad-din-netlist",
        "name": plan.get("name", "DIN-Verteiler"),
        "valid": not errors,
        "errors": errors,
        "nets": nets,
    }
