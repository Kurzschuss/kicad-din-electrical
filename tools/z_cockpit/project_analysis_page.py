from __future__ import annotations

from collections import defaultdict
from html import escape

from .project_analysis import AnalysisFinding, ProjectAnalysisResult, analyze_project

_STATUS_LABELS = {"ok": "OK", "warning": "Warnung", "error": "Fehler"}
_CHECK_LABELS = {
    "device_id_missing": "Fehlende Geräte-IDs",
    "device_id_duplicate": "Doppelte Geräte-IDs",
    "symbol_reference_missing": "Fehlende Symbolreferenzen",
    "symbol_reference_unknown": "Unbekannte Symbolreferenzen",
    "footprint_missing": "Fehlende Footprints",
    "symbol_preview_missing": "Fehlende Symbolvorschauen",
    "footprint_preview_missing": "Fehlende Footprintvorschauen",
    "symbol_unused": "Ungenutzte Symbole",
}


def _finding_html(finding: AnalysisFinding) -> str:
    return (
        f'<li class="analysis-finding" data-severity="{finding.severity}">'
        f'<div><strong>{_STATUS_LABELS[finding.severity]}</strong> '
        f'<code>{escape(finding.reference)}</code></div>'
        f'<p>{escape(finding.message_de)}</p>'
        f'<p class="analysis-recommendation"><strong>Empfehlung:</strong> '
        f'{escape(finding.recommendation_de)}</p></li>'
    )


def project_analysis_page_html(result: ProjectAnalysisResult | None = None) -> str:
    """Rendert die repositoryweite Konsistenzprüfung als Diagnose-Seite."""
    analysis = analyze_project() if result is None else result
    grouped: dict[str, list[AnalysisFinding]] = defaultdict(list)
    for finding in analysis.findings:
        grouped[finding.check_id].append(finding)

    groups: list[str] = []
    for check_id in sorted(grouped):
        findings = grouped[check_id]
        errors = sum(item.severity == "error" for item in findings)
        warnings = len(findings) - errors
        label = _CHECK_LABELS.get(check_id, check_id)
        groups.append(
            f'<details class="analysis-group" data-check="{escape(check_id)}">'
            f'<summary><strong>{escape(label)}</strong>'
            f'<span>{len(findings)} Befund(e) · {errors} Fehler · {warnings} Warnung(en)</span></summary>'
            f'<ul>{"".join(_finding_html(item) for item in findings)}</ul></details>'
        )

    if not groups:
        body = '<p class="analysis-complete">Keine Konsistenzprobleme gefunden.</p>'
    else:
        body = f'<div class="analysis-groups">{"".join(groups)}</div>'

    return (
        '<section class="page" id="page-diagnose"><h2>Projektanalyse</h2>'
        '<p>Repositoryweite Prüfung von Geräte-IDs, Symbolreferenzen, Footprints und Vorschauen.</p>'
        '<div class="cards analysis-summary">'
        f'<div class="card">Geräte geprüft<strong>{analysis.device_count}</strong></div>'
        f'<div class="card">Symbole geprüft<strong>{analysis.symbol_count}</strong></div>'
        f'<div class="card">Warnungen<strong>{analysis.warning_count}</strong></div>'
        f'<div class="card">Fehler<strong>{analysis.error_count}</strong></div>'
        f'<div class="card">Status<strong>{_STATUS_LABELS[analysis.status]}</strong></div>'
        f'</div>{body}</section>'
    )
