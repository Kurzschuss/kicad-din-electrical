"""Compact text visualization of up to six 36-module DIN fields."""
from .field_plan import detailed_plan


def render(devices: list[str]) -> str:
    plan = detailed_plan(devices)
    lines = [f"DIN-Verteilung {plan['total_modules']}/{plan['max_modules']} Module"]
    for field in plan["fields"]:
        used = field["modules"]
        reserve = field["reserve"]
        bar = "█" * used + "·" * reserve
        lines.append(f"Feld {field['field']:>1}: |{bar}| {used:>2}/36")
        lines.append("        " + "  ".join(field["devices"]))
    return "\n".join(lines)
