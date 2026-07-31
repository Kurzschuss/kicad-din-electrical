"""Represent wiring connections between DIN devices and terminal blocks."""


def connection(source_ref: str, source_pin: str, target_ref: str, target_pin: str, net: str, **meta) -> dict:
    return {
        "source_ref": str(source_ref),
        "source_pin": str(source_pin),
        "target_ref": str(target_ref),
        "target_pin": str(target_pin),
        "net": str(net),
        **meta,
    }


def build_connection_manifest(plan: dict, connections: list[dict] | None = None) -> dict:
    """Keep explicit device-terminal wiring separate from physical placement."""
    return {
        "format": "kicad-din-connection-manifest",
        "name": plan.get("name", "DIN-Verteiler"),
        "connections": [dict(c) for c in (connections or [])],
    }


def validate_connections(connections: list[dict]) -> list[str]:
    errors = []
    required = ("source_ref", "source_pin", "target_ref", "target_pin", "net")
    for index, item in enumerate(connections, 1):
        missing = [key for key in required if not item.get(key)]
        if missing:
            errors.append(f"connection {index}: missing {', '.join(missing)}")
    return errors
