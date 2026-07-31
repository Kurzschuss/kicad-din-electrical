"""User-editable DIN rail placement helpers."""
from .din_rail_layout import component_te


def move_component(component: dict, rail: int, start_te: int) -> dict:
    """Move a component without changing its electrical identity or label."""
    rail = int(rail)
    start_te = int(start_te)
    width = component_te(component)
    if rail < 1 or start_te < 1:
        raise ValueError("rail and start_te must be positive")
    updated = dict(component)
    updated.update({"rail": rail, "start_te": start_te, "end_te": start_te + width - 1, "width_te": width})
    return updated


def move_components(components: list[dict], reference: str, rail: int, start_te: int) -> list[dict]:
    found = False
    result = []
    for component in components:
        if str(component.get("reference")) == str(reference):
            result.append(move_component(component, rail, start_te))
            found = True
        else:
            result.append(dict(component))
    if not found:
        raise KeyError(f"unknown component reference: {reference}")
    return result
