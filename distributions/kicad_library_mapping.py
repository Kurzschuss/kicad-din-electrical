"""Map DIN catalog component types to the project's KiCad symbol catalog."""
import csv
from pathlib import Path

SYMBOL_LIBRARY_ROOT = Path(__file__).parent.parent / "symbols" / "DIN_Electrical_Symbols"
DEFAULT_SYMBOL_CATALOG = SYMBOL_LIBRARY_ROOT / "symbol_catalog.csv"

_COMPONENT_TO_SYMBOL = {
    "DIN_RAIL_MAIN_SWITCH": "MAIN_SWITCH",
    "DIN_RAIL_TRANSFER_SWITCH": "MAIN_SWITCH",
    "DIN_RAIL_SURGE_PROTECTION": "DISTRIBUTION",
    "DIN_RAIL_POWER_SUPPLY": "DISTRIBUTION",
    "DIN_RAIL_TERMINAL_BLOCK": "DISTRIBUTION",
}


def load_symbol_catalog(path: str | Path = DEFAULT_SYMBOL_CATALOG) -> dict[str, dict]:
    with Path(path).open(newline="", encoding="utf-8") as handle:
        rows = csv.DictReader(handle)
        return {row["Symbol"]: dict(row) for row in rows if row.get("Symbol")}


def resolve_symbol(component: dict, catalog: dict[str, dict] | None = None) -> dict:
    catalog = catalog or load_symbol_catalog()
    component_type = str(component.get("component_type", ""))
    symbol_name = component.get("symbol") or _COMPONENT_TO_SYMBOL.get(component_type, "DISTRIBUTION")
    entry = catalog.get(symbol_name)
    if entry is None:
        raise KeyError(f"symbol {symbol_name!r} is not present in the KiCad symbol catalog")
    library_name = f"Z_{symbol_name}"
    return {
        "symbol": symbol_name,
        "library_id": f"{library_name}:{symbol_name}",
        "standard": entry.get("Standard"),
    }
