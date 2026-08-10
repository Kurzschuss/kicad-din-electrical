from __future__ import annotations

from dataclasses import dataclass
from html import escape
import json

from tools.generate_device_catalog_html import collect_devices


_SOURCE_LABELS = {
    "template": "Vorlage",
    "verified": "Verifiziert",
    "unverified": "Ungeprüft",
}


@dataclass(frozen=True)
class ManufacturerSeriesView:
    name: str
    device_ids: tuple[str, ...]
    families: tuple[str, ...]
    source_states: tuple[str, ...]

    @property
    def device_count(self) -> int:
        return len(self.device_ids)


@dataclass(frozen=True)
class ManufacturerView:
    catalog_name: str
    display_name: str
    series: tuple[ManufacturerSeriesView, ...]
    device_ids: tuple[str, ...]
    families: tuple[str, ...]
    source_states: tuple[str, ...]

    @property
    def series_count(self) -> int:
        return len(self.series)

    @property
    def device_count(self) -> int:
        return len(self.device_ids)


def _manufacturer_name(value: str) -> str:
    return "Herstellerneutral" if value == "Generic" else value


def _source_label(value: str) -> str:
    return _SOURCE_LABELS.get(value, value or "Unbekannt")


def collect_manufacturers(
    devices: list[dict[str, object]] | None = None,
) -> tuple[ManufacturerView, ...]:
    """Aggregiert Hersteller und Serien ausschließlich aus dem technischen Gerätekatalog."""
    source = list(collect_devices()["devices"]) if devices is None else list(devices)
    manufacturers: dict[str, dict[str, object]] = {}

    for item in source:
        catalog_name = str(item.get("manufacturer") or "Unbekannt")
        series_name = str(item.get("series") or "Ohne Serie")
        family = str(item.get("family") or "Unbekannt")
        source_state = str(item.get("source_status") or "unverified")
        device_id = str(item.get("id") or "")
        if not device_id:
            continue

        manufacturer = manufacturers.setdefault(
            catalog_name,
            {
                "device_ids": set(),
                "families": set(),
                "source_states": set(),
                "series": {},
            },
        )
        manufacturer["device_ids"].add(device_id)  # type: ignore[union-attr]
        manufacturer["families"].add(family)  # type: ignore[union-attr]
        manufacturer["source_states"].add(source_state)  # type: ignore[union-attr]

        series_map = manufacturer["series"]  # type: ignore[index]
        series = series_map.setdefault(
            series_name,
            {"device_ids": set(), "families": set(), "source_states": set()},
        )
        series["device_ids"].add(device_id)
        series["families"].add(family)
        series["source_states"].add(source_state)

    result: list[ManufacturerView] = []
    for catalog_name, manufacturer in manufacturers.items():
        series_items: list[ManufacturerSeriesView] = []
        for series_name, series in manufacturer["series"].items():  # type: ignore[union-attr]
            series_items.append(
                ManufacturerSeriesView(
                    name=series_name,
                    device_ids=tuple(sorted(series["device_ids"], key=str.casefold)),
                    families=tuple(sorted(series["families"], key=str.casefold)),
                    source_states=tuple(sorted(series["source_states"], key=str.casefold)),
                )
            )
        series_items.sort(key=lambda item: item.name.casefold())
        result.append(
            ManufacturerView(
                catalog_name=catalog_name,
                display_name=_manufacturer_name(catalog_name),
                series=tuple(series_items),
                device_ids=tuple(sorted(manufacturer["device_ids"], key=str.casefold)),  # type: ignore[arg-type]
                families=tuple(sorted(manufacturer["families"], key=str.casefold)),  # type: ignore[arg-type]
                source_states=tuple(sorted(manufacturer["source_states"], key=str.casefold)),  # type: ignore[arg-type]
            )
        )

    return tuple(sorted(result, key=lambda item: item.display_name.casefold()))


def _options(values: tuple[str, ...]) -> str:
    return "".join(f'<option value="{escape(value)}">{escape(value)}</option>' for value in values)


def _json_attr(values: tuple[str, ...]) -> str:
    return escape(json.dumps(values, ensure_ascii=False), quote=True)


def _source_text(states: tuple[str, ...]) -> str:
    return ", ".join(_source_label(value) for value in states)


def _series_table(item: ManufacturerView) -> str:
    rows = []
    for series in item.series:
        rows.append(
            '<tr>'
            f'<th scope="row">{escape(series.name)}</th>'
            f'<td>{series.device_count}</td>'
            f'<td>{escape(", ".join(series.families))}</td>'
            f'<td>{escape(_source_text(series.source_states))}</td>'
            '</tr>'
        )
    if not rows:
        return '<p class="manufacturer-empty">Keine Serienzuordnung vorhanden.</p>'
    return (
        '<div class="manufacturer-series-wrap"><table class="manufacturer-series-table">'
        '<thead><tr><th>Serie</th><th>Geräte</th><th>Gerätefamilien</th><th>Quellenstatus</th></tr></thead>'
        f'<tbody>{"".join(rows)}</tbody></table></div>'
    )


def _inspector_template(item: ManufacturerView, index: int) -> str:
    device_ids = "".join(f'<li><code>{escape(device_id)}</code></li>' for device_id in item.device_ids)
    catalog_note = (
        "Herstellerneutrale Katalogvorlage"
        if item.catalog_name == "Generic"
        else item.catalog_name
    )
    return (
        f'<template id="manufacturer-inspector-{index}">'
        '<div class="manufacturer-inspector-fixed">'
        '<dl class="manufacturer-properties">'
        f'<dt>Hersteller</dt><dd><strong>{escape(item.display_name)}</strong></dd>'
        f'<dt>Katalogwert</dt><dd><code>{escape(item.catalog_name)}</code></dd>'
        f'<dt>Einordnung</dt><dd>{escape(catalog_note)}</dd>'
        f'<dt>Serien</dt><dd>{item.series_count}</dd>'
        f'<dt>Geräte</dt><dd>{item.device_count}</dd>'
        f'<dt>Gerätefamilien</dt><dd>{escape(", ".join(item.families))}</dd>'
        f'<dt>Quellenstatus</dt><dd>{escape(_source_text(item.source_states))}</dd>'
        '</dl>'
        '<h3>Serien</h3>'
        f'{_series_table(item)}'
        '</div>'
        '<section class="manufacturer-device-section"><h3>Geräte-IDs</h3>'
        f'<div class="manufacturer-device-scroll"><ul class="manufacturer-device-ids">{device_ids}</ul></div>'
        '</section>'
        '</template>'
    )


def manufacturer_page_html(
    manufacturers: tuple[ManufacturerView, ...] | None = None,
) -> str:
    """Rendert die read-only Hersteller-/Serienübersicht aus dem Gerätekatalog."""
    items = collect_manufacturers() if manufacturers is None else manufacturers
    total_series = sum(item.series_count for item in items)
    total_devices = sum(item.device_count for item in items)
    families = tuple(sorted({family for item in items for family in item.families}, key=str.casefold))
    series_names = tuple(sorted({series.name for item in items for series in item.series}, key=str.casefold))
    source_labels = tuple(
        sorted({_source_label(state) for item in items for state in item.source_states}, key=str.casefold)
    )
    manufacturer_names = tuple(item.display_name for item in items)

    rows: list[str] = []
    templates: list[str] = []
    for index, item in enumerate(items):
        source_text = _source_text(item.source_states)
        rows.append(
            f'<tr class="manufacturer-row" tabindex="0" data-index="{index}" '
            f'data-manufacturer="{escape(item.display_name, quote=True)}" '
            f'data-series="{_json_attr(tuple(series.name for series in item.series))}" '
            f'data-families="{_json_attr(item.families)}" '
            f'data-sources="{_json_attr(tuple(_source_label(state) for state in item.source_states))}">'
            f'<th scope="row"><strong>{escape(item.display_name)}</strong></th>'
            f'<td>{item.series_count}</td><td>{item.device_count}</td>'
            f'<td>{escape(", ".join(item.families))}</td>'
            f'<td>{escape(source_text)}</td></tr>'
        )
        templates.append(_inspector_template(item, index))

    empty_row = '<tr><td colspan="5">Keine Herstellerdaten im Gerätekatalog vorhanden.</td></tr>'
    table_rows = "".join(rows) if rows else empty_row

    return (
        '<style>'
        '#page-hersteller.active{position:absolute;inset:0;display:flex;flex-direction:column;min-height:0;overflow:hidden;padding:0}'
        '.manufacturer-workspace{display:grid;grid-template-columns:minmax(0,1fr) 360px;height:100%;min-height:0;overflow:hidden}'
        '.manufacturer-main{min-width:0;min-height:0;padding:1rem;display:flex;flex-direction:column;overflow:hidden}'
        '.manufacturer-title{margin:0 0 .35rem;flex:0 0 auto}'
        '.manufacturer-subtitle{margin:.1rem 0 .9rem;opacity:.78;flex:0 0 auto}'
        '.manufacturer-filters{display:grid;grid-template-columns:repeat(4,minmax(130px,1fr));gap:.6rem;margin-bottom:.8rem;flex:0 0 auto}'
        '.manufacturer-table-wrap{flex:1 1 auto;min-height:0;overflow:auto;border:1px solid #8886}'
        '.manufacturer-table{border-collapse:collapse;width:100%;min-width:760px}'
        '.manufacturer-table th,.manufacturer-table td{padding:.55rem .65rem;border-bottom:1px solid #8884;text-align:left;white-space:nowrap}'
        '.manufacturer-table thead th{position:sticky;top:0;background:Canvas;z-index:1}'
        '.manufacturer-table th[scope="row"]{position:static;background:transparent}'
        '.manufacturer-row{cursor:pointer}'
        '.manufacturer-row:hover{background:#2878c812}'
        '.manufacturer-row.selected{background:#2878c81f;font-weight:700}'
        '.manufacturer-result-count{margin:.65rem 0 0;font-size:.9rem;opacity:.8;flex:0 0 auto}'
        '.manufacturer-inspector{min-width:0;min-height:0;height:100%;padding:1rem;display:flex;flex-direction:column;overflow:hidden;border-left:1px solid #8886}'
        '.manufacturer-inspector>h2{margin-top:0;flex:0 0 auto}'
        '#manufacturer-inspector-content{min-height:0;flex:1 1 auto;display:flex;flex-direction:column;overflow:hidden}'
        '.manufacturer-inspector-fixed{flex:0 0 auto;min-height:0}'
        '.manufacturer-properties{display:grid;grid-template-columns:1fr 1.35fr;gap:.45rem .7rem;margin:0 0 .8rem}'
        '.manufacturer-properties dt{font-weight:700}'
        '.manufacturer-properties dd{margin:0;min-width:0;overflow-wrap:anywhere}'
        '.manufacturer-inspector-fixed>h3{margin:.6rem 0 .45rem}'
        '.manufacturer-series-wrap{max-height:220px;overflow:auto;border:1px solid #8886;border-radius:.35rem}'
        '.manufacturer-series-table{border-collapse:collapse;width:100%;min-width:520px}'
        '.manufacturer-series-table th,.manufacturer-series-table td{padding:.45rem .5rem;border-bottom:1px solid #8884;text-align:left;white-space:nowrap}'
        '.manufacturer-series-table thead th{position:sticky;top:0;background:Canvas}'
        '.manufacturer-series-table th[scope="row"]{position:static;background:transparent}'
        '.manufacturer-device-section{min-height:0;flex:1 1 auto;display:flex;flex-direction:column;margin-top:.8rem}'
        '.manufacturer-device-section>h3{margin:.2rem 0 .5rem;flex:0 0 auto}'
        '.manufacturer-device-scroll{min-height:0;flex:1 1 auto;overflow-y:auto;overflow-x:hidden;scrollbar-gutter:stable;padding-right:.2rem}'
        '.manufacturer-device-ids{list-style:none;padding:0;margin:0;display:grid;gap:.4rem}'
        '.manufacturer-device-ids li{padding:.35rem .45rem;border:1px solid #8885;border-radius:.3rem}'
        '.manufacturer-device-ids code{white-space:normal;overflow-wrap:anywhere;word-break:break-word}'
        '.manufacturer-empty{padding:.7rem;border:1px dashed #8888;text-align:center}'
        '@media(max-width:1050px){.manufacturer-workspace{grid-template-columns:1fr}.manufacturer-inspector{height:auto;overflow:auto;border-left:0;border-top:1px solid #8886}'
        '#manufacturer-inspector-content{overflow:visible}.manufacturer-device-scroll{max-height:18rem}.manufacturer-filters{grid-template-columns:repeat(2,minmax(120px,1fr))}}'
        '</style>'
        '<section class="page" id="page-hersteller"><div class="manufacturer-workspace">'
        '<div class="manufacturer-main">'
        '<h2 class="manufacturer-title">Hersteller</h2>'
        '<p class="manufacturer-subtitle">Read-only Übersicht aus dem technischen Gerätekatalog. Hersteller, Serien und Gerätezuordnungen bleiben damit ohne zweite Datenpflege nachvollziehbar.</p>'
        '<div class="manufacturer-filters">'
        f'<label>Hersteller ({len(items)})<select id="manufacturer-page-filter-name"><option value="">Alle</option>{_options(manufacturer_names)}</select></label>'
        f'<label>Serien ({total_series})<select id="manufacturer-page-filter-series"><option value="">Alle</option>{_options(series_names)}</select></label>'
        f'<label>Gerätefamilien ({len(families)})<select id="manufacturer-page-filter-family"><option value="">Alle</option>{_options(families)}</select></label>'
        f'<label>Quellenstatus ({len(source_labels)})<select id="manufacturer-page-filter-source"><option value="">Alle</option>{_options(source_labels)}</select></label>'
        '</div>'
        '<div class="manufacturer-table-wrap"><table class="manufacturer-table" id="manufacturer-overview">'
        '<thead><tr><th>Hersteller</th><th>Serien</th><th>Geräte</th><th>Gerätefamilien</th><th>Quellenstatus</th></tr></thead>'
        f'<tbody>{table_rows}</tbody></table></div>'
        f'<p class="manufacturer-result-count" id="manufacturer-result-count">{len(items)} Hersteller · {total_series} Serien · {total_devices} Geräte</p>'
        '</div>'
        '<section class="manufacturer-inspector"><h2>Eigenschaften</h2>'
        '<div id="manufacturer-inspector-content"><p>Hersteller auswählen.</p></div></section>'
        f'{"".join(templates)}'
        '</div></section>'
        '<script type="text/javascript">(()=>{'
        'const table=document.getElementById("manufacturer-overview");if(!table)return;'
        'const rows=[...table.querySelectorAll(".manufacturer-row")];'
        'const inspector=document.getElementById("manufacturer-inspector-content");'
        'const count=document.getElementById("manufacturer-result-count");'
        'const nameFilter=document.getElementById("manufacturer-page-filter-name");'
        'const seriesFilter=document.getElementById("manufacturer-page-filter-series");'
        'const familyFilter=document.getElementById("manufacturer-page-filter-family");'
        'const sourceFilter=document.getElementById("manufacturer-page-filter-source");'
        'let selected=null;'
        'function values(row,key){try{return JSON.parse(row.dataset[key]||"[]");}catch(_){return[];}}'
        'function reset(){rows.forEach(row=>row.classList.remove("selected"));selected=null;inspector.innerHTML="<p>Hersteller auswählen.</p>";}'
        'function select(row){rows.forEach(item=>item.classList.remove("selected"));row.classList.add("selected");selected=row;'
        'const template=document.getElementById(`manufacturer-inspector-${row.dataset.index}`);inspector.innerHTML=template?template.innerHTML:"<p>Keine Detaildaten vorhanden.</p>";}'
        'function apply(){let visible=0;rows.forEach(row=>{const show=(!nameFilter.value||row.dataset.manufacturer===nameFilter.value)'
        '&&(!seriesFilter.value||values(row,"series").includes(seriesFilter.value))'
        '&&(!familyFilter.value||values(row,"families").includes(familyFilter.value))'
        '&&(!sourceFilter.value||values(row,"sources").includes(sourceFilter.value));row.hidden=!show;if(show)visible+=1;});'
        'if(selected&&selected.hidden)reset();count.textContent=`${visible} Hersteller sichtbar`;}'
        'rows.forEach(row=>{row.addEventListener("click",()=>select(row));row.addEventListener("keydown",event=>{if(event.key==="Enter"||event.key===" "){event.preventDefault();select(row);}});});'
        '[nameFilter,seriesFilter,familyFilter,sourceFilter].forEach(filter=>filter.addEventListener("change",apply));apply();'
        '})();</script>'
    )
