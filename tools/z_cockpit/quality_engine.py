from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from .library_browser import SymbolLibrary, collect_symbol_libraries

Severity = Literal["ok", "warning", "error"]


@dataclass(frozen=True)
class QualityIssue:
    check_id: str
    severity: Severity
    message_de: str
    symbol_reference: str


@dataclass(frozen=True)
class LibraryQualityResult:
    library_name: str
    score: int
    status: Severity
    checks_total: int
    checks_passed: int
    warning_count: int
    error_count: int
    issues: tuple[QualityIssue, ...]


def _issue(check_id: str, severity: Severity, message_de: str, reference: str) -> QualityIssue:
    return QualityIssue(check_id, severity, message_de, reference)


def evaluate_library(library: SymbolLibrary) -> LibraryQualityResult:
    """Bewertet eine Bibliothek deterministisch anhand vorhandener Zuordnungen und Vorschauen."""
    issues: list[QualityIssue] = []
    passed = 0
    checks_per_symbol = 5

    for symbol in library.symbols:
        reference = symbol.reference

        if symbol.device_count:
            passed += 1
        else:
            issues.append(_issue("device_mapping", "warning", "Keine Gerätezuordnung vorhanden.", reference))

        if symbol.footprint_available:
            passed += 1
        else:
            issues.append(_issue("footprint_exists", "error", "Zugeordnete Footprintdatei fehlt.", reference))

        if symbol.symbol_preview_available:
            passed += 1
        else:
            issues.append(_issue("symbol_preview", "warning", "Symbolvorschau fehlt.", reference))

        if symbol.footprint_preview_available:
            passed += 1
        else:
            issues.append(_issue("footprint_preview", "warning", "Footprintvorschau fehlt.", reference))

        if symbol.symbol_preview_available and symbol.footprint_preview_available:
            passed += 1
        else:
            issues.append(_issue("complete_preview_pair", "warning", "Vollständiges Vorschaupaar fehlt.", reference))

    total = library.symbol_count * checks_per_symbol
    score = 100 if total == 0 else round(passed * 100 / total)
    errors = sum(issue.severity == "error" for issue in issues)
    warnings = sum(issue.severity == "warning" for issue in issues)
    status: Severity = "error" if errors else "warning" if warnings else "ok"

    return LibraryQualityResult(
        library_name=library.name,
        score=score,
        status=status,
        checks_total=total,
        checks_passed=passed,
        warning_count=warnings,
        error_count=errors,
        issues=tuple(issues),
    )


def evaluate_libraries(
    libraries: tuple[SymbolLibrary, ...] | None = None,
) -> tuple[LibraryQualityResult, ...]:
    """Bewertet alle Bibliotheken in stabiler alphabetischer Reihenfolge."""
    source = collect_symbol_libraries() if libraries is None else libraries
    return tuple(evaluate_library(library) for library in sorted(source, key=lambda item: item.name))
