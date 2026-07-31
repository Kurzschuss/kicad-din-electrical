"""Bridge the DIN device catalog to the 216-TE layout engine."""
from .din_device_catalog import generic_catalog
from .din_rail_layout import layout_summary


def catalog_layout(components: list[dict] | None = None, rails: int = 18, te_per_rail: int = 12) -> dict:
    """Return a complete placement/usage summary for selected catalog devices."""
    selected = list(components) if components is not None else generic_catalog()
    return layout_summary(selected, rails=rails, te_per_rail=te_per_rail)


def fit_catalog_components(components: list[dict], rails: int = 18, te_per_rail: int = 12) -> bool:
    try:
        layout_summary(components, rails=rails, te_per_rail=te_per_rail)
    except ValueError:
        return False
    return True
