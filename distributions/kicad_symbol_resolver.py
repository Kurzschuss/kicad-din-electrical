"""Resolve DIN catalog devices to known KiCad project symbols and pins."""
from .kicad_library_mapping import load_symbol_catalog, resolve_symbol
from .din_pin_mapping import pins_for_component


def resolve_component(component: dict, catalog: dict[str, dict] | None = None) -> dict:
    symbol = resolve_symbol(component, catalog)
    pins = pins_for_component(component)
    return {
        **dict(component),
        **symbol,
        "pins": pins,
    }


def resolve_components(components: list[dict]) -> list[dict]:
    catalog = load_symbol_catalog()
    return [resolve_component(component, catalog) for component in components]
