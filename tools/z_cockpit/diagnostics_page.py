from __future__ import annotations

from dataclasses import dataclass
from html import escape
import json
from typing import Any

from .quality_engine import LibraryQualityResult, evaluate_libraries

_SEVERITY_LABELS = {"error": "Fehler", "warning": "Warnung"}
_SEVERITY_ORDER = {"error": 0, "warning": 1}

_LIBRARY_ACTIONS = {
    "device_mapping": "Gerätezuordnung im technischen Gerätekatalog prüfen oder bewusst als nicht zugeordnet dokumentieren.",
    "footprint_exists": "Footprint-Zuordnung und referenzierte Footprintdatei prüfen; fehlende Datei ergänzen oder Zuordnung korrigieren.",
    "symbol_preview": "Symbolvorschauen mit dem vorgesehenen Generator neu erzeugen und den Generatorstand prüfen.",
    "footprint_preview": "Footprintvorschau bzw. Footprint-Geometrie prüfen und anschließend die Vorschau neu erzeugen.",
    "complete_preview_pair": "Symbol- und Footprintvorschau gemeinsam prüfen, bis ein vollständiges Vorschaupaar vorhanden ist.",
}


@dataclass(frozen=True)
class DiagnosticEntry:
    severity: str
    source: str
    code: str
    area: str
    reference: str
    message_de: str
    action_de: str
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class DiagnosticsSnapshot:
    entries: tuple[DiagnosticEntry, ...]
    project_checks_total: int
    project_checks_passed: int
    library_checks_total: int
    library_checks_passed: int

    @property
    def error_count(self) -> int:
        return sum(item.severity == "error" for item in self.entries)

    @property
    def warning_count(self) -> int:
        return sum(item.severity == "warning" for item in self.entries)

    @property
    def issue_count(self) -> int:
        return len(self.entries)

    @property
    def status(self) -> str:
        if self.error_count:
            return "error"
        if self.warning_count:
            return "warning"
        return "ok"


def _project_action(item: Any) -> str:
    if item.status == "error":
        return (
            "Betroffenen Prüfbereich mit dem zugehörigen Fachvalidator oder Generator korrigieren "
            "und anschließend den ProjectOS-Projektvalidator erneut ausführen."
        )
    return (
        "Hinweis im betroffenen Prüfbereich fachlich bewerten. Nicht blockierende Warnungen nur "
        "nach nachvollziehbarer Klärung beseitigen oder dokumentieren."
    )


def collect_diagnostics(
    *,
    project_report: Any | None = None,
    library_results: tuple[LibraryQualityResult, ...] | None = None,
) -> DiagnosticsSnapshot:
    """Führt vorhandene ProjectOS- und Bibliotheksbefunde read-only zusammen."""
    if project_report is None:
        from tools.project_validator import validate_project

        project_report = validate_project()
    libraries = evaluate_libraries() if library_results is None else library_results

    entries: list[DiagnosticEntry] = []
    for item in project_report.checks:
        if item.status not in {"warning", "error"}:
            continue
        entries.append(
            DiagnosticEntry(
                severity=item.status,
                source="Projektvalidator",
                code=item.check_id,
                area=item.area,
                reference=item.label_de,
                message_de=item.message_de,
                action_de=_project_action(item),
                details=tuple(item.details),
            )
        )

    for library in libraries:
        for issue in library.issues:
            entries.append(
                DiagnosticEntry(
                    severity=issue.severity,
                    source="Bibliotheksqualität",
                    code=f"LIB-{issue.check_id}",
                    area=library.library_name,
                    reference=issue.symbol_reference,
                    message_de=issue.message_de,
                    action_de=_LIBRARY_ACTIONS.get(
                        issue.check_id,
                        "Bibliotheksbefund prüfen und über die zuständige Datenquelle oder den zuständigen Generator korrigieren.",
                    ),
                )
            )

    entries.sort(
        key=lambda item: (
            _SEVERITY_ORDER.get(item.severity, 9),
            item.source.casefold(),
            item.area.casefold(),
            item.reference.casefold(),
            item.code.casefold(),
        )
    )
    return DiagnosticsSnapshot(
        entries=tuple(entries),
        project_checks_total=project_report.checks_total,
        project_checks_passed=project_report.checks_passed,
        library_checks_total=sum(item.checks_total for item in libraries),
        library_checks_passed=sum(item.checks_passed for item in libraries),
    )


def _options(values: tuple[str, ...]) -> str:
    return "".join(f'<option value="{escape(value, quote=True)}">{escape(value)}</option>' for value in values)


def _entry_template(item: DiagnosticEntry, index: int) -> str:
    details = "".join(f"<li>{escape(detail)}</li>" for detail in item.details)
    details_html = (
        f'<div class="diagnostic-detail-block"><h3>Details</h3><ul>{details}</ul></div>'
        if details
        else '<div class="diagnostic-detail-block"><h3>Details</h3><p>Keine zusätzlichen Detaildaten.</p></div>'
    )
    return (
        f'<template id="diagnostic-inspector-{index}">'
        '<div class="diagnostic-inspector-fixed">'
        '<dl class="diagnostic-properties">'
        f'<dt>Status</dt><dd><strong>{escape(_SEVERITY_LABELS[item.severity])}</strong></dd>'
        f'<dt>Quelle</dt><dd>{escape(item.source)}</dd>'
        f'<dt>Prüfcode</dt><dd><code>{escape(item.code)}</code></dd>'
        f'<dt>Bereich</dt><dd>{escape(item.area)}</dd>'
        f'<dt>Referenz</dt><dd><code>{escape(item.reference)}</code></dd>'
        '</dl>'
        '<h3>Befund</h3>'
        f'<p>{escape(item.message_de)}</p>'
        '<h3>Empfohlene Aktion</h3>'
        f'<p>{escape(item.action_de)}</p>'
        '</div>'
        f'{details_html}'
        '</template>'
    )


def diagnostics_page_html(snapshot: DiagnosticsSnapshot | None = None) -> str:
    """Rendert eine statische, read-only Diagnose-Arbeitsliste für Z_Cockpit."""
    state = collect_diagnostics() if snapshot is None else snapshot
    sources = tuple(sorted({item.source for item in state.entries}, key=str.casefold))
    areas = tuple(sorted({item.area for item in state.entries}, key=str.casefold))
    severities = tuple(
        label for severity, label in (("error", "Fehler"), ("warning", "Warnung"))
        if any(item.severity == severity for item in state.entries)
    )

    rows: list[str] = []
    templates: list[str] = []
    for index, item in enumerate(state.entries):
        rows.append(
            f'<tr class="diagnostic-row" tabindex="0" data-index="{index}" '
            f'data-severity="{escape(_SEVERITY_LABELS[item.severity], quote=True)}" '
            f'data-source="{escape(item.source, quote=True)}" '
            f'data-area="{escape(item.area, quote=True)}">'
            f'<td><span class="diagnostic-badge diagnostic-{item.severity}">{escape(_SEVERITY_LABELS[item.severity])}</span></td>'
            f'<td>{escape(item.source)}</td>'
            f'<td><code>{escape(item.code)}</code></td>'
            f'<td>{escape(item.area)}</td>'
            f'<td><code>{escape(item.reference)}</code></td>'
            f'<td>{escape(item.message_de)}</td></tr>'
        )
        templates.append(_entry_template(item, index))

    if rows:
        table_rows = "".join(rows)
    else:
        table_rows = (
            '<tr class="diagnostic-empty-row"><td colspan="6">'
            'Keine Fehler oder Warnungen aus den eingebundenen Repository-Prüfungen.</td></tr>'
        )

    status_label = {"ok": "OK", "warning": "Warnungen", "error": "Fehler"}[state.status]
    info_payload = escape(
        json.dumps(
            {
                "project_checks": [state.project_checks_passed, state.project_checks_total],
                "library_checks": [state.library_checks_passed, state.library_checks_total],
            },
            ensure_ascii=False,
        ),
        quote=True,
    )

    return (
        '<style>'
        '#page-diagnose.active{position:absolute;inset:0;display:flex;flex-direction:column;min-height:0;overflow:hidden;padding:0}'
        '.diagnostic-workspace{display:grid;grid-template-columns:minmax(0,1fr) 380px;height:100%;min-height:0;overflow:hidden}'
        '.diagnostic-main{min-width:0;min-height:0;padding:1rem;display:flex;flex-direction:column;overflow:hidden}'
        '.diagnostic-title{margin:0 0 .25rem;flex:0 0 auto}'
        '.diagnostic-subtitle{margin:.1rem 0 .75rem;opacity:.78;flex:0 0 auto}'
        '.diagnostic-summary{display:grid;grid-template-columns:repeat(5,minmax(125px,1fr));gap:.7rem;margin-bottom:.8rem;flex:0 0 auto}'
        '.diagnostic-summary .card{padding:.7rem}.diagnostic-summary .card strong{font-size:1.35rem}'
        '.diagnostic-filters{display:grid;grid-template-columns:repeat(3,minmax(130px,1fr));gap:.6rem;margin-bottom:.8rem;flex:0 0 auto}'
        '.diagnostic-table-wrap{flex:1 1 auto;min-height:0;overflow:auto;border:1px solid #8886}'
        '.diagnostic-table{border-collapse:collapse;width:100%;min-width:980px}'
        '.diagnostic-table th,.diagnostic-table td{padding:.5rem .6rem;border-bottom:1px solid #8884;text-align:left;white-space:nowrap}'
        '.diagnostic-table td:last-child{white-space:normal;min-width:300px}'
        '.diagnostic-table thead th{position:sticky;top:0;background:Canvas;z-index:1}'
        '.diagnostic-row{cursor:pointer}'
        '.diagnostic-row:hover{background:#2878c812}'
        '.diagnostic-row.selected{background:#2878c81f;font-weight:600}'
        '.diagnostic-badge{display:inline-block;padding:.18rem .42rem;border-radius:999px;font-weight:700;font-size:.8rem}'
        '.diagnostic-error{border:1px solid #b33a3a}.diagnostic-warning{border:1px solid #c58a00}'
        '.diagnostic-result-count{margin:.65rem 0 0;font-size:.9rem;opacity:.8;flex:0 0 auto}'
        '.diagnostic-inspector{min-width:0;min-height:0;height:100%;padding:1rem;display:flex;flex-direction:column;overflow:hidden;border-left:1px solid #8886}'
        '.diagnostic-inspector>h2{margin-top:0;flex:0 0 auto}'
        '#diagnostic-inspector-content{min-height:0;flex:1 1 auto;overflow:auto;scrollbar-gutter:stable}'
        '.diagnostic-properties{display:grid;grid-template-columns:1fr 1.4fr;gap:.45rem .7rem;margin:0 0 1rem}'
        '.diagnostic-properties dt{font-weight:700}.diagnostic-properties dd{margin:0;min-width:0;overflow-wrap:anywhere}'
        '.diagnostic-inspector-fixed h3,.diagnostic-detail-block h3{margin:.85rem 0 .35rem}'
        '.diagnostic-detail-block ul{padding-left:1.2rem}.diagnostic-detail-block li{margin:.35rem 0;overflow-wrap:anywhere}'
        '.diagnostic-readonly-note{padding:.7rem;border:1px solid #2878c866;border-left:5px solid #2878c8;border-radius:.4rem;margin:.1rem 0 .8rem;flex:0 0 auto}'
        '@media(max-width:1050px){.diagnostic-workspace{grid-template-columns:1fr}.diagnostic-inspector{height:auto;max-height:40vh;border-left:0;border-top:1px solid #8886}.diagnostic-summary{grid-template-columns:repeat(2,minmax(120px,1fr))}.diagnostic-filters{grid-template-columns:1fr}}'
        '</style>'
        f'<section class="page" id="page-diagnose" data-check-counts="{info_payload}">'
        '<div class="diagnostic-workspace"><div class="diagnostic-main">'
        '<h2 class="diagnostic-title">Diagnose</h2>'
        '<p class="diagnostic-subtitle">Arbeitsliste aus ProjectOS-Projektvalidator und Bibliotheks-Quality-Engine.</p>'
        '<div class="diagnostic-readonly-note"><strong>Read-only:</strong> Die Diagnose zeigt vorhandene Befunde und führt keine automatische Reparatur aus. Laufzeit-Wissensgraphdiagnosen werden erst angezeigt, wenn eine persistierte Projektinstanz angebunden ist.</div>'
        '<div class="diagnostic-summary">'
        f'<div class="card">Gesamtstatus<strong>{status_label}</strong></div>'
        f'<div class="card">Befunde<strong>{state.issue_count}</strong></div>'
        f'<div class="card">Fehler<strong>{state.error_count}</strong></div>'
        f'<div class="card">Warnungen<strong>{state.warning_count}</strong></div>'
        f'<div class="card">Projektprüfungen<strong>{state.project_checks_passed}/{state.project_checks_total}</strong></div>'
        '</div>'
        '<div class="diagnostic-filters">'
        f'<label>Status<select id="diagnostic-filter-severity"><option value="">Alle</option>{_options(severities)}</select></label>'
        f'<label>Quelle<select id="diagnostic-filter-source"><option value="">Alle</option>{_options(sources)}</select></label>'
        f'<label>Bereich<select id="diagnostic-filter-area"><option value="">Alle</option>{_options(areas)}</select></label>'
        '</div>'
        '<div class="diagnostic-table-wrap"><table class="diagnostic-table" id="diagnostic-overview">'
        '<thead><tr><th>Status</th><th>Quelle</th><th>Code</th><th>Bereich</th><th>Referenz</th><th>Befund</th></tr></thead>'
        f'<tbody>{table_rows}</tbody></table></div>'
        f'<p class="diagnostic-result-count" id="diagnostic-result-count">{state.issue_count} Befund(e) · Bibliotheksprüfungen {state.library_checks_passed}/{state.library_checks_total}</p>'
        '</div><section class="diagnostic-inspector"><h2>Details</h2>'
        '<div id="diagnostic-inspector-content"><p>Befund auswählen.</p></div></section>'
        f'{"".join(templates)}</div></section>'
        '<script type="text/javascript">(()=>{'
        'const table=document.getElementById("diagnostic-overview");if(!table)return;'
        'const rows=[...table.querySelectorAll(".diagnostic-row")];'
        'const inspector=document.getElementById("diagnostic-inspector-content");'
        'const count=document.getElementById("diagnostic-result-count");'
        'const severity=document.getElementById("diagnostic-filter-severity");'
        'const source=document.getElementById("diagnostic-filter-source");'
        'const area=document.getElementById("diagnostic-filter-area");'
        'let selected=null;'
        'function selectRow(row){rows.forEach(item=>item.classList.remove("selected"));row.classList.add("selected");selected=row;'
        'const tpl=document.getElementById(`diagnostic-inspector-${row.dataset.index}`);inspector.replaceChildren(tpl.content.cloneNode(true));}'
        'function apply(){let visible=0;rows.forEach(row=>{const show=(!severity.value||row.dataset.severity===severity.value)&&(!source.value||row.dataset.source===source.value)&&(!area.value||row.dataset.area===area.value);row.hidden=!show;if(show)visible++;});'
        'count.textContent=`${visible} Befund(e)`;if(selected&&selected.hidden){selected.classList.remove("selected");selected=null;inspector.innerHTML="<p>Befund auswählen.</p>";}'
        'const first=rows.find(row=>!row.hidden);if(!selected&&first)selectRow(first);}'
        '[severity,source,area].forEach(filter=>filter.addEventListener("change",apply));'
        'rows.forEach(row=>{row.addEventListener("click",()=>selectRow(row));row.addEventListener("keydown",event=>{if(event.key==="Enter"||event.key===" "){event.preventDefault();selectRow(row);}});});'
        'apply();})();</script>'
    )
