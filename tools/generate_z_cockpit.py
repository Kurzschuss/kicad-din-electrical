#!/usr/bin/env python3
"""Erzeugt die tabellenbasierte Z_Cockpit-Ansicht aus dem Gerätekatalog."""

from __future__ import annotations

import argparse
from html import escape
import json
from pathlib import Path
import sys

from tools.generate_device_catalog_html import collect_devices
from tools.validate_device_catalog import REPO_ROOT

OUTPUT_PATH = REPO_ROOT / "docs" / "site" / "z-cockpit.html"


def _text(value: object, suffix: str = "") -> str:
    if value is None or value == "":
        return "–"
    return f"{value}{suffix}"


def cockpit_devices() -> list[dict[str, object]]:
    result: list[dict[str, object]] = []
    for item in collect_devices()["devices"]:
        manufacturer = str(item["manufacturer"])
        result.append(
            {
                "name": str(item.get("name_de") or item["device_type"]),
                "id": str(item["id"]),
                "family": str(item["family"]),
                "manufacturer": "Herstellerneutral" if manufacturer == "Generic" else manufacturer,
                "poles": _text(item.get("poles"), "P"),
                "curve": _text(item.get("trip_curve")),
                "current": _text(item.get("rated_current_a"), " A"),
                "symbol": str(item["symbol"]),
                "footprint": str(item["footprint_policy"]),
                "model": False,
                "status": "Geprüft" if item.get("source_status") == "template" else "Entwurf",
            }
        )
    return result


def render_html(devices: list[dict[str, object]]) -> str:
    payload = json.dumps(devices, ensure_ascii=False).replace("</", "<\\/")
    return f"""<!doctype html>
<html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Z_Cockpit – Geräteübersicht</title><style>
:root{{font-family:system-ui,sans-serif;color-scheme:light dark}}*{{box-sizing:border-box}}body{{margin:0;min-height:100vh;display:grid;grid-template-rows:auto auto 1fr auto}}header,nav,footer{{padding:.7rem 1rem;border-bottom:1px solid #8886}}header h1{{margin:0;font-size:1.25rem}}nav{{display:flex;gap:1rem}}main{{display:grid;grid-template-columns:230px 1fr 310px;min-height:0}}aside,section{{padding:1rem;overflow:auto}}aside{{border-right:1px solid #8886}}.details{{border-left:1px solid #8886}}ul{{list-style:none;padding:0}}li{{padding:.4rem .5rem;cursor:pointer}}li.active,tbody tr.selected{{background:#2878c81f;font-weight:700}}.filters{{display:grid;grid-template-columns:repeat(6,minmax(125px,1fr));gap:.6rem;margin-bottom:.8rem}}label{{display:grid;gap:.2rem;font-size:.8rem}}select{{padding:.45rem}}.table-wrap{{overflow:auto;border:1px solid #8886}}table{{border-collapse:collapse;width:100%;min-width:1050px}}th,td{{padding:.55rem .65rem;border-bottom:1px solid #8884;text-align:left;white-space:nowrap}}th{{position:sticky;top:0;background:Canvas}}tbody tr{{cursor:pointer}}tbody tr:hover{{background:#2878c812}}dl{{display:grid;grid-template-columns:1fr 1.4fr;gap:.45rem .7rem}}dt{{font-weight:700}}dd{{margin:0}}.preview{{margin-top:.7rem;min-height:180px;display:grid;place-items:center;border:1px dashed #8888;text-align:center}}footer{{border-top:1px solid #8886;border-bottom:0;display:flex;justify-content:space-between}}@media(max-width:1050px){{main{{grid-template-columns:200px 1fr}}.details{{grid-column:1/-1;border-left:0;border-top:1px solid #8886}}}}
</style></head><body>
<header><h1>Z_Cockpit – Bibliotheks- und Geräteübersicht</h1></header><nav><span>Datei</span><span>Bibliothek</span><span>Werkzeuge</span><span>Qualität</span><span>Ansicht</span><span>Hilfe</span></nav>
<main><aside><h2>Gerätefamilien</h2><ul id="families"><li class="active" data-family="">Alle Geräte</li></ul></aside>
<section><div class="filters">
<label>Gerätefamilie<select id="family"><option value="">Alle</option></select></label><label>Hersteller<select id="manufacturer"><option value="">Alle</option></select></label><label>Polzahl<select id="poles"><option value="">Alle</option></select></label><label>Charakteristik<select id="curve"><option value="">Alle</option></select></label><label>Nennstrom<select id="current"><option value="">Alle</option></select></label><label>Status<select id="status"><option value="">Alle</option></select></label>
</div><div class="table-wrap"><table id="devices"><thead><tr><th>Name</th><th>Technische ID</th><th>Familie</th><th>Hersteller</th><th>Polzahl</th><th>Charakteristik</th><th>Nennstrom</th><th>Symbol</th><th>Footprint</th><th>3D</th><th>Status</th></tr></thead><tbody></tbody></table></div></section>
<section class="details"><h2>Eigenschaften</h2><dl id="properties"><dt>Auswahl</dt><dd>Bitte ein Gerät auswählen.</dd></dl><div class="preview" id="preview">Vorschau wird nach Auswahl angezeigt.</div></section></main>
<footer><span id="count">0 Geräte</span><span>Datenquelle: technischer Gerätekatalog</span><span>Z_Cockpit 0.2</span></footer>
<script>const data={payload};const fields={{family:'family',manufacturer:'manufacturer',poles:'poles',curve:'curve',current:'current',status:'status'}};
function values(key){{return[...new Set(data.map(x=>x[key]))].sort((a,b)=>a.localeCompare(b,'de',{{numeric:true}}))}}function option(select,value){{const o=document.createElement('option');o.value=value;o.textContent=value;select.appendChild(o)}}
Object.entries(fields).forEach(([id,key])=>{{const el=document.getElementById(id);values(key).forEach(v=>option(el,v));el.addEventListener('change',render)}});const list=document.getElementById('families');values('family').forEach(v=>{{const li=document.createElement('li');li.dataset.family=v;li.textContent=v;list.appendChild(li)}});list.querySelectorAll('li').forEach(li=>li.addEventListener('click',()=>{{list.querySelectorAll('li').forEach(x=>x.classList.remove('active'));li.classList.add('active');document.getElementById('family').value=li.dataset.family;render()}}));
function mark(v){{return v?'<strong>✓</strong>':'–'}}function render(){{const tbody=document.querySelector('#devices tbody');tbody.innerHTML='';const rows=data.filter(item=>Object.entries(fields).every(([id,key])=>{{const v=document.getElementById(id).value;return!v||item[key]===v}}));rows.forEach(item=>{{const tr=document.createElement('tr');tr.innerHTML=`<td>${{item.name}}</td><td><code>${{item.id}}</code></td><td>${{item.family}}</td><td>${{item.manufacturer}}</td><td>${{item.poles}}</td><td>${{item.curve}}</td><td>${{item.current}}</td><td><code>${{item.symbol}}</code></td><td>${{item.footprint}}</td><td>${{mark(item.model)}}</td><td>${{item.status}}</td>`;tr.addEventListener('click',()=>selectRow(tr,item));tbody.appendChild(tr)}});document.getElementById('count').textContent=`${{rows.length}} Gerät(e)`}}
function selectRow(tr,item){{document.querySelectorAll('#devices tbody tr').forEach(x=>x.classList.remove('selected'));tr.classList.add('selected');document.getElementById('properties').innerHTML=`<dt>Name</dt><dd>${{item.name}}</dd><dt>Technische ID</dt><dd><code>${{item.id}}</code></dd><dt>Symbol</dt><dd><code>${{item.symbol}}</code></dd><dt>Familie</dt><dd>${{item.family}}</dd><dt>Nennstrom</dt><dd>${{item.current}}</dd><dt>Status</dt><dd>${{item.status}}</dd>`;document.getElementById('preview').innerHTML=`<strong>${{item.name}}</strong><br><br>Symbolvorschau wird im nächsten Ausbau angebunden.`}}render();</script></body></html>"""


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
    print(f"Erzeugt: {OUTPUT_PATH.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
