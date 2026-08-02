#!/usr/bin/env python3
"""Erzeugt eine statische, durchsuchbare HTML-Übersicht der KiCad-Bibliotheken."""

from __future__ import annotations

import argparse
from html import escape
import json
from pathlib import Path
import sys

from tools.generate_quality_report import collect_statistics
from tools.validate_device_catalog import DEVICE_ROOT, TAXONOMY_PATH, catalog_files, load_device
from tools.validate_libraries import (
    FOOTPRINT_ROOT,
    REPO_ROOT,
    SYMBOL_ROOT,
    footprint_policy,
    symbol_names,
    symbol_properties,
)

OUTPUT_PATH = REPO_ROOT / "docs" / "site" / "index.html"


def collect_devices(
    device_root: Path = DEVICE_ROOT, taxonomy_path: Path = TAXONOMY_PATH
) -> tuple[list[dict[str, object]], list[str]]:
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
                "manufacturer": data["manufacturer"],
                "series": data["series"],
                "part_number": data["part_number"],
                "device_type": data["device_type"],
                "family_id": data["function_group"],
                "group": family["group"],
                "family": family["name"],
                "symbol": data["symbol"],
                "footprint_policy": data["footprint_policy"],
                "footprint": data.get("footprint", "") or "—",
                "source_status": data.get("source_status", "unverified"),
            }
        )
    devices.sort(key=lambda item: (str(item["group"]).casefold(), str(item["family"]).casefold(), str(item["id"])))
    groups = sorted({str(item["group"]) for item in devices}, key=str.casefold)
    return devices, groups


def collect_site_data(symbol_root: Path = SYMBOL_ROOT, footprint_root: Path = FOOTPRINT_ROOT) -> dict[str, object]:
    symbols: list[dict[str, object]] = []
    for path in sorted(symbol_root.glob("Z_*.kicad_sym"), key=lambda item: item.name.casefold()):
        names = symbol_names(path)
        properties = symbol_properties(path) if names else {}
        symbols.append(
            {
                "library": path.stem,
                "status": "befüllt" if names else "vorbereitet, noch leer",
                "symbols": names,
                "policy": footprint_policy(properties) if names else "—",
                "footprint": properties.get("Footprint", "").strip() or "—",
            }
        )

    footprints: list[dict[str, object]] = []
    for pretty in sorted(
        (path for path in footprint_root.glob("Z_*.pretty") if path.is_dir()),
        key=lambda item: item.name.casefold(),
    ):
        files = sorted(pretty.glob("*.kicad_mod"), key=lambda item: item.name.casefold())
        footprints.append(
            {
                "library": pretty.stem,
                "count": len(files),
                "footprints": [path.stem for path in files],
            }
        )

    devices, device_groups = collect_devices()
    return {
        "statistics": collect_statistics(symbol_root, footprint_root),
        "symbols": symbols,
        "footprints": footprints,
        "devices": devices,
        "device_groups": device_groups,
    }


def _symbol_rows(items: list[dict[str, object]]) -> str:
    rows: list[str] = []
    for item in items:
        names = item["symbols"]
        content = ", ".join(escape(str(name)) for name in names) if names else "—"
        rows.append(
            "<tr>"
            f"<td><code>{escape(str(item['library']))}</code></td>"
            f"<td>{escape(str(item['status']))}</td>"
            f"<td>{content}</td>"
            f"<td><code>{escape(str(item['policy']))}</code></td>"
            f"<td><code>{escape(str(item['footprint']))}</code></td>"
            "</tr>"
        )
    return "\n".join(rows)


def _footprint_rows(items: list[dict[str, object]]) -> str:
    rows: list[str] = []
    for item in items:
        names = item["footprints"]
        content = ", ".join(f"<code>{escape(str(name))}</code>" for name in names) if names else "—"
        rows.append(
            "<tr>"
            f"<td><code>{escape(str(item['library']))}</code></td>"
            f"<td>{item['count']}</td>"
            f"<td>{content}</td>"
            "</tr>"
        )
    return "\n".join(rows)


def _device_rows(items: list[dict[str, object]]) -> str:
    rows: list[str] = []
    for item in items:
        rows.append(
            f'<tr data-group="{escape(str(item["group"]))}">'
            f"<td><code>{escape(str(item['id']))}</code></td>"
            f"<td>{escape(str(item['group']))}<br><span class=\"muted\">{escape(str(item['family']))}</span></td>"
            f"<td>{escape(str(item['manufacturer']))}</td>"
            f"<td>{escape(str(item['series']))}</td>"
            f"<td><code>{escape(str(item['part_number']))}</code></td>"
            f"<td>{escape(str(item['device_type']))}</td>"
            f"<td><code>{escape(str(item['symbol']))}</code></td>"
            f"<td><code>{escape(str(item['footprint_policy']))}</code></td>"
            f"<td>{escape(str(item['source_status']))}</td>"
            "</tr>"
        )
    return "\n".join(rows)


def render_html(data: dict[str, object]) -> str:
    stats = data["statistics"]
    symbols = data["symbols"]
    footprints = data["footprints"]
    devices = data["devices"]
    device_groups = data["device_groups"]
    errors = stats["errors"]
    warnings = stats["warnings"]
    quality = "Keine blockierenden Fehler" if not errors else f"{len(errors)} blockierende Fehler"
    group_options = "\n".join(
        f'<option value="{escape(str(group))}">{escape(str(group))}</option>' for group in device_groups
    )

    return f"""<!doctype html>
<html lang="de">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>KiCad DIN Electrical – Bibliotheksreferenz</title>
  <style>
    :root {{ color-scheme: light dark; font-family: system-ui, sans-serif; }}
    body {{ max-width: 1280px; margin: 0 auto; padding: 2rem; line-height: 1.5; }}
    header {{ margin-bottom: 2rem; }}
    .cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 1rem; }}
    .card {{ border: 1px solid #8886; border-radius: .6rem; padding: 1rem; }}
    .card strong {{ display: block; font-size: 1.7rem; }}
    .filters {{ display: grid; grid-template-columns: 2fr 1fr; gap: 1rem; margin: 1.5rem 0; }}
    input, select {{ width: 100%; box-sizing: border-box; padding: .75rem; font: inherit; }}
    .table-wrap {{ overflow-x: auto; margin-bottom: 2.5rem; }}
    table {{ width: 100%; border-collapse: collapse; min-width: 760px; }}
    th, td {{ border-bottom: 1px solid #8885; padding: .65rem; text-align: left; vertical-align: top; }}
    th {{ position: sticky; top: 0; background: Canvas; }}
    code {{ overflow-wrap: anywhere; }}
    .muted {{ opacity: .75; }}
    @media (max-width: 700px) {{ .filters {{ grid-template-columns: 1fr; }} }}
  </style>
</head>
<body>
  <header>
    <h1>KiCad DIN Electrical – Bibliotheksreferenz</h1>
    <p>Automatisch erzeugte Übersicht der Symbol-, Footprint- und Gerätedaten.</p>
  </header>

  <section class="cards" aria-label="Kennzahlen">
    <div class="card"><strong>{stats['symbol_libraries']}</strong>Symbolbibliotheken</div>
    <div class="card"><strong>{stats['symbols']}</strong>Hauptsymbole</div>
    <div class="card"><strong>{stats['footprint_libraries']}</strong>Footprintbibliotheken</div>
    <div class="card"><strong>{stats['footprints']}</strong>Footprints</div>
    <div class="card"><strong>{len(devices)}</strong>Geräte</div>
    <div class="card"><strong>{len(device_groups)}</strong>belegte Funktionsgruppen</div>
    <div class="card"><strong>{len(errors)}</strong>Fehler</div>
    <div class="card"><strong>{len(warnings)}</strong>Hinweise</div>
  </section>

  <p><strong>Qualitätsstatus:</strong> {escape(quality)}</p>
  <div class="filters">
    <input id="search" type="search" placeholder="Bibliothek, Symbol, Footprint oder Gerät suchen …" aria-label="Referenz durchsuchen">
    <select id="group" aria-label="Geräte nach Funktionsgruppe filtern">
      <option value="">Alle Funktionsgruppen</option>
{group_options}
    </select>
  </div>

  <h2>Gerätekatalog</h2>
  <p class="muted">Die Gruppen- und Familiennamen stammen aus der zentralen Gerätetaxonomie. <code>template</code> kennzeichnet herstellerneutrale Beispieldaten.</p>
  <div class="table-wrap"><table id="devices">
    <thead><tr><th>Geräte-ID</th><th>Gruppe / Familie</th><th>Hersteller</th><th>Serie</th><th>Artikelnummer</th><th>Gerätetyp</th><th>Symbol</th><th>Footprint Policy</th><th>Quellenstatus</th></tr></thead>
    <tbody>
{_device_rows(devices)}
    </tbody>
  </table></div>

  <h2>Symbolbibliotheken</h2>
  <div class="table-wrap"><table id="symbols">
    <thead><tr><th>Bibliothek</th><th>Status</th><th>Symbole</th><th>Footprint Policy</th><th>Standard-Footprint</th></tr></thead>
    <tbody>
{_symbol_rows(symbols)}
    </tbody>
  </table></div>

  <h2>Footprintbibliotheken</h2>
  <div class="table-wrap"><table id="footprints">
    <thead><tr><th>Bibliothek</th><th>Anzahl</th><th>Footprints</th></tr></thead>
    <tbody>
{_footprint_rows(footprints)}
    </tbody>
  </table></div>

  <p class="muted">Erzeugt mit <code>python tools/generate_html_reference.py</code>. Ein fehlender Footprint ist zulässig, sofern die Richtlinie nicht <code>required</code> lautet.</p>

  <script>
    const input = document.getElementById('search');
    const group = document.getElementById('group');
    function applyFilters() {{
      const query = input.value.toLocaleLowerCase('de');
      const selectedGroup = group.value;
      document.querySelectorAll('tbody tr').forEach(row => {{
        const matchesText = row.textContent.toLocaleLowerCase('de').includes(query);
        const matchesGroup = !row.closest('#devices') || !selectedGroup || row.dataset.group === selectedGroup;
        row.hidden = !(matchesText && matchesGroup);
      }});
    }}
    input.addEventListener('input', applyFilters);
    group.addEventListener('change', applyFilters);
  </script>
</body>
</html>
"""


def generated_content() -> str:
    return render_html(collect_site_data())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="nur prüfen, ob die HTML-Datei aktuell ist")
    args = parser.parse_args()
    expected = generated_content()

    if args.check:
        actual = OUTPUT_PATH.read_text(encoding="utf-8") if OUTPUT_PATH.is_file() else ""
        if actual == expected:
            print("Die HTML-Bibliotheksreferenz ist aktuell.")
            return 0
        print("Die HTML-Bibliotheksreferenz ist nicht aktuell.", file=sys.stderr)
        print("Bitte den Generator ohne --check ausführen.", file=sys.stderr)
        return 1

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(expected, encoding="utf-8")
    print(f"Erzeugt: {OUTPUT_PATH.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
