"""Prepare KiCad symbol instances from the DIN export manifest."""
from .kicad_export_manifest import build_export_manifest


def build_symbol_manifest(plan: dict) -> dict:
    export = build_export_manifest(plan)
    symbols = []
    for item in export["components"]:
        symbols.append({
            "reference": item["reference"],
            "value": item["value"],
            "part_number": item.get("part_number"),
            "symbol_library": item.get("symbol_library") or "Device:Generic",
            "footprint": item.get("footprint"),
            "rail": item.get("rail"),
            "start_te": item.get("start_te"),
            "end_te": item.get("end_te"),
        })
    for item in export["terminals"]:
        symbols.append({
            "reference": item["reference"],
            "value": item.get("value") or item.get("part_number") or "Terminal_Block",
            "part_number": item.get("part_number"),
            "symbol_library": item.get("symbol_library") or "Connector_Generic:Conn_01x02",
            "footprint": item.get("footprint"),
            "label": item["label"],
            "terminal_function": item.get("terminal_function"),
            "rail": item.get("rail"),
            "start_te": item.get("start_te"),
            "end_te": item.get("end_te"),
        })
    return {"format": "kicad-symbol-manifest", "name": export["name"], "symbols": symbols}
