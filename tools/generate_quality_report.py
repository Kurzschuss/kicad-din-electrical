#!/usr/bin/env python3
"""Erzeugt einen zusammenfassenden Qualitätsbericht der KiCad-Bibliotheken."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
import argparse
import sys

try:
    from tools.validate_libraries import (
        FOOTPRINT_ROOT,
        REPO_ROOT,
        SYMBOL_ROOT,
        footprint_policy,
        symbol_names,
        symbol_properties,
        validate_repository,
    )
except ModuleNotFoundError:  # direkter Aufruf aus dem Repository-Hauptordner
    from validate_libraries import (
        FOOTPRINT_ROOT,
        REPO_ROOT,
        SYMBOL_ROOT,
        footprint_policy,
        symbol_names,
        symbol_properties,
        validate_repository,
    )

REPORT_PATH = REPO_ROOT / "docs" / "04_Reference" / "QUALITY_REPORT.md"


def collect_statistics(symbol_root: Path = SYMBOL_ROOT, footprint_root: Path = FOOTPRINT_ROOT) -> dict[str, object]:
    symbol_files = sorted(symbol_root.glob("Z_*.kicad_sym"), key=lambda path: path.name.casefold())
    pretty_dirs = sorted(
        (path for path in footprint_root.glob("Z_*.pretty") if path.is_dir()),
        key=lambda path: path.name.casefold(),
    )
    footprint_files = sorted(
        footprint_root.glob("Z_*.pretty/*.kicad_mod"),
        key=lambda path: path.as_posix().casefold(),
    )

    filled_libraries = 0
    empty_libraries = 0
    total_symbols = 0
    policies: Counter[str] = Counter()
    assigned_footprints = 0
    unassigned_footprints = 0

    for path in symbol_files:
        names = symbol_names(path)
        if names:
            filled_libraries += 1
            total_symbols += len(names)
            properties = symbol_properties(path)
            policies[footprint_policy(properties)] += 1
            if properties.get("Footprint", "").strip():
                assigned_footprints += 1
            else:
                unassigned_footprints += 1
        else:
            empty_libraries += 1

    report = validate_repository(symbol_root, footprint_root)
    return {
        "symbol_libraries": len(symbol_files),
        "filled_symbol_libraries": filled_libraries,
        "empty_symbol_libraries": empty_libraries,
        "symbols": total_symbols,
        "footprint_libraries": len(pretty_dirs),
        "footprints": len(footprint_files),
        "policies": policies,
        "assigned_footprints": assigned_footprints,
        "unassigned_footprints": unassigned_footprints,
        "errors": report.errors,
        "warnings": report.warnings,
    }


def render_quality_report(stats: dict[str, object]) -> str:
    policies: Counter[str] = stats["policies"]  # type: ignore[assignment]
    errors = stats["errors"]
    warnings = stats["warnings"]
    status = "✅ keine blockierenden Fehler" if not errors else f"❌ {len(errors)} blockierende Fehler"

    lines = [
        "# Bibliotheks-Qualitätsbericht",
        "",
        "> Diese Datei wird mit `python tools/generate_quality_report.py` erzeugt.",
        "",
        f"**Gesamtstatus:** {status}",
        "",
        "## Übersicht",
        "",
        "| Bereich | Anzahl |",
        "|---|---:|",
        f"| Symbolbibliotheken | {stats['symbol_libraries']} |",
        f"| davon befüllt | {stats['filled_symbol_libraries']} |",
        f"| davon vorbereitet, noch leer | {stats['empty_symbol_libraries']} |",
        f"| erkannte Hauptsymbole | {stats['symbols']} |",
        f"| Footprintbibliotheken | {stats['footprint_libraries']} |",
        f"| Footprints | {stats['footprints']} |",
        f"| Validator-Fehler | {len(errors)} |",
        f"| Validator-Hinweise | {len(warnings)} |",
        "",
        "## Footprint-Richtlinien",
        "",
        "Die Richtlinie wird pro befüllter Symbolbibliothek ausgewertet. Fehlt das Feld `Footprint Policy`, gilt `optional`.",
        "",
        "| Richtlinie | Anzahl | Bedeutung |",
        "|---|---:|---|",
        f"| `required` | {policies.get('required', 0)} | Footprint ist verpflichtend |",
        f"| `optional` | {policies.get('optional', 0)} | Footprint darf fehlen |",
        f"| `none` | {policies.get('none', 0)} | kein Footprint vorgesehen |",
        "",
        "## Footprint-Zuordnungen",
        "",
        f"- Symbole mit eingetragener Footprint-Zuordnung: **{stats['assigned_footprints']}**",
        f"- Symbole ohne Footprint-Zuordnung: **{stats['unassigned_footprints']}**",
        "",
        "Ein fehlender Footprint ist kein Qualitätsfehler, solange die Richtlinie nicht `required` lautet.",
        "",
        "## Validator-Ergebnis",
        "",
    ]

    if not errors:
        lines.append("- ✅ Keine blockierenden Fehler gefunden.")
    else:
        lines.append("### Fehler")
        lines.append("")
        for item in errors:
            lines.append(f"- ❌ `{item.code}` `{item.path}` — {item.message}")

    if warnings:
        lines.extend(["", "### Hinweise", ""])
        for item in warnings:
            lines.append(f"- ⚠️ `{item.code}` `{item.path}` — {item.message}")
    else:
        lines.extend(["", "- ✅ Keine zusätzlichen Hinweise."])

    lines.extend(
        [
            "",
            "## Einordnung",
            "",
            "Der Bericht beschreibt den technischen Ausbauzustand. Ein vorbereitetes Symbol, eine leere Bibliothek oder ein bewusst nicht verwendeter Footprint ist nicht automatisch ein Fehler.",
            "",
        ]
    )
    return "\n".join(lines)


def generated_content() -> str:
    return render_quality_report(collect_statistics())


def check_report(expected: str) -> bool:
    actual = REPORT_PATH.read_text(encoding="utf-8") if REPORT_PATH.is_file() else ""
    if actual == expected:
        print("Der Bibliotheks-Qualitätsbericht ist aktuell.")
        return True
    print("Der Bibliotheks-Qualitätsbericht ist nicht aktuell.", file=sys.stderr)
    print("Bitte den Generator ohne --check ausführen.", file=sys.stderr)
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="nur prüfen, ob der Bericht aktuell ist")
    args = parser.parse_args()
    content = generated_content()
    if args.check:
        return 0 if check_report(content) else 1
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(content, encoding="utf-8")
    print(f"Erzeugt: {REPORT_PATH.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
