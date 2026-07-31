"""Export a schematic plan to a deterministic KiCad .kicad_sch skeleton."""
from pathlib import Path
from .kicad_schematic_plan import build_schematic_plan


def _quote(value: str) -> str:
    return '"' + str(value).replace('\\', '\\\\').replace('"', '\\"') + '"'


def build_kicad_sch(plan: dict, connections: list[dict] | None = None) -> str:
    """Return a minimal, deterministic KiCad schematic document skeleton.

    Symbol/net metadata is emitted as KiCad text properties so the generated
    file remains inspectable even before library-specific symbol geometry is
    resolved by KiCad.
    """
    schematic = build_schematic_plan(plan, connections)
    lines = [
        '(kicad_sch (version 20231120) (generator kicad-din-electrical)',
        '  (uuid 00000000-0000-0000-0000-000000000001)',
        '  (paper "A4")',
        '  (lib_symbols)',
        '  )',
        '  (junction (at 0 0) (diameter 0) (color 0 0 0 0) (uuid 00000000-0000-0000-0000-000000000002))',
    ]
    for index, symbol in enumerate(schematic["symbols"], 1):
        lines.extend([
            f'  (text {_quote(symbol["reference"])} (exclude_from_sim no) (effects (font (size 1.27 1.27))))',
            f'  (text {_quote(symbol.get("value", ""))} (exclude_from_sim no) (effects (font (size 1.27 1.27))))',
        ])
    for net_name, pins in schematic["nets"].items():
        lines.append(f'  (text {_quote(f"NET {net_name}: {pins}")} (exclude_from_sim no) (effects (font (size 1.0 1.0))))')
    lines.append(')')
    return "\\n".join(lines) + "\\n"


def write_kicad_sch(path: str | Path, plan: dict, connections: list[dict] | None = None) -> Path:
    target = Path(path)
    target.write_text(build_kicad_sch(plan, connections), encoding="utf-8")
    return target
