#!/usr/bin/env python3
"""Erzeugt die modulare Z_Cockpit-Ansicht aus dem Gerätekatalog."""

from __future__ import annotations

import argparse
import json
import sys

from tools.generate_device_catalog_html import collect_devices
from tools.validate_device_catalog import REPO_ROOT
from tools.z_cockpit import (
    DEFAULT_PAGES,
    collect_project_status,
    development_navigator_html,
    footprint_assignment,
    library_health_page_html,
    library_page_html,
    load_project_state,
    next_tasks_html,
    project_progress_html,
    security_page_html,
    symbol_preview,
)

OUTPUT_PATH = REPO_ROOT / "docs" / "site" / "z-cockpit.html"


def _text(value: object, suffix: str = "") -> str:
    if value is None or value == "":
        return "–"
    return f"{value}{suffix}"


def cockpit_devices() -> list[dict[str, object]]:
    result: list[dict[str, object]] = []
    for item in collect_devices()["devices"]:
        manufacturer = str(item["manufacturer"])
        symbol = str(item["symbol"])
        symbol_image = symbol_preview(symbol)
        footprint = footprint_assignment(symbol)
        result.append({
            "name": str(item.get("name_de") or item["device_type"]),
            "id": str(item["id"]),
            "family": str(item["family"]),
            "manufacturer": "Herstellerneutral" if manufacturer == "Generic" else manufacturer,
            "poles": _text(item.get("poles"), "P"),
            "curve": _text(item.get("trip_curve")),
            "current": _text(item.get("rated_current_a"), " A"),
            "symbol": symbol,
            "symbol_preview_url": symbol_image.relative_url,
            "symbol_preview_available": symbol_image.available,
            "footprint": footprint.footprint_name or str(item["footprint_policy"]),
            "footprint_preview_url": footprint.preview_relative_url,
            "footprint_preview_available": footprint.preview_available,
            "footprint_preview_status": footprint.preview_status,
            "model": False,
            "status": "Geprüft" if item.get("source_status") == "template" else "Entwurf",
        })
    return result


def cockpit_summary(devices: list[dict[str, object]]) -> dict[str, int]:
    return {
        "devices": len(devices),
        "families": len({str(item["family"]) for item in devices}),
        "manufacturers": len({str(item["manufacturer"]) for item in devices}),
        "checked": sum(item["status"] == "Geprüft" for item in devices),
    }


def navigation_html() -> str:
    return "".join(
        f'<button class="page-link" data-page="{page.page_id}" title="{page.description_de}">'
        f'{page.label_de}{"" if page.implemented else " <small>– geplant</small>"}</button>'
        for page in DEFAULT_PAGES
    )


def project_status_html() -> str:
    cards = []
    for item in collect_project_status():
        if item.status_id == "ruleset" and item.available:
            state_class, state_label, symbol = "prepared", "Vorbereitet", "●"
        elif item.available:
            state_class, state_label, symbol = "available", "Vorhanden", "✓"
        else:
            state_class, state_label, symbol = "missing", "Fehlt", "!"
        cards.append(
            f'<article class="status-card {state_class}" data-status="{item.status_id}">'
            f'<div class="status-heading"><span aria-hidden="true">{symbol}</span><strong>{item.label_de}</strong></div>'
            f'<div class="status-state">{state_label}</div><p>{item.detail_de}</p></article>'
        )
    return "".join(cards)


def placeholder_pages_html() -> str:
    return "".join(
        f'<section class="page" id="page-{page.page_id}"><h2>{page.label_de}</h2><p>{page.description_de}</p>'
        '<div class="placeholder">Dieser Bereich befindet sich im Aufbau.</div></section>'
        for page in DEFAULT_PAGES
        if page.page_id not in {"start", "geraete", "bibliotheken", "qualitaet", "sicherheit"}
    )


def render_html(devices: list[dict[str, object]]) -> str:
    payload = json.dumps(devices, ensure_ascii=False).replace("</", "<\\/")
    summary = cockpit_summary(devices)
    project = load_project_state()
    return f"""<!doctype html>
<html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Z_Cockpit</title><style>
:root{{font-family:system-ui,sans-serif;color-scheme:light dark}}*{{box-sizing:border-box}}body{{margin:0;min-height:100vh;display:grid;grid-template-rows:auto 1fr auto}}header,footer{{padding:.75rem 1rem;border-bottom:1px solid #8886}}header h1{{margin:0;font-size:1.25rem}}main{{display:grid;grid-template-columns:230px 1fr;min-height:0}}aside{{padding:1rem;border-right:1px solid #8886;overflow:auto}}.page-link{{display:block;width:100%;padding:.65rem .7rem;margin:.2rem 0;text-align:left;border:0;background:transparent;cursor:pointer;border-radius:.35rem}}.page-link.active{{background:#2878c824;font-weight:700}}.page-link small{{opacity:.65}}.workspace{{min-width:0;overflow:auto}}.page{{display:none;padding:1rem}}.page.active{{display:block}}.cards,.status-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:1rem}}.card,.status-card,.dashboard-panel,.development-navigator,.library-card,.quality-card{{border:1px solid #8886;border-radius:.5rem;padding:1rem}}.card strong{{display:block;font-size:1.8rem;margin-top:.35rem}}.dashboard-grid{{display:grid;grid-template-columns:minmax(0,2fr) minmax(260px,1fr);gap:1rem;margin-top:1.5rem}}.development-navigator{{margin-top:1rem;border-left:5px solid #2878c8}}.development-navigator h3{{margin-top:0}}.navigator-kicker{{font-weight:700;opacity:.8}}.navigator-recommendation h4{{font-size:1.2rem;margin:.55rem 0}}.navigator-blocked{{margin-top:1rem;padding-top:.75rem;border-top:1px solid #8885}}.progress-row{{display:grid;grid-template-columns:minmax(150px,1fr) minmax(160px,2fr) 4rem;gap:.75rem;align-items:center;margin:.65rem 0}}.progress-track,.quality-progress{{height:.75rem;border-radius:999px;background:#8883;overflow:hidden}}.progress-fill,.quality-progress span{{display:block;height:100%;background:currentColor}}.next-tasks{{padding-left:1.4rem}}.status-section{{margin-top:1.5rem}}.status-heading{{display:flex;gap:.55rem;align-items:center}}.status-state{{font-weight:700;margin:.65rem 0 .25rem}}.status-card.available{{border-left:5px solid #2e8b57}}.status-card.prepared{{border-left:5px solid #c58a00}}.status-card.missing{{border-left:5px solid #b33a3a}}.security-table-wrap,.library-table-wrap{{overflow:auto;margin-top:1rem;border:1px solid #8886;border-radius:.5rem}}.security-table{{min-width:760px}}.security-table th[scope="row"]{{position:static;background:transparent}}.security-table tr[data-state="vorhanden"]{{border-left:5px solid #2e8b57}}.security-table tr[data-state="vorbereitet"]{{border-left:5px solid #c58a00}}.security-table tr[data-state="laufzeitpruefung"]{{border-left:5px solid #2878c8}}.security-table tr[data-state="fehlt"]{{border-left:5px solid #b33a3a}}.security-notice{{margin-top:1rem;padding:1rem;border:1px solid #c58a0088;border-left:5px solid #c58a00;border-radius:.5rem}}.library-list,.quality-list{{display:grid;gap:1rem;margin-top:1rem}}.library-card summary,.quality-card summary{{cursor:pointer;display:flex;justify-content:space-between;gap:1rem}}.quality-card[data-status="ok"]{{border-left:5px solid #2e8b57}}.quality-card[data-status="warning"]{{border-left:5px solid #c58a00}}.quality-card[data-status="error"]{{border-left:5px solid #b33a3a}}.quality-score{{font-weight:700}}.quality-issues{{padding-left:1.3rem}}.quality-issues li{{margin:.45rem 0}}.quality-complete{{font-weight:700}}.library-table{{min-width:900px}}.device-layout{{display:grid;grid-template-columns:1fr 360px;min-height:0}}.device-main,.details{{padding:1rem;overflow:auto}}.details{{border-left:1px solid #8886}}.filters{{display:grid;grid-template-columns:repeat(6,minmax(125px,1fr));gap:.6rem;margin-bottom:.8rem}}label{{display:grid;gap:.2rem;font-size:.8rem}}select{{padding:.45rem}}.table-wrap{{overflow:auto;border:1px solid #8886}}table{{border-collapse:collapse;width:100%;min-width:1050px}}th,td{{padding:.55rem .65rem;border-bottom:1px solid #8884;text-align:left;white-space:nowrap}}th{{position:sticky;top:0;background:Canvas}}tbody tr{{cursor:pointer}}tbody tr:hover{{background:#2878c812}}tbody tr.selected{{background:#2878c81f;font-weight:700}}dl{{display:grid;grid-template-columns:1fr 1.4fr;gap:.45rem .7rem}}dt{{font-weight:700}}dd{{margin:0}}.preview-grid{{display:grid;gap:1rem;margin-top:1rem}}.preview-card{{border:1px solid #8886;border-radius:.5rem;padding:.8rem}}.preview,.placeholder{{min-height:150px;display:grid;place-items:center;border:1px dashed #8888;text-align:center;padding:1rem}}.preview img{{display:block;width:100%;max-width:280px;height:auto}}.preview-note{{margin:.6rem 0 0;font-size:.85rem;opacity:.75}}.preview-status{{font-weight:700;margin:.5rem 0 0}}footer{{border-top:1px solid #8886;border-bottom:0;display:flex;justify-content:space-between;gap:1rem}}@media(max-width:1050px){{main{{grid-template-columns:190px 1fr}}.device-layout,.dashboard-grid{{grid-template-columns:1fr}}.details{{border-left:0;border-top:1px solid #8886}}}}
</style></head><body>
<header><h1>Z_Cockpit – Bibliotheks- und Geräteübersicht</h1></header><main><aside><h2>Bereiche</h2>{navigation_html()}</aside><div class="workspace">
<section class="page active" id="page-start"><h2>Projektstatus</h2><p>Zentrale Übersicht aus Gerätekatalog und Projektmodell.</p><div class="cards"><div class="card">Geräte<strong>{summary['devices']}</strong></div><div class="card">Gerätefamilien<strong>{summary['families']}</strong></div><div class="card">Hersteller<strong>{summary['manufacturers']}</strong></div><div class="card">Geprüfte Geräte<strong>{summary['checked']}</strong></div></div><div class="dashboard-grid"><section class="dashboard-panel"><h3>Fortschritt bis Version {project.target_release}</h3>{project_progress_html(project)}</section><section class="dashboard-panel"><h3>Nächste Aufgaben</h3>{next_tasks_html(project, limit=5)}</section></div>{development_navigator_html(project)}<section class="status-section"><h3>Projektbestandteile</h3><div class="status-grid">{project_status_html()}</div></section></section>
<section class="page" id="page-geraete"><div class="device-layout"><div class="device-main"><h2>Geräte</h2><div class="filters"><label>Gerätefamilie<select id="family"><option value="">Alle</option></select></label><label>Hersteller<select id="manufacturer"><option value="">Alle</option></select></label><label>Polzahl<select id="poles"><option value="">Alle</option></select></label><label>Charakteristik<select id="curve"><option value="">Alle</option></select></label><label>Nennstrom<select id="current"><option value="">Alle</option></select></label><label>Status<select id="status"><option value="">Alle</option></select></label></div><div class="table-wrap"><table id="devices"><thead><tr><th>Name</th><th>Technische ID</th><th>Familie</th><th>Hersteller</th><th>Polzahl</th><th>Charakteristik</th><th>Nennstrom</th><th>Symbol</th><th>Footprint</th><th>3D</th><th>Status</th></tr></thead><tbody></tbody></table></div></div><section class="details"><h2>Eigenschaften</h2><dl id="properties"><dt>Auswahl</dt><dd>Bitte ein Gerät auswählen.</dd></dl><div class="preview-grid"><article class="preview-card"><h3>Symbol</h3><div class="preview" id="symbol-preview">Vorschau wird nach Auswahl angezeigt.</div></article><article class="preview-card"><h3>Footprint</h3><div class="preview" id="footprint-preview">Vorschau wird nach Auswahl angezeigt.</div></article></div></section></div></section>{library_page_html()}{library_health_page_html()}{security_page_html()}{placeholder_pages_html()}</div></main>
<footer><span id="count">{summary['devices']} Gerät(e)</span><span>Datenquellen: Gerätekatalog und project_state.yaml</span><span>Z_Cockpit 1.1</span></footer>
<script>const data={payload};const fields={{family:'family',manufacturer:'manufacturer',poles:'poles',curve:'curve',current:'current',status:'status'}};function showPage(id){{document.querySelectorAll('.page').forEach(x=>x.classList.toggle('active',x.id===`page-${{id}}`));document.querySelectorAll('.page-link').forEach(x=>x.classList.toggle('active',x.dataset.page===id));}}document.querySelectorAll('.page-link').forEach(button=>button.addEventListener('click',()=>showPage(button.dataset.page)));document.querySelector('[data-page="start"]').classList.add('active');function values(key){{return[...new Set(data.map(x=>x[key]))].sort((a,b)=>a.localeCompare(b,'de',{{numeric:true}}))}}function option(select,value){{const o=document.createElement('option');o.value=value;o.textContent=value;select.appendChild(o)}}Object.entries(fields).forEach(([id,key])=>{{const el=document.getElementById(id);values(key).forEach(v=>option(el,v));el.addEventListener('change',render)}});function mark(v){{return v?'<strong>✓</strong>':'–'}}function render(){{const tbody=document.querySelector('#devices tbody');tbody.innerHTML='';const rows=data.filter(item=>Object.entries(fields).every(([id,key])=>{{const v=document.getElementById(id).value;return!v||item[key]===v}}));rows.forEach(item=>{{const tr=document.createElement('tr');tr.innerHTML=`<td>${{item.name}}</td><td><code>${{item.id}}</code></td><td>${{item.family}}</td><td>${{item.manufacturer}}</td><td>${{item.poles}}</td><td>${{item.curve}}</td><td>${{item.current}}</td><td><code>${{item.symbol}}</code></td><td>${{item.footprint}}</td><td>${{mark(item.model)}}</td><td>${{item.status}}</td>`;tr.addEventListener('click',()=>selectRow(tr,item));tbody.appendChild(tr)}});document.getElementById('count').textContent=`${{rows.length}} Gerät(e)`}}function symbolPreviewHtml(item){{if(!item.symbol_preview_available)return `<div><strong>${{item.name}}</strong><p>Für dieses Symbol ist keine Vorschau verfügbar.</p></div>`;return `<div><img src="${{item.symbol_preview_url}}" alt="Symbolvorschau ${{item.symbol}}"><p class="preview-note">Technische SVG-Schnellansicht · ${{item.symbol}}</p></div>`}}function footprintPreviewHtml(item){{if(!item.footprint_preview_available)return `<div><strong>${{item.footprint}}</strong><p>Für diesen Footprint ist keine Vorschau verfügbar.</p><p class="preview-status">${{item.footprint_preview_status}}</p></div>`;const note=item.footprint_preview_status==='Platzhalter'?'Footprint vorhanden, aber noch ohne darstellbare Geometrie.':'Technische SVG-Schnellansicht';return `<div><img src="${{item.footprint_preview_url}}" alt="Footprintvorschau ${{item.footprint}}"><p class="preview-note">${{note}} · ${{item.footprint}}</p><p class="preview-status">${{item.footprint_preview_status}}</p></div>`}}function selectRow(tr,item){{document.querySelectorAll('#devices tbody tr').forEach(x=>x.classList.remove('selected'));tr.classList.add('selected');document.getElementById('properties').innerHTML=`<dt>Name</dt><dd>${{item.name}}</dd><dt>Technische ID</dt><dd><code>${{item.id}}</code></dd><dt>Symbol</dt><dd><code>${{item.symbol}}</code></dd><dt>Footprint</dt><dd><code>${{item.footprint}}</code></dd><dt>Familie</dt><dd>${{item.family}}</dd><dt>Nennstrom</dt><dd>${{item.current}}</dd><dt>Status</dt><dd>${{item.status}}</dd>`;document.getElementById('symbol-preview').innerHTML=symbolPreviewHtml(item);document.getElementById('footprint-preview').innerHTML=footprintPreviewHtml(item)}}render();</script></body></html>"""


def generated_content() -> str:
    return render_html(cockpit_devices())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="nur prüfen, ob die HTML-Datei aktuell ist")
    args = parser.parse_args()
    expected = generated_content()
    if args.check:
        actual = OUTPUT_PATH.read_text(encoding="utf-8") if OUTPUT_PATH.is_file() else ""
        if actual == expected:
            print("Die Z_Cockpit-Ansicht ist aktuell.")
            return 0
        print("Die Z_Cockpit-Ansicht ist nicht aktuell.", file=sys.stderr)
        return 1
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(expected, encoding="utf-8")
    print(f"Z_Cockpit erzeugt: {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
