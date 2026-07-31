"""Generic DIN-rail device catalog for distribution planning.

Dimensions are intentionally explicit so real manufacturer parts can be added
without changing the layout engine.
"""

from .din_power_supplies import power_supply
from .din_switchgear import main_switch, surge_protection, transfer_switch


def device(part_number: str, manufacturer: str, component_type: str, width_te: int, **spec) -> dict:
    width_te = int(width_te)
    if width_te < 1:
        raise ValueError("width_te must be positive")
    return {
        "part_number": part_number,
        "manufacturer": manufacturer,
        "component_type": component_type,
        "width_te": width_te,
        "din_rail": True,
        **spec,
    }


def generic_catalog() -> list[dict]:
    catalog = []
    for poles in (2, 3, 4):
        catalog.append(main_switch(poles, poles, catalog_source="generic"))
        catalog.append(transfer_switch(poles, poles, catalog_source="generic"))
        catalog.append(surge_protection(poles=poles, width_te=poles, catalog_source="generic"))
    for voltage in (5, 12, 24):
        for width in (1, 2, 3, 4):
            catalog.append(power_supply(voltage, width, catalog_source="generic"))
    return catalog
