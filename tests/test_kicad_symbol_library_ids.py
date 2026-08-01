"""Tests for KiCad symbol library IDs after the Z_ library rename."""

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


def test_every_catalog_symbol_resolves_to_an_existing_prefixed_library():
    catalog = load_symbol_catalog()
    missing = []
    mismatches = []

    for symbol_name in sorted(catalog):
        resolved = resolve_symbol({"symbol": symbol_name}, catalog)
        expected_library = f"Z_{symbol_name}"
        expected_id = f"{expected_library}:{symbol_name}"
        if resolved["library_id"] != expected_id:
            mismatches.append((symbol_name, resolved["library_id"], expected_id))
        if not (SYMBOL_LIBRARY_ROOT / f"{expected_library}.kicad_sym").is_file():
            missing.append(symbol_name)

    assert mismatches == []
    assert missing == []
