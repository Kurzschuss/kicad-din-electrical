"""Tests for KiCad symbol library IDs after the Z_ library rename."""
from pathlib import Path

from distributions.kicad_library_mapping import SYMBOL_LIBRARY_ROOT, load_symbol_catalog, resolve_symbol


def test_resolved_library_id_uses_existing_prefixed_library():
    catalog = load_symbol_catalog()

    resolved = resolve_symbol({"symbol": "MCB"}, catalog)

    assert resolved["library_id"] == "Z_MCB:MCB"
    library_name, symbol_name = resolved["library_id"].split(":", 1)
    assert symbol_name == resolved["symbol"]
    assert (SYMBOL_LIBRARY_ROOT / f"{library_name}.kicad_sym").is_file()


def test_default_component_mapping_uses_prefixed_library_id():
    catalog = load_symbol_catalog()

    resolved = resolve_symbol({"component_type": "DIN_RAIL_MAIN_SWITCH"}, catalog)

    assert resolved["library_id"] == "Z_MAIN_SWITCH:MAIN_SWITCH"
