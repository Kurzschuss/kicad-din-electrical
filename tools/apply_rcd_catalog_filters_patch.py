#!/usr/bin/env python3
"""Temporärer Arbeitshelfer: ergänzt RCD-Typ/IΔn in Katalog und Z_Cockpit."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: str, old: str, new: str) -> None:
    target = ROOT / path
    text = target.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{path}: erwartete genau einen Treffer, gefunden: {count}\n{old}")
    target.write_text(text.replace(old, new, 1), encoding="utf-8")


def patch_device_catalog() -> None:
    path = "tools/generate_device_catalog_html.py"
    replace_once(
        path,
        '                "rated_current_a": data.get("rated_current_a"),\n                "trip_curve": data.get("trip_curve"),',
        '                "rated_current_a": data.get("rated_current_a"),\n                "residual_current_ma": data.get("residual_current_ma"),\n                "rcd_type": data.get("rcd_type"),\n                "trip_curve": data.get("trip_curve"),',
    )
    replace_once(
        path,
        '        "families": sorted({str(item["family"]) for item in devices}, key=str.casefold),\n        "source_states": sorted({str(item["source_status"]) for item in devices}, key=str.casefold),',
        '        "families": sorted({str(item["family"]) for item in devices}, key=str.casefold),\n        "rcd_types": sorted(\n            {str(item["rcd_type"]) for item in devices if item.get("rcd_type") not in (None, "")},\n            key=str.casefold,\n        ),\n        "residual_currents_ma": sorted(\n            {item["residual_current_ma"] for item in devices if item.get("residual_current_ma") not in (None, "")},\n            key=float,\n        ),\n        "source_states": sorted({str(item["source_status"]) for item in devices}, key=str.casefold),',
    )
    replace_once(
        path,
        'def _rows(devices: list[dict[str, object]]) -> str:',
        'def _measurement_options(values: list[object], all_label: str, suffix: str) -> str:\n    rows = [f\'<option value="">{escape(all_label)}</option>\']\n    rows.extend(\n        f\'<option value="{escape(str(value))}">{escape(_display(value, suffix))}</option>\'\n        for value in values\n    )\n    return "\\n".join(rows)\n\n\ndef _rows(devices: list[dict[str, object]]) -> str:',
    )
    replace_once(
        path,
        '            f\'data-family="{escape(str(item["family"]))}" \'\n            f\'data-source="{escape(str(item["source_status"]))}">\'',
        '            f\'data-family="{escape(str(item["family"]))}" \'\n            f\'data-rcd-type="{escape(str(item.get("rcd_type") or ""))}" \'\n            f\'data-residual-current="{escape(str(item.get("residual_current_ma") or ""))}" \'\n            f\'data-source="{escape(str(item["source_status"]))}">\'',
    )
    replace_once(
        path,
        '            f\'<td>{escape(_display(item["rated_current_a"], " A"))}</td>\'\n            f\'<td>{escape(_display(item["trip_curve"]))}</td>\'',
        '            f\'<td>{escape(_display(item["rated_current_a"], " A"))}</td>\'\n            f\'<td>{escape(_display(item.get("rcd_type")))}</td>\'\n            f\'<td>{escape(_display(item.get("residual_current_ma"), " mA"))}</td>\'\n            f\'<td>{escape(_display(item["trip_curve"]))}</td>\'',
    )
    replace_once(path, 'grid-template-columns: 2fr repeat(3, 1fr)', 'grid-template-columns: 2fr repeat(5, 1fr)')
    replace_once(path, 'min-width: 1350px', 'min-width: 1550px')
    replace_once(
        path,
        '    <select id="family" aria-label="Gerätefamilie filtern">{_options(data[\'families\'], \'Alle Gerätefamilien\')}</select>\n    <select id="source" aria-label="Quellenstatus filtern">{_options(data[\'source_states\'], \'Alle Quellenstatus\')}</select>',
        '    <select id="family" aria-label="Gerätefamilie filtern">{_options(data[\'families\'], \'Alle Gerätefamilien\')}</select>\n    <select id="rcd-type" aria-label="RCD-Typ filtern">{_options(data.get(\'rcd_types\', []), \'Alle RCD-Typen\')}</select>\n    <select id="residual-current" aria-label="Bemessungsdifferenzstrom filtern">{_measurement_options(data.get(\'residual_currents_ma\', []), \'Alle IΔn\', \' mA\')}</select>\n    <select id="source" aria-label="Quellenstatus filtern">{_options(data[\'source_states\'], \'Alle Quellenstatus\')}</select>',
    )
    replace_once(
        path,
        '<th>Polzahl</th><th>Nennstrom</th><th>Kennlinie</th><th>Ausschaltvermögen</th>',
        '<th>Polzahl</th><th>Nennstrom</th><th>RCD-Typ</th><th>IΔn</th><th>Kennlinie</th><th>Ausschaltvermögen</th>',
    )
    replace_once(
        path,
        "    const family = document.getElementById('family');\n    const source = document.getElementById('source');",
        "    const family = document.getElementById('family');\n    const rcdType = document.getElementById('rcd-type');\n    const residualCurrent = document.getElementById('residual-current');\n    const source = document.getElementById('source');",
    )
    replace_once(
        path,
        "          && (!family.value || row.dataset.family === family.value)\n          && (!source.value || row.dataset.source === source.value);",
        "          && (!family.value || row.dataset.family === family.value)\n          && (!rcdType.value || row.dataset.rcdType === rcdType.value)\n          && (!residualCurrent.value || row.dataset.residualCurrent === residualCurrent.value)\n          && (!source.value || row.dataset.source === source.value);",
    )
    replace_once(
        path,
        "    [search, group, family, source].forEach(element => element.addEventListener(element.tagName === 'INPUT' ? 'input' : 'change', applyFilters));",
        "    [search, group, family, rcdType, residualCurrent, source].forEach(element => element.addEventListener(element.tagName === 'INPUT' ? 'input' : 'change', applyFilters));",
    )


def patch_device_catalog_tests() -> None:
    path = "tests/test_generate_device_catalog_html.py"
    replace_once(
        path,
        '    assert device["rated_current_a"] == 16\n    assert device["breaking_capacity_ka"] == 6',
        '    assert device["rated_current_a"] == 16\n    assert device["residual_current_ma"] is None\n    assert device["rcd_type"] is None\n    assert device["breaking_capacity_ka"] == 6',
    )
    marker = '\n\ndef test_render_html_contains_technical_columns_and_filters():'
    new_test = '''\n\ndef test_collect_devices_includes_rcd_values(tmp_path: Path):\n    device_root = tmp_path / "devices"\n    device_root.mkdir()\n    taxonomy = tmp_path / "families.json"\n    taxonomy.write_text(\n        json.dumps({"families": [{"id": "protection.rcd", "group": "Schutzgeräte", "name": "Fehlerstrom-Schutzeinrichtungen"}]}),\n        encoding="utf-8",\n    )\n    (device_root / "rcd.yaml").write_text(\n        json.dumps({\n            "id": "generic.rcd.b40-30ma",\n            "manufacturer": "Generic",\n            "series": "Template RCD",\n            "part_number": "RCD-B-40-30",\n            "device_type": "Fehlerstrom-Schutzschalter",\n            "function_group": "protection.rcd",\n            "poles": 2,\n            "rated_current_a": 40,\n            "residual_current_ma": 30,\n            "rcd_type": "B",\n            "modules": 2,\n            "symbol": "Z_RCD:RCD",\n            "footprint_policy": "optional",\n            "source_status": "template"\n        }),\n        encoding="utf-8",\n    )\n\n    data = collect_devices(device_root, taxonomy)\n    device = data["devices"][0]\n\n    assert device["rcd_type"] == "B"\n    assert device["residual_current_ma"] == 30\n    assert data["rcd_types"] == ["B"]\n    assert data["residual_currents_ma"] == [30]\n'''
    replace_once(path, marker, new_test + marker)
    replace_once(
        path,
        '    assert \'id="source"\' in html\n    assert "16 A" in html',
        '    assert \'id="source"\' in html\n    assert \'id="rcd-type"\' in html\n    assert \'id="residual-current"\' in html\n    assert "RCD-Typ" in html\n    assert "IΔn" in html\n    assert "16 A" in html',
    )
    target = ROOT / path
    text = target.read_text(encoding="utf-8")
    text += '''\n\ndef test_render_html_contains_rcd_filter_values_and_row_data():\n    data = {\n        "devices": [{\n            "id": "generic.rcd.b40-30ma",\n            "group": "Schutzgeräte",\n            "family": "Fehlerstrom-Schutzeinrichtungen",\n            "family_id": "protection.rcd",\n            "manufacturer": "Generic",\n            "series": "Template RCD",\n            "part_number": "RCD-B-40-30",\n            "device_type": "Fehlerstrom-Schutzschalter",\n            "poles": 2,\n            "rated_current_a": 40,\n            "residual_current_ma": 30,\n            "rcd_type": "B",\n            "trip_curve": None,\n            "breaking_capacity_ka": None,\n            "modules": 2,\n            "symbol": "Z_RCD:RCD",\n            "footprint_policy": "optional",\n            "source_status": "template",\n        }],\n        "groups": ["Schutzgeräte"],\n        "families": ["Fehlerstrom-Schutzeinrichtungen"],\n        "rcd_types": ["B"],\n        "residual_currents_ma": [30],\n        "source_states": ["template"],\n    }\n\n    html = render_html(data)\n\n    assert 'data-rcd-type="B"' in html\n    assert 'data-residual-current="30"' in html\n    assert '<option value="B">B</option>' in html\n    assert '<option value="30">30 mA</option>' in html\n    assert "40 A" in html\n    assert "30 mA" in html\n'''
    target.write_text(text, encoding="utf-8")


def patch_cockpit() -> None:
    path = "tools/generate_z_cockpit.py"
    replace_once(
        path,
        '            "current": _text(item.get("rated_current_a"), " A"),\n            "symbol": symbol,',
        '            "current": _text(item.get("rated_current_a"), " A"),\n            "rcd_type": _text(item.get("rcd_type")),\n            "residual_current": _text(item.get("residual_current_ma"), " mA"),\n            "symbol": symbol,',
    )
    replace_once(path, 'grid-template-columns:repeat(6,minmax(125px,1fr))', 'grid-template-columns:repeat(8,minmax(125px,1fr))')
    replace_once(path, 'table{{border-collapse:collapse;width:100%;min-width:1050px}}', 'table{{border-collapse:collapse;width:100%;min-width:1250px}}')
    replace_once(
        path,
        '<label>Nennstrom<select id="current"><option value="">Alle</option></select></label><label>Status<select id="status"><option value="">Alle</option></select></label>',
        '<label>Nennstrom<select id="current"><option value="">Alle</option></select></label><label>RCD-Typ<select id="rcd_type"><option value="">Alle</option></select></label><label>IΔn<select id="residual_current"><option value="">Alle</option></select></label><label>Status<select id="status"><option value="">Alle</option></select></label>',
    )
    replace_once(
        path,
        '<th>Charakteristik</th><th>Nennstrom</th><th>Symbol</th>',
        '<th>Charakteristik</th><th>Nennstrom</th><th>RCD-Typ</th><th>IΔn</th><th>Symbol</th>',
    )
    replace_once(
        path,
        "const fields={{family:'family',manufacturer:'manufacturer',poles:'poles',curve:'curve',current:'current',status:'status'}};",
        "const fields={{family:'family',manufacturer:'manufacturer',poles:'poles',curve:'curve',current:'current',rcd_type:'rcd_type',residual_current:'residual_current',status:'status'}};",
    )
    replace_once(
        path,
        '<td>${{item.curve}}</td><td>${{item.current}}</td><td><code>${{item.symbol}}</code></td>',
        '<td>${{item.curve}}</td><td>${{item.current}}</td><td>${{item.rcd_type}}</td><td>${{item.residual_current}}</td><td><code>${{item.symbol}}</code></td>',
    )
    replace_once(
        path,
        '<dt>Familie</dt><dd>${{item.family}}</dd><dt>Nennstrom</dt><dd>${{item.current}}</dd><dt>Status</dt>',
        '<dt>Familie</dt><dd>${{item.family}}</dd><dt>Nennstrom</dt><dd>${{item.current}}</dd><dt>RCD-Typ</dt><dd>${{item.rcd_type}}</dd><dt>IΔn</dt><dd>${{item.residual_current}}</dd><dt>Status</dt>',
    )
    replace_once(path, 'Z_Cockpit 1.1', 'Z_Cockpit 1.2')


def patch_cockpit_tests() -> None:
    path = "tests/test_generate_z_cockpit.py"
    replace_once(
        path,
        '    assert all(isinstance(item["model"], bool) for item in devices)\n',
        '    assert all(isinstance(item["model"], bool) for item in devices)\n    assert all("rcd_type" in item for item in devices)\n    assert all("residual_current" in item for item in devices)\n',
    )
    marker = '\n\ndef test_summary_uses_real_catalog_values():'
    new_test = '''\n\ndef test_rcd_values_are_exposed_for_cockpit_filtering():\n    device = next(\n        item\n        for item in cockpit_devices()\n        if item["id"] == "generic.rcd-2p-b-bplus-template-series.b40-30ma"\n    )\n    assert device["rcd_type"] == "B"\n    assert device["residual_current"] == "30 mA"\n    assert device["current"] == "40 A"\n    assert device["curve"] == "–"\n'''
    replace_once(path, marker, new_test + marker)
    replace_once(
        path,
        '    assert "Charakteristik" in html\n    assert "generic.mcb-1p-b16-template" in html',
        '    assert "Charakteristik" in html\n    assert "RCD-Typ" in html\n    assert "IΔn" in html\n    assert \'id="rcd_type"\' in html\n    assert \'id="residual_current"\' in html\n    assert "generic.mcb-1p-b16-template" in html\n    assert "generic.rcd-2p-b-bplus-template-series.b40-30ma" in html\n    assert \'\\"rcd_type\\": \\"B\\"\' in html\n    assert \'\\"residual_current\\": \\"30 mA\\"\' in html',
    )
    replace_once(path, '    assert "Z_Cockpit 1.1" in html', '    assert "Z_Cockpit 1.2" in html')


def patch_docs() -> None:
    path = "docs/03_Developer/Z_COCKPIT.md"
    replace_once(
        path,
        'Geräte- und Bibliotheksansicht behalten den festen rechten Inspektor und getrennte Scrollbereiche. Symbol-, Footprint- und 3D-Vorschauen werden aus vorhandenen Repositorydaten erzeugt. Eine technische `F.Fab`-Hüllkörpervorschau zählt nicht als echtes 3D-Modell.',
        'Geräte- und Bibliotheksansicht behalten den festen rechten Inspektor und getrennte Scrollbereiche. Die Geräteansicht führt für RCD/FI zusätzlich `RCD-Typ` und Bemessungsdifferenzstrom `IΔn` als eigene Tabellenwerte und Filter; MCB-Kennlinien bleiben weiterhin separat unter `Charakteristik`. Symbol-, Footprint- und 3D-Vorschauen werden aus vorhandenen Repositorydaten erzeugt. Eine technische `F.Fab`-Hüllkörpervorschau zählt nicht als echtes 3D-Modell.',
    )


def main() -> None:
    patch_device_catalog()
    patch_device_catalog_tests()
    patch_cockpit()
    patch_cockpit_tests()
    patch_docs()


if __name__ == "__main__":
    main()
