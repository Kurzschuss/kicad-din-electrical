#!/usr/bin/env python3
"""Erzeugt die Symbol- und Footprint-Indizes aus der Repositorystruktur."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
SYMBOL_ROOT = REPO_ROOT / "symbols"
FOOTPRINT_ROOT = REPO_ROOT / "footprints"
REFERENCE_ROOT = REPO_ROOT / "docs" / "04_Reference"
SYMBOL_INDEX = REFERENCE_ROOT / "SYMBOL_INDEX.md"
FOOTPRINT_INDEX = REFERENCE_ROOT / "FOOTPRINT_INDEX.md"


def display_path(path: Path) -> Path:
    """Zeigt Repositorypfade relativ, andere Pfade unverändert an."""
    try:
        return path.relative_to(REPO_ROOT)
    except ValueError:
        return path


def symbol_libraries(root: Path = SYMBOL_ROOT) -> list[Path]:
    """Liefert alle Symbolbibliotheken alphabetisch sortiert."""
    return sorted(root.glob("Z_*.kicad_sym"), key=lambda path: path.name.casefold())


def footprint_libraries(root: Path = FOOTPRINT_ROOT) -> list[Path]:
    """Liefert alle .pretty-Bibliotheken alphabetisch sortiert."""
    return sorted(
        (path for path in root.glob("Z_*.pretty") if path.is_dir()),
        key=lambda path: path.name.casefold(),
    )


def _quoted_value(text: str, start: int) -> tuple[str, int]:
    """Liest einen KiCad-String ab dem öffnenden Anführungszeichen."""
    value: list[str] = []
    escaped = False
    index = start + 1
    while index < len(text):
        char = text[index]
        if escaped:
            value.append(char)
            escaped = False
        elif char == "\\":
            escaped = True
        elif char == '"':
            return "".join(value), index + 1
        else:
            value.append(char)
        index += 1
    return "".join(value), index


def symbol_names(path: Path) -> list[str]:
    """Liest die Namen der Hauptsymbole einer KiCad-Symbolbibliothek."""
    text = path.read_text(encoding="utf-8")
    names: list[str] = []
    depth = 0
    index = 0
    in_string = False
    escaped = False

    while index < len(text):
        char = text[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            index += 1
            continue
        if char == '"':
            in_string = True
            index += 1
            continue
        if char == "(":
            if depth == 1 and text.startswith("(symbol", index):
                cursor = index + len("(symbol")
                while cursor < len(text) and text[cursor].isspace():
                    cursor += 1
                if cursor < len(text) and text[cursor] == '"':
                    name, _ = _quoted_value(text, cursor)
                    names.append(name)
            depth += 1
        elif char == ")":
            depth = max(0, depth - 1)
        index += 1

    return sorted(set(names), key=str.casefold)


def render_symbol_index(libraries: list[Path], footprint_root: Path = FOOTPRINT_ROOT) -> str:
    lines = [
        "# Symbolbibliotheken",
        "",
        "> Diese Datei wird mit `python tools/generate_library_reference.py` erzeugt.",
        "",
        "Die Symbolbibliotheken liegen direkt unter `symbols/`.",
        "",
        f"**Anzahl der Bibliotheken:** {len(libraries)}",
        "",
        "## Bibliotheken und Inhalte",
        "",
    ]
    for library in libraries:
        names = symbol_names(library) if library.is_file() else []
        pretty = footprint_root / f"{library.stem}.pretty"
        footprints = (
            sorted(pretty.glob("*.kicad_mod"), key=lambda path: path.name.casefold())
            if pretty.is_dir()
            else []
        )
        symbol_status = f"{len(names)} Symbol(e)" if names else "vorbereitet, noch leer"
        footprint_status = (
            f"`{pretty.name}` mit {len(footprints)} Footprint(s)"
            if pretty.is_dir()
            else f"`{pretty.name}` fehlt"
        )
        lines.append(f"- `{library.name}` — {symbol_status}")
        lines.append(f"  - Footprintbibliothek: {footprint_status}")
        lines.extend(f"  - Symbol: `{name}`" for name in names)
    lines.extend([
        "",
        "## Namensregel",
        "",
        "Der KiCad-Bibliotheksname entspricht dem Dateinamen ohne `.kicad_sym`.",
        "Eine qualifizierte Symbol-ID verwendet das Format `<Bibliothek>:<Symbol>`.",
        "",
    ])
    return "\n".join(lines)


def render_footprint_index(libraries: list[Path]) -> str:
    lines = [
        "# Footprintbibliotheken",
        "",
        "> Diese Datei wird mit `python tools/generate_library_reference.py` erzeugt.",
        "",
        "Die Footprintbibliotheken liegen als `.pretty`-Ordner unter `footprints/`.",
        "",
        f"**Anzahl der Bibliotheken:** {len(libraries)}",
        "",
        "## Bibliotheken",
        "",
    ]
    for library in libraries:
        footprints = sorted(library.glob("*.kicad_mod"), key=lambda path: path.name.casefold())
        status = f"{len(footprints)} Footprint(s)" if footprints else "vorbereitet, noch leer"
        lines.append(f"- `{library.name}` — {status}")
        lines.extend(f"  - `{path.name}`" for path in footprints)
    lines.extend([
        "",
        "## Namensregel",
        "",
        "Eine qualifizierte Footprint-ID verwendet das Format `<Bibliothek>:<Footprint>`.",
        "Eine `.pretty`-Bibliothek darf mehrere `.kicad_mod`-Dateien enthalten.",
        "",
    ])
    return "\n".join(lines)


def generated_files() -> dict[Path, str]:
    return {
        SYMBOL_INDEX: render_symbol_index(symbol_libraries()),
        FOOTPRINT_INDEX: render_footprint_index(footprint_libraries()),
    }


def check_files(files: dict[Path, str]) -> bool:
    outdated: list[Path] = []
    for path, expected in files.items():
        actual = path.read_text(encoding="utf-8") if path.is_file() else ""
        if actual != expected:
            outdated.append(path)
    if outdated:
        print("Die folgenden Referenzdateien sind nicht aktuell:", file=sys.stderr)
        for path in outdated:
            print(f"- {display_path(path)}", file=sys.stderr)
        print("Bitte den Generator ohne --check ausführen.", file=sys.stderr)
        return False
    print("Die Bibliotheksreferenz ist aktuell.")
    return True


def write_files(files: dict[Path, str]) -> None:
    REFERENCE_ROOT.mkdir(parents=True, exist_ok=True)
    for path, content in files.items():
        path.write_text(content, encoding="utf-8")
        print(f"Erzeugt: {display_path(path)}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="nur prüfen, ob die erzeugten Indexdateien aktuell sind")
    args = parser.parse_args()
    files = generated_files()
    if args.check:
        return 0 if check_files(files) else 1
    write_files(files)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
