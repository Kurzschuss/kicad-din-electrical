"""Export a DIN schematic plan with resolved project symbol metadata."""
import os
from pathlib import Path
from tempfile import NamedTemporaryFile

from .kicad_schematic_plan import build_schematic_plan
from .kicad_terminal_label_export import terminal_label_fields


class KiCadSchematicExportError(RuntimeError):
    """Raised when a KiCad schematic cannot be exported safely."""


def _quote(value: str) -> str:
    return '"' + str(value).replace('\\', '\\\\').replace('"', '\\"') + '"'


def build_kicad_sch(plan: dict, connections: list[dict] | None = None) -> str:
    schematic = build_schematic_plan(plan, connections)
    fields = terminal_label_fields(plan)
    lines = [
        '(kicad_sch (version 20231120) (generator kicad-din-electrical)',
        '  (uuid 00000000-0000-0000-0000-000000000001)',
        '  (paper "A4")',
        '  (lib_symbols)',
        '  )',
    ]
    for symbol in schematic["symbols"]:
        lines.extend([
            f'  (text {_quote(symbol["reference"])} (exclude_from_sim no) (effects (font (size 1.27 1.27))))',
            f'  (text {_quote(symbol.get("value", ""))} (exclude_from_sim no) (effects (font (size 1.27 1.27))))',
            f'  (text {_quote(symbol.get("library_id", ""))} (exclude_from_sim no) (effects (font (size 0.9 0.9))))',
            f'  (text {_quote(str(symbol.get("pins", [])))} (exclude_from_sim no) (effects (font (size 0.9 0.9))))',
        ])
    for field in fields:
        field_text = f'{field["reference"]} | {field["field_name"]}={field["label"]}'
        lines.append(
            f'  (text {_quote(field_text)} (exclude_from_sim no) (effects (font (size 1.0 1.0))))'
        )
    for net_name, pins in schematic["nets"].items():
        net_text = f"NET {net_name}: {pins}"
        lines.append(
            f'  (text {_quote(net_text)} (exclude_from_sim no) (effects (font (size 1.0 1.0))))'
        )
    lines.append(')')
    return "\n".join(lines) + "\n"


def write_kicad_sch(path: str | Path, plan: dict, connections: list[dict] | None = None) -> Path:
    """Build and atomically replace a KiCad schematic export target."""
    target = Path(path)
    temporary: Path | None = None
    try:
        rendered = build_kicad_sch(plan, connections)
        target.parent.mkdir(parents=True, exist_ok=True)
        with NamedTemporaryFile(
            "w",
            encoding="utf-8",
            dir=target.parent,
            prefix=f".{target.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            temporary = Path(handle.name)
            handle.write(rendered)
            handle.flush()
            os.fsync(handle.fileno())
        temporary.replace(target)
    except (OSError, TypeError, ValueError, KeyError) as exc:
        if temporary is not None:
            try:
                temporary.unlink(missing_ok=True)
            except OSError:
                pass
        raise KiCadSchematicExportError(
            f"KiCad schematic cannot be exported safely: {target}"
        ) from exc
    return target
