"""Human-readable report for an automatically allocated DIN distribution."""
from .auto_distribution import allocate


def report(devices: list[str]) -> str:
    fields = allocate(devices)
    lines = ["DIN-Verteilungsplan", "==================="]
    total = sum(field["modules"] for field in fields)
    lines.append(f"Gesamt: {total}/216 Module")
    for field in fields:
        lines.append(
            f"Feld {field['field']}: {field['modules']}/36 Module, "
            f"Reserve {field['reserve']}"
        )
        lines.append("  " + ", ".join(field["devices"]))
    return "\n".join(lines)
