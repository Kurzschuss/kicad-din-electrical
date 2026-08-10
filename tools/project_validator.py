#!/usr/bin/env python3
"""Aggregiert die projektweiten Konsistenzprüfungen von ProjectOS.

Der Validator verändert keine Repositorydateien. Er bündelt vorhandene
Single-Source-of-Truth-Prüfungen und Generatorverträge in einen stabilen,
maschinenlesbaren Projektbericht.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
from pathlib import Path
import sys
from typing import Callable, Literal

from tools.generate_device_catalog_html import (
    OUTPUT_PATH as DEVICE_CATALOG_HTML_PATH,
    generated_content as generated_device_catalog_html,
)
from tools.generate_device_variants import (
    check_files as generated_variants_are_current,
    generated_files as generated_variant_files,
)
from tools.generate_html_reference import (
    OUTPUT_PATH as HTML_REFERENCE_PATH,
    generated_content as generated_html_reference,
)
from tools.generate_library_reference import generated_files as generated_reference_files
from tools.generate_quality_report import (
    REPORT_PATH as QUALITY_REPORT_PATH,
    generated_content as generated_quality_report,
)
from tools.generate_symbol_previews import (
    check_previews,
    generated_files as generated_preview_files,
)
from tools.validate_device_catalog import REPO_ROOT, catalog_files, validate_catalog
from tools.validate_libraries import validate_repository
from tools.z_cockpit.pages import DEFAULT_PAGES
from tools.z_cockpit.project_model import load_project_state

Status = Literal["ok", "warning", "error"]


@dataclass(frozen=True)
class ProjectCheckResult:
    check_id: str
    area: str
    label_de: str
    status: Status
    message_de: str
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class ProjectValidationReport:
    checks: tuple[ProjectCheckResult, ...]

    @property
    def checks_total(self) -> int:
        return len(self.checks)

    @property
    def checks_passed(self) -> int:
        return sum(item.status != "error" for item in self.checks)

    @property
    def warning_count(self) -> int:
        return sum(item.status == "warning" for item in self.checks)

    @property
    def error_count(self) -> int:
        return sum(item.status == "error" for item in self.checks)

    @property
    def status(self) -> Status:
        if self.error_count:
            return "error"
        if self.warning_count:
            return "warning"
        return "ok"

    @property
    def successful(self) -> bool:
        return self.error_count == 0

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": 1,
            "status": self.status,
            "checks_total": self.checks_total,
            "checks_passed": self.checks_passed,
            "warning_count": self.warning_count,
            "error_count": self.error_count,
            "checks": [asdict(item) for item in self.checks],
        }


def _relative(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _file_matches(path: Path, expected: str) -> bool:
    return path.is_file() and path.read_text(encoding="utf-8") == expected


def _outdated_paths(files: dict[Path, str]) -> tuple[str, ...]:
    return tuple(
        _relative(path)
        for path, expected in files.items()
        if not _file_matches(path, expected)
    )


def _ok(check_id: str, area: str, label: str, message: str) -> ProjectCheckResult:
    return ProjectCheckResult(check_id, area, label, "ok", message)


def _warning(
    check_id: str,
    area: str,
    label: str,
    message: str,
    details: tuple[str, ...] = (),
) -> ProjectCheckResult:
    return ProjectCheckResult(check_id, area, label, "warning", message, details)


def _error(
    check_id: str,
    area: str,
    label: str,
    message: str,
    details: tuple[str, ...] = (),
) -> ProjectCheckResult:
    return ProjectCheckResult(check_id, area, label, "error", message, details)


def check_project_model() -> ProjectCheckResult:
    check_id, area, label = "PRJ-001", "project_state", "Projektmodell"
    try:
        state = load_project_state()
    except (OSError, ValueError) as exc:
        return _error(check_id, area, label, "Projektmodell ist nicht konsistent.", (str(exc),))
    task_count = sum(len(milestone.tasks) for milestone in state.milestones)
    return _ok(
        check_id,
        area,
        label,
        f"Projektmodell ist gültig: {len(state.milestones)} Meilensteine, {task_count} Aufgaben.",
    )


def check_library_validation() -> ProjectCheckResult:
    check_id, area, label = "PRJ-002", "libraries", "KiCad-Bibliotheken"
    try:
        report = validate_repository()
    except (OSError, ValueError) as exc:
        return _error(check_id, area, label, "Bibliotheksprüfung konnte nicht ausgeführt werden.", (str(exc),))
    if report.errors:
        return _error(
            check_id,
            area,
            label,
            f"Bibliotheksvalidator meldet {len(report.errors)} blockierende Fehler.",
            tuple(f"{item.code} {item.path}: {item.message}" for item in report.errors),
        )
    if report.warnings:
        return _warning(
            check_id,
            area,
            label,
            f"Bibliotheken sind konsistent; {len(report.warnings)} nicht blockierende Hinweise bleiben offen.",
            tuple(f"{item.code} {item.path}: {item.message}" for item in report.warnings),
        )
    return _ok(check_id, area, label, "Bibliotheksvalidator meldet keine Fehler oder Hinweise.")


def check_device_catalog() -> ProjectCheckResult:
    check_id, area, label = "PRJ-003", "device_catalog", "Gerätekatalog"
    try:
        errors = validate_catalog()
        count = len(catalog_files())
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return _error(check_id, area, label, "Gerätekatalog konnte nicht geprüft werden.", (str(exc),))
    if errors:
        return _error(
            check_id,
            area,
            label,
            f"Gerätekatalog enthält {len(errors)} Fehler.",
            tuple(errors),
        )
    return _ok(check_id, area, label, f"Gerätekatalog ist konsistent: {count} Gerätedateien.")


def check_generated_variants() -> ProjectCheckResult:
    check_id, area, label = "PRJ-004", "generators", "Generierte Gerätevarianten"
    try:
        files = generated_variant_files()
        current = generated_variants_are_current(files)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return _error(check_id, area, label, "Gerätevarianten konnten nicht geprüft werden.", (str(exc),))
    if not current:
        return _error(check_id, area, label, "Generierte Gerätevarianten fehlen oder sind nicht aktuell.")
    return _ok(check_id, area, label, f"{len(files)} generierte Gerätevarianten sind aktuell.")


def check_library_reference() -> ProjectCheckResult:
    check_id, area, label = "PRJ-005", "generated_docs", "Bibliotheksreferenz"
    try:
        outdated = _outdated_paths(generated_reference_files())
    except (OSError, ValueError) as exc:
        return _error(check_id, area, label, "Bibliotheksreferenz konnte nicht geprüft werden.", (str(exc),))
    if outdated:
        return _error(check_id, area, label, "Generierte Bibliotheksreferenz ist nicht aktuell.", outdated)
    return _ok(check_id, area, label, "Symbol- und Footprintindex entsprechen dem Generatorstand.")


def check_quality_report() -> ProjectCheckResult:
    check_id, area, label = "PRJ-006", "generated_docs", "Qualitätsbericht"
    try:
        current = _file_matches(QUALITY_REPORT_PATH, generated_quality_report())
    except (OSError, ValueError) as exc:
        return _error(check_id, area, label, "Qualitätsbericht konnte nicht geprüft werden.", (str(exc),))
    if not current:
        return _error(
            check_id,
            area,
            label,
            "Generierter Bibliotheks-Qualitätsbericht ist nicht aktuell.",
            (_relative(QUALITY_REPORT_PATH),),
        )
    return _ok(check_id, area, label, "Bibliotheks-Qualitätsbericht entspricht dem Generatorstand.")


def check_symbol_previews() -> ProjectCheckResult:
    check_id, area, label = "PRJ-007", "previews", "Symbolvorschauen"
    try:
        files = generated_preview_files()
        current = check_previews(files)
    except (OSError, ValueError) as exc:
        return _error(check_id, area, label, "Symbolvorschauen konnten nicht geprüft werden.", (str(exc),))
    if not current:
        return _error(check_id, area, label, "Symbolvorschauen fehlen oder sind nicht aktuell.")
    return _ok(check_id, area, label, f"{len(files)} Symbolvorschauen entsprechen dem Generatorstand.")


def check_html_reference() -> ProjectCheckResult:
    check_id, area, label = "PRJ-008", "generated_html", "HTML-Bibliotheksreferenz"
    try:
        current = _file_matches(HTML_REFERENCE_PATH, generated_html_reference())
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return _error(check_id, area, label, "HTML-Bibliotheksreferenz konnte nicht geprüft werden.", (str(exc),))
    if not current:
        return _error(
            check_id,
            area,
            label,
            "HTML-Bibliotheksreferenz ist nicht aktuell.",
            (_relative(HTML_REFERENCE_PATH),),
        )
    return _ok(check_id, area, label, "HTML-Bibliotheksreferenz entspricht dem Generatorstand.")


def check_device_catalog_html() -> ProjectCheckResult:
    check_id, area, label = "PRJ-009", "generated_html", "HTML-Gerätekatalog"
    try:
        current = _file_matches(DEVICE_CATALOG_HTML_PATH, generated_device_catalog_html())
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return _error(check_id, area, label, "HTML-Gerätekatalog konnte nicht geprüft werden.", (str(exc),))
    if not current:
        return _error(
            check_id,
            area,
            label,
            "HTML-Gerätekatalog ist nicht aktuell.",
            (_relative(DEVICE_CATALOG_HTML_PATH),),
        )
    return _ok(check_id, area, label, "HTML-Gerätekatalog entspricht dem Generatorstand.")


def check_cockpit_page_registry() -> ProjectCheckResult:
    check_id, area, label = "PRJ-010", "z_cockpit", "Z_Cockpit-Seitenmodell"
    page_ids = [page.page_id for page in DEFAULT_PAGES]
    duplicates = sorted({page_id for page_id in page_ids if page_ids.count(page_id) > 1})
    required = {"start", "geraete", "bibliotheken", "qualitaet", "sicherheit"}
    implemented = {page.page_id for page in DEFAULT_PAGES if page.implemented}
    missing = sorted(required - implemented)
    details: list[str] = []
    if duplicates:
        details.append("Doppelte Seiten-IDs: " + ", ".join(duplicates))
    if missing:
        details.append("Erwartete umgesetzte Seiten fehlen: " + ", ".join(missing))
    if details:
        return _error(check_id, area, label, "Z_Cockpit-Seitenregistrierung ist nicht konsistent.", tuple(details))
    return _ok(
        check_id,
        area,
        label,
        f"Z_Cockpit-Seitenregistrierung ist konsistent: {len(DEFAULT_PAGES)} Seiten, {len(implemented)} umgesetzt.",
    )


_DEFAULT_CHECKS: tuple[Callable[[], ProjectCheckResult], ...] = (
    check_project_model,
    check_library_validation,
    check_device_catalog,
    check_generated_variants,
    check_library_reference,
    check_quality_report,
    check_symbol_previews,
    check_html_reference,
    check_device_catalog_html,
    check_cockpit_page_registry,
)


def validate_project(
    checks: tuple[Callable[[], ProjectCheckResult], ...] = _DEFAULT_CHECKS,
) -> ProjectValidationReport:
    """Führt alle Projektprüfungen in stabiler Reihenfolge aus."""
    return ProjectValidationReport(tuple(check() for check in checks))


def _print_report(report: ProjectValidationReport) -> None:
    print("ProjectOS Projektvalidator")
    print(
        f"Prüfungen: {report.checks_passed}/{report.checks_total} bestanden · "
        f"Warnungen: {report.warning_count} · Fehler: {report.error_count}"
    )
    for item in report.checks:
        marker = {"ok": "OK", "warning": "WARN", "error": "ERROR"}[item.status]
        print(f"[{marker}] {item.check_id} {item.label_de}: {item.message_de}")
        for detail in item.details:
            print(f"  - {detail}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--json-output",
        type=Path,
        help="maschinenlesbaren Bericht zusätzlich als JSON schreiben",
    )
    args = parser.parse_args()
    report = validate_project()
    _print_report(report)
    if args.json_output is not None:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(
            json.dumps(report.to_dict(), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"JSON-Bericht: {_relative(args.json_output)}")
    return 0 if report.successful else 1


if __name__ == "__main__":
    raise SystemExit(main())
