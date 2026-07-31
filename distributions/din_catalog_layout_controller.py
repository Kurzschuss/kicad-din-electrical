"""Integrate catalog selection, auto-placement and editor state."""
from .din_catalog_editor import add_catalog_device, catalog_choices
from .din_layout_editor_view import build_editor_state


def add_device_and_refresh(components: list[dict], device: dict, rails: int = 18, te_per_rail: int = 12) -> dict:
    updated = add_catalog_device(components, device, rails, te_per_rail)
    return build_editor_state(updated, rails, te_per_rail)


def available_devices(path=None) -> list[dict]:
    return catalog_choices(path)
