#!/usr/bin/env python3
"""Erzeugt eine statische HTML-Seite für den technischen Gerätekatalog."""

from __future__ import annotations

import argparse
from html import escape
import json
from pathlib import Path
import sys

from tools.validate_device_catalog import DEVICE_ROOT, REPO_ROOT, TAXONOMY_PATH, catalog_files, load_device

OUTPUT_PATH = REPO_ROOT / "docs" / "site" / "devices.html"


def _display(value: object, suffix: str = "") -> str:
    if value is None or value == "":
        return "—"
    return f"{value}{suffix}"


def collect_devices(
    device_root: Path = DEVICE_ROOT,
    taxonomy_path: Path = TAXONOMY_PATH,
) -> dict[str, object]:
    taxonomy = json.loads(taxonomy_path.read_text(encoding="utf-8"))
    families = {
        item["id"]: {"group": item["group"], "name": item["name"]}
        for item in taxonomy["families"]
    }
    devices: list[dict[str, object]] = []
    for path in catalog_files(device_root):
        data = load_device(path)
        family = families[data["function_group"]]
        devices.append(
            {
                "id": data["id"],
                "group": family["group"],
                "family": family["name"],
                "family_id": data["function_group"],
                "manufacturer": data["manufacturer"],
                "series": data["series"],
                "part_number": data["part_number"],
                "device_type": data["device_type"],
                "poles": data.get("poles"),
                "rated_current_a": data.get("rated_current_a"),
                "residual_current_ma": data.get("residual_current_ma"),
                "rcd_type": data.get("rcd_type"),
                "trip_curve": data.get("trip_curve"),
                "breaking_capacity_ka": data.get("breaking_capacity_ka"),
                "modules": data.get("modules"),
                "symbol": data["symbol"],
                "footprint_policy": data["footprint_policy"],
                "source_status": data.get("source_status", "unverified"),
            }
        )
    devices.sort(key=lambda item: (str(item["group"]).casefold(), str(item["family"]).casefold(), str(item["id"])))
    return {
        "devices": devices,
        "groups": sorted({str(item["group"]) for item in devices}, key=str.casefold),
        "families": sorted({str(item["family"]) for item in devices}, key=str.casefold),
        "rcd_types": sorted(
            {str(item["rcd_type"]) for item in devices if item.get("rcd_type") not in (None, "")},
            key=str.casefold,
        ),
        "residual_currents_ma": sorted(
            {item["residual_current_ma"] for item in devices if item.get("residual_current_ma") not in (None, "")},
            key=float,
        ),
        "source_states": sorted({str(item["source_status"]) for item in devices}, key=str.casefold),
    }


def _options(values: list[str], all_label: str) -> str:
    rows = [f'<option value="">{escape(all_label)}</option>']
    rows.extend(f'<option value="{escape(value)}">{escape(value)}</option>' for value in values)
    return "\n".join(rows)


def _measurement_options(values: list[object], all_label: str, suffix: str) -> str:
    rows = [f'<option value="">{escape(all_label)}</option>']
    rows.extend(
        f'<option value="{escape(str(value))}">{escape(_display(value, suffix))}</option>'
        for value in values
    )
    return "\n".join(rows)


def _rows(devices: list[dict[str, object]]) -> str:
    rows: list[str] = []
    for item in devices:
        rows.append(
            f'<tr data-group="{escape(str(item["group"]))}" '
            f'data-family="{escape(str(item["family"]))}" '
            f'data-rcd-type="{escape(str(item.get("rcd_type") or ""))}" '
            f'data-residual-current="{escape(str(item.get("residual_current_ma") or ""))}" '
            f'data-source="{escape(str(item["source_status"]))}">'
            f'<td><code>{escape(str(item["id"]))}</code></td>'
            f'<td>{escape(str(item["group"]))}<br><span class="muted">{escape(str(item["family"]))}</span></td>'
            f'<td>{escape(str(item["manufacturer"]))}</td>'
            f'<td>{escape(str(item["series"]))}</td>'
            f'<td><code>{escape(str(item["part_number"]))}</code></td>'
            f'<td>{escape(_display(item["poles"]))}</td>'
            f'<td>{escape(_display(item["rated_current_a"], " A"))}</td>'
            f'<td>{escape(_display(item.get("rcd_type")))}</td>'
            f'<td>{escape(_display(item.get("residual_current_ma"), " mA"))}</td>'
            f'<td>{escape(_display(item["trip_curve"]))}</td>'
            f'<td>{escape(_display(item["breaking_capacity_ka"], " kA"))}</td>'
            f'<td>{escape(_display(item["modules"], " TE"))}</td>'
            f'<td><code>{escape(str(item["symbol"]))}</code></td>'
            f'<td><code>{escape(str(item["footprint_policy"]))}</code></td>'
            f'<td>{escape(str(item["source_status"]))}</td>'
            '</tr>'
        )
    return "\n".join(rows)


def render_html(data: dict[str, object]) -> str:
    devices = data["devices"]
    return f"""<!doctype html>
<html lang="de">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>KiCad DIN Electrical – Gerätekatalog</title>
  <style>
    :root {{ color-scheme: light dark; font-family: system-ui, sans-serif; }}
    body {{ max-width: 1500px; margin: 0 auto; padding: 2rem; line-height: 1.5; }}
    .filters {{ display: grid; grid-template-columns: 2fr repeat(5, 1fr); gap: .75rem; margin: 1.5rem 0; }}
    input, select {{ width: 100%; box-sizing: border-box; padding: .7rem; font: inherit; }}
    .table-wrap {{ overflow-x: auto; }}
    table {{ width: 100%; min-width: 1550px; border-collapse: collapse; }}
    th, td {{ border-bottom: 1px solid #8885; padding: .6rem; text-align: left; vertical-align: top; }}
    th {{ position: sticky; top: 0; background: Canvas; }}
    .muted {{ opacity: .72; }}
    .count {{ font-weight: 700; }}
    @media (max-width: 900px) {{ .filters {{ grid-template-columns: 1fr 1fr; }} }}
    @media (max-width: 600px) {{ .filters {{ grid-template-columns: 1fr; }} }}
  </style>
</head>
<body>
  <header>
    <h1>Technischer Gerätekatalog</h1>
    <p>Fachliche Gerätedaten mit elektrischen Kenngrößen. Herstellerneutrale Vorlagen bleiben durch den Quellenstatus <code>template</code> erkennbar.</p>
    <p><a href="index.html">Zur Bibliotheksübersicht</a></p>
  </header>

  <p><span class="count" id="count">{len(devices)}</span> von {len(devices)} Geräten sichtbar</p>
  <div class="filters">
    <input id="search" type="search" placeholder="Gerät, Hersteller, Serie oder Artikelnummer suchen …" aria-label="Geräte durchsuchen">
    <select id="group" aria-label="Funktionsgruppe filtern">{_options(data['groups'], 'Alle Funktionsgruppen')}</select>
    <select id="family" aria-label="Gerätefamilie filtern">{_options(data['families'], 'Alle Gerätefamilien')}</select>
    <select id="rcd-type" aria-label="RCD-Typ filtern">{_options(data.get('rcd_types', []), 'Alle RCD-Typen')}</select>
    <select id="residual-current" aria-label="Bemessungsdifferenzstrom filtern">{_measurement_options(data.get('residual_currents_ma', []), 'Alle IΔn', ' mA')}</select>
    <select id="source" aria-label="Quellenstatus filtern">{_options(data['source_states'], 'Alle Quellenstatus')}</select>
  </div>

  <div class="table-wrap"><table id="devices">
    <thead><tr><th>Geräte-ID</th><th>Gruppe / Familie</th><th>Hersteller</th><th>Serie</th><th>Artikelnummer</th><th>Polzahl</th><th>Nennstrom</th><th>RCD-Typ</th><th>IΔn</th><th>Kennlinie</th><th>Ausschaltvermögen</th><th>Breite</th><th>Symbol</th><th>Footprint Policy</th><th>Quelle</th></tr></thead>
    <tbody>
{_rows(devices)}
    </tbody>
  </table></div>

  <p class="muted">Erzeugt mit <code>python tools/generate_device_catalog_html.py</code>.</p>
  <script>
    const search = document.getElementById('search');
    const group = document.getElementById('group');
    const family = document.getElementById('family');
    const rcdType = document.getElementById('rcd-type');
    const residualCurrent = document.getElementById('residual-current');
    const source = document.getElementById('source');
    const count = document.getElementById('count');
    function applyFilters() {{
      const query = search.value.toLocaleLowerCase('de');
      let visible = 0;
      document.querySelectorAll('#devices tbody tr').forEach(row => {{
        const matches = row.textContent.toLocaleLowerCase('de').includes(query)
          && (!group.value || row.dataset.group === group.value)
          && (!family.value || row.dataset.family === family.value)
          && (!rcdType.value || row.dataset.rcdType === rcdType.value)
          && (!residualCurrent.value || row.dataset.residualCurrent === residualCurrent.value)
          && (!source.value || row.dataset.source === source.value);
        row.hidden = !matches;
        if (matches) visible += 1;
      }});
      count.textContent = visible;
    }}
    [search, group, family, rcdType, residualCurrent, source].forEach(element => element.addEventListener(element.tagName === 'INPUT' ? 'input' : 'change', applyFilters));
  </script>
</body>
</html>
"""


def generated_content() -> str:
    return render_html(collect_devices())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="nur prüfen, ob die HTML-Datei aktuell ist")
    args = parser.parse_args()
    expected = generated_content()
    if args.check:
        actual = OUTPUT_PATH.read_text(encoding="utf-8") if OUTPUT_PATH.is_file() else ""
        if actual == expected:
            print("Der HTML-Gerätekatalog ist aktuell.")
            return 0
        print("Der HTML-Gerätekatalog ist nicht aktuell.", file=sys.stderr)
        return 1
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(expected, encoding="utf-8")
    print(f"Erzeugt: {OUTPUT_PATH.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
