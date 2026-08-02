#!/usr/bin/env python3
"""Validiert die grundlegende Konsistenz der KiCad-Bibliotheken."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
SYMBOL_ROOT = REPO_ROOT / "symbols" / "DIN_Electrical_Symbols"
FOOTPRINT_ROOT = REPO_ROOT / "footprints"

PROPERTY_RE = re.compile(r'\(property\s+"((?:\\.|[^"\\])*)"\s+"((?:\\.|[^"\\])*)"')
FOOTPRINT_NAME_RE = re.compile(r'^\(footprint\s+"((?:\\.|[^"\\])*)"')
TOP_LEVEL_SYMBOL_RE = re.compile(r'^\s{2}\(symbol\s+"((?:\\.|[^"\\])*)"', re.MULTILINE)


def _unescape(value: str) -> str:
    return value.replace('\\"', '"').replace('\\\\', '\\')


@dataclass(frozen=True)
class Finding:
    level: str
    code: str
    path: str
    message: str


@dataclass
class ValidationReport:
    findings: list[Finding] = field(default_factory=list)

    def error(self, code: str, path: Path, message: str) -> None:
        self.findings.append(Finding("ERROR", code, _display(path), message))

    def warning(self, code: str, path: Path, message: str) -> None:
        self.findings.append(Finding("WARNING", code, _display(path), message))

    @property
    def errors(self) -> list[Finding]:
        return [item for item in self.findings if item.level == "ERROR"]

    @property
    def warnings(self) -> list[Finding]:
        return [item for item in self.findings if item.level == "WARNING"]


def _display(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def symbol_properties(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    return {_unescape(name): _unescape(value) for name, value in PROPERTY_RE.findall(text)}


def symbol_names(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    return sorted({_unescape(name) for name in TOP_LEVEL_SYMBOL_RE.findall(text)}, key=str.casefold)


def footprint_name(path: Path) -> str | None:
    first_line = path.read_text(encoding="utf-8").splitlines()[0] if path.is_file() else ""
    match = FOOTPRINT_NAME_RE.match(first_line)
    return _unescape(match.group(1)) if match else None


def validate_symbol_library(path: Path, report: ValidationReport, footprint_root: Path) -> None:
    expected_pretty = footprint_root / f"{path.stem}.pretty"
    if not expected_pretty.is_dir():
        report.error("SYM001", path, f"Gleichnamige Footprintbibliothek {expected_pretty.name} fehlt.")

    names = symbol_names(path)
    if not names:
        report.warning("SYM100", path, "Symbolbibliothek ist vorbereitet, aber noch leer.")
        return

    props = symbol_properties(path)
    description = props.get("Description", "").strip()
    footprint = props.get("Footprint", "").strip()
    datasheet = props.get("Datasheet", "").strip()
    manufacturer = props.get("Manufacturer", "").strip()

    if not description:
        report.warning("SYM101", path, "Beschreibung fehlt.")
    if not datasheet:
        report.warning("SYM102", path, "Datenblatt ist noch nicht hinterlegt.")
    if not manufacturer:
        report.warning("SYM103", path, "Hersteller ist noch nicht hinterlegt.")

    if not footprint:
        report.warning("SYM104", path, "Standard-Footprint ist noch nicht zugeordnet.")
        return

    if ":" not in footprint:
        report.error("SYM002", path, f"Footprint-ID '{footprint}' ist nicht vollständig qualifiziert.")
        return

    library_name, footprint_id = footprint.split(":", 1)
    target = footprint_root / f"{library_name}.pretty" / f"{footprint_id}.kicad_mod"
    if not target.is_file():
        report.error("SYM003", path, f"Zugeordneter Footprint '{footprint}' existiert nicht.")


def validate_footprint(path: Path, report: ValidationReport) -> None:
    declared = footprint_name(path)
    if declared is None:
        report.error("FP001", path, "Footprintkopf konnte nicht gelesen werden.")
    elif declared != path.stem:
        report.error("FP002", path, f"Deklarierter Name '{declared}' stimmt nicht mit dem Dateinamen überein.")

    if path.parent.suffix != ".pretty":
        report.error("FP003", path, "Footprint liegt nicht in einer .pretty-Bibliothek.")


def validate_repository(symbol_root: Path = SYMBOL_ROOT, footprint_root: Path = FOOTPRINT_ROOT) -> ValidationReport:
    report = ValidationReport()

    symbol_files = sorted(symbol_root.glob("Z_*.kicad_sym"), key=lambda item: item.name.casefold())
    footprint_files = sorted(footprint_root.glob("Z_*.pretty/*.kicad_mod"), key=lambda item: item.as_posix().casefold())

    for path in symbol_files:
        validate_symbol_library(path, report, footprint_root)
    for path in footprint_files:
        validate_footprint(path, report)

    symbol_stems = {path.stem for path in symbol_files}
    for pretty in sorted(footprint_root.glob("Z_*.pretty"), key=lambda item: item.name.casefold()):
        if pretty.stem not in symbol_stems:
            report.warning("LIB100", pretty, "Footprintbibliothek besitzt derzeit keine gleichnamige Symbolbibliothek.")

    return report


def print_report(report: ValidationReport) -> None:
    print("Bibliotheks-Validator – Phase 1")
    print(f"Fehler: {len(report.errors)}")
    print(f"Hinweise: {len(report.warnings)}")
    for item in report.findings:
        print(f"[{item.level}] {item.code} {item.path}: {item.message}")


def main() -> int:
    report = validate_repository()
    print_report(report)
    return 1 if report.errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
