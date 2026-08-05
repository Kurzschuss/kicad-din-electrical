from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Literal, Mapping

from tools.generate_device_catalog_html import collect_devices

from .library_browser import SymbolLibrary, collect_symbol_libraries

AnalysisSeverity = Literal["warning", "error"]


@dataclass(frozen=True)
class AnalysisFinding:
    check_id: str
    severity: AnalysisSeverity
    reference: str
    message_de: str
    recommendation_de: str


@dataclass(frozen=True)
class ProjectAnalysisResult:
    device_count: int
    symbol_count: int
    checks_total: int
    warning_count: int
    error_count: int
    status: Literal["ok", "warning", "error"]
    findings: tuple[AnalysisFinding, ...]


def _finding(
    check_id: str,
    severity: AnalysisSeverity,
    reference: str,
    message_de: str,
    recommendation_de: str,
) -> AnalysisFinding:
    return AnalysisFinding(check_id, severity, reference, message_de, recommendation_de)


def analyze_project(
    devices: Iterable[Mapping[str, object]] | None = None,
    libraries: tuple[SymbolLibrary, ...] | None = None,
) -> ProjectAnalysisResult:
    """Prüft Geräte und Bibliotheken repositoryweit auf konsistente Zuordnungen."""
    source_devices = tuple(collect_devices()["devices"] if devices is None else devices)
    source_libraries = collect_symbol_libraries(devices=source_devices) if libraries is None else libraries

    symbols = {
        symbol.reference: symbol
        for library in source_libraries
        for symbol in library.symbols
    }
    findings: list[AnalysisFinding] = []
    seen_ids: set[str] = set()

    for device in source_devices:
        device_id = str(device.get("id") or "").strip()
        symbol_reference = str(device.get("symbol") or "").strip()
        reference = device_id or "<Gerät ohne ID>"

        if not device_id:
            findings.append(_finding(
                "device_id_missing",
                "error",
                reference,
                "Technische Geräte-ID fehlt.",
                "Eine eindeutige technische ID im Gerätekatalog ergänzen.",
            ))
        elif device_id in seen_ids:
            findings.append(_finding(
                "device_id_duplicate",
                "error",
                device_id,
                "Technische Geräte-ID ist mehrfach vorhanden.",
                "Die Geräte-IDs eindeutig machen.",
            ))
        else:
            seen_ids.add(device_id)

        if not symbol_reference:
            findings.append(_finding(
                "symbol_reference_missing",
                "error",
                reference,
                "Symbolreferenz fehlt.",
                "Eine Referenz im Format Bibliothek:Symbol ergänzen.",
            ))
            continue

        symbol = symbols.get(symbol_reference)
        if symbol is None:
            findings.append(_finding(
                "symbol_reference_unknown",
                "error",
                reference,
                f"Symbolreferenz {symbol_reference} ist nicht vorhanden.",
                "Symbolreferenz korrigieren oder das fehlende Symbol anlegen.",
            ))
            continue

        if not symbol.footprint_available:
            findings.append(_finding(
                "footprint_missing",
                "error",
                symbol_reference,
                "Zugeordnete Footprintdatei fehlt.",
                "Footprintzuordnung korrigieren oder die Footprintdatei ergänzen.",
            ))
        if not symbol.symbol_preview_available:
            findings.append(_finding(
                "symbol_preview_missing",
                "warning",
                symbol_reference,
                "Symbolvorschau fehlt.",
                "Symbolvorschau erzeugen und versionieren.",
            ))
        if not symbol.footprint_preview_available:
            findings.append(_finding(
                "footprint_preview_missing",
                "warning",
                symbol_reference,
                "Footprintvorschau fehlt.",
                "Footprintvorschau erzeugen und versionieren.",
            ))

    for symbol_reference, symbol in symbols.items():
        if not symbol.device_count:
            findings.append(_finding(
                "symbol_unused",
                "warning",
                symbol_reference,
                "Symbol wird von keinem Gerät verwendet.",
                "Gerätezuordnung ergänzen oder das ungenutzte Symbol dokumentieren.",
            ))

    ordered = tuple(sorted(findings, key=lambda item: (item.severity, item.check_id, item.reference)))
    errors = sum(item.severity == "error" for item in ordered)
    warnings = sum(item.severity == "warning" for item in ordered)
    status: Literal["ok", "warning", "error"] = "error" if errors else "warning" if warnings else "ok"

    return ProjectAnalysisResult(
        device_count=len(source_devices),
        symbol_count=len(symbols),
        checks_total=len(source_devices) * 5 + len(symbols),
        warning_count=warnings,
        error_count=errors,
        status=status,
        findings=ordered,
    )
