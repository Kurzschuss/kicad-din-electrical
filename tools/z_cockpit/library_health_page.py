from __future__ import annotations

from html import escape
from typing import Any

from .quality_engine import LibraryQualityResult, evaluate_libraries

_STATUS_LABELS = {"ok": "OK", "warning": "Warnung", "error": "Fehler"}


def _project_validation_html(report: Any | None) -> str:
    if report is None:
        return ""
    checks = []
    for item in report.checks:
        details = "".join(f"<li>{escape(detail)}</li>" for detail in item.details)
        detail_block = f'<ul class="project-check-details">{details}</ul>' if details else ""
        checks.append(
            f'<article class="project-check" data-check="{escape(item.check_id)}" data-status="{item.status}">'
            f'<div><code>{escape(item.check_id)}</code> <strong>{escape(item.label_de)}</strong></div>'
            f'<div class="project-check-state">{_STATUS_LABELS[item.status]}</div>'
            f'<p>{escape(item.message_de)}</p>{detail_block}</article>'
        )
    return (
        f'<section class="project-validation" data-status="{report.status}"><h3>Projektkonsistenz</h3>'
        '<p>Projektweite Prüfung von Projektmodell, Bibliotheken, Katalog, Generatorständen und Cockpit-Struktur.</p>'
        '<div class="cards project-validation-summary">'
        f'<div class="card">Projektstatus<strong>{_STATUS_LABELS[report.status]}</strong></div>'
        f'<div class="card">Prüfungen<strong>{report.checks_passed}/{report.checks_total}</strong></div>'
        f'<div class="card">Warnungen<strong>{report.warning_count}</strong></div>'
        f'<div class="card">Fehler<strong>{report.error_count}</strong></div></div>'
        f'<div class="project-check-list">{"".join(checks)}</div></section>'
    )


def library_health_page_html(
    results: tuple[LibraryQualityResult, ...] | None = None,
    *,
    project_report: Any | None = None,
) -> str:
    """Rendert Projektkonsistenz und Library Quality als Cockpit-Qualitätsseite."""
    if results is None and project_report is None:
        # Lazy-Import vermeidet eine zyklische Abhängigkeit beim Laden des
        # z_cockpit-Pakets. Im echten Cockpit wird der Projektbericht automatisch
        # berechnet; Unit-Tests mit injizierten Library-Ergebnissen bleiben isoliert.
        from tools.project_validator import validate_project

        project_report = validate_project()

    items = evaluate_libraries() if results is None else results
    checks_total = sum(item.checks_total for item in items)
    checks_passed = sum(item.checks_passed for item in items)
    warnings = sum(item.warning_count for item in items)
    errors = sum(item.error_count for item in items)
    overall_score = 100 if checks_total == 0 else round(checks_passed * 100 / checks_total)

    cards: list[str] = []
    for item in items:
        issues = "".join(
            f'<li data-severity="{issue.severity}" data-check="{escape(issue.check_id)}">'
            f'<strong>{_STATUS_LABELS[issue.severity]}</strong> '
            f'<code>{escape(issue.symbol_reference)}</code>: {escape(issue.message_de)}</li>'
            for issue in item.issues
        )
        issue_block = (
            f'<ul class="quality-issues">{issues}</ul>'
            if issues
            else '<p class="quality-complete">Alle Qualitätsprüfungen bestanden.</p>'
        )
        cards.append(
            f'<details class="quality-card" data-library="{escape(item.library_name)}" '
            f'data-status="{item.status}">'
            f'<summary><strong>{escape(item.library_name)}</strong>'
            f'<span class="quality-score">{item.score} % · {_STATUS_LABELS[item.status]}</span></summary>'
            f'<div class="quality-progress" role="progressbar" aria-label="Gesundheitswert {escape(item.library_name)}" '
            f'aria-valuemin="0" aria-valuemax="100" aria-valuenow="{item.score}">'
            f'<span style="width:{item.score}%"></span></div>'
            f'<p>{item.checks_passed} von {item.checks_total} Prüfungen bestanden · '
            f'{item.warning_count} Warnung(en) · {item.error_count} Fehler</p>'
            f'{issue_block}</details>'
        )

    return (
        '<section class="page" id="page-qualitaet"><h2>Bibliotheksgesundheit</h2>'
        '<p>Bewertung aus der zentralen Quality Engine für Zuordnungen, Footprints und Vorschauen.</p>'
        f'{_project_validation_html(project_report)}'
        '<h3>Bibliotheksprüfungen</h3>'
        '<div class="cards quality-summary">'
        f'<div class="card">Gesundheitswert<strong>{overall_score} %</strong></div>'
        f'<div class="card">Prüfungen<strong>{checks_passed}/{checks_total}</strong></div>'
        f'<div class="card">Warnungen<strong>{warnings}</strong></div>'
        f'<div class="card">Fehler<strong>{errors}</strong></div></div>'
        f'<div class="quality-list">{"".join(cards)}</div></section>'
    )
