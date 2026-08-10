from __future__ import annotations

from html import escape

from .library_browser import SymbolLibrary, collect_symbol_libraries


def _state(value: bool, present: str = "Vorhanden", missing: str = "Fehlt") -> str:
    return present if value else missing


def _yes_no(value: bool) -> str:
    return "Ja" if value else "Nein"


def _preview_state(library: SymbolLibrary) -> str:
    if library.symbol_count == 0 or library.complete_preview_count == 0:
        return "Keine"
    if library.complete_preview_count == library.symbol_count:
        return "Vollständig"
    return "Teilweise"


def _select_options(values: tuple[str, ...]) -> str:
    return "".join(
        f'<option value="{escape(value)}">{escape(value)}</option>'
        for value in values
    )


def _symbol_table(library: SymbolLibrary) -> str:
    rows: list[str] = []
    for symbol in library.symbols:
        devices = ", ".join(escape(device_id) for device_id in symbol.device_ids) or "Keine Gerätezuordnung"
        footprint = escape(symbol.footprint_name) if symbol.footprint_name else "Nicht zugeordnet"
        rows.append(
            f'<tr data-symbol="{escape(symbol.reference)}">'
            f'<th scope="row"><code>{escape(symbol.reference)}</code></th>'
            f'<td>{symbol.device_count}</td><td>{footprint}</td>'
            f'<td>{_state(symbol.symbol_preview_available)}</td>'
            f'<td>{_state(symbol.footprint_preview_available)}</td>'
            f'<td>{devices}</td></tr>'
        )
    if not rows:
        return '<p class="library-empty">Diese Bibliothek enthält derzeit keine Top-Level-Symbole.</p>'
    return (
        '<div class="library-symbol-table-wrap"><table class="library-table">'
        '<thead><tr><th>Symbol</th><th>Geräte</th><th>Footprint</th>'
        '<th>Symbolvorschau</th><th>Footprintvorschau</th><th>Geräte-IDs</th></tr></thead>'
        f'<tbody>{"".join(rows)}</tbody></table></div>'
    )


def library_page_html(libraries: tuple[SymbolLibrary, ...] | None = None) -> str:
    """Rendert die Bibliotheken als filterbare Tabellenansicht mit Detailbereich."""
    items = collect_symbol_libraries() if libraries is None else libraries
    total_symbols = sum(library.symbol_count for library in items)
    total_devices = sum(library.device_count for library in items)
    total_footprints = sum(library.footprint_count for library in items)
    total_complete = sum(library.complete_preview_count for library in items)

    overview_rows: list[str] = []
    detail_templates: list[str] = []
    for index, library in enumerate(items):
        has_symbols = library.symbol_count > 0
        has_devices = library.device_count > 0
        has_footprints = library.footprint_count > 0
        preview_state = _preview_state(library)
        template_id = f"library-detail-{index}"
        overview_rows.append(
            f'<tr class="library-row" data-library="{escape(library.name)}" '
            f'data-symbols="{_yes_no(has_symbols)}" data-devices="{_yes_no(has_devices)}" '
            f'data-footprints="{_yes_no(has_footprints)}" data-preview="{preview_state}" '
            f'data-detail-template="{template_id}">'
            f'<td><strong>{escape(library.name)}</strong></td>'
            f'<td>{library.symbol_count}</td><td>{library.device_count}</td>'
            f'<td>{library.footprint_count}</td><td>{library.complete_preview_count}</td>'
            f'<td>{preview_state}</td></tr>'
        )
        detail_templates.append(
            f'<template id="{template_id}">'
            '<dl class="library-properties">'
            f'<dt>Bibliothek</dt><dd><code>{escape(library.name)}</code></dd>'
            f'<dt>Symbole</dt><dd>{library.symbol_count}</dd>'
            f'<dt>Gerätezuordnungen</dt><dd>{library.device_count}</dd>'
            f'<dt>Footprints</dt><dd>{library.footprint_count}</dd>'
            f'<dt>Vorschaupaare</dt><dd>{library.complete_preview_count}</dd>'
            f'<dt>Vorschau-Status</dt><dd>{preview_state}</dd>'
            '</dl>'
            '<h3>Symbole</h3>'
            f'{_symbol_table(library)}'
            '</template>'
        )

    library_names = tuple(sorted((library.name for library in items), key=str.casefold))
    preview_states = tuple(
        state for state in ("Vollständig", "Teilweise", "Keine")
        if any(_preview_state(library) == state for library in items)
    )

    return (
        '<style>'
        '.workspace{position:relative}'
        '#page-geraete{padding:0}'
        '#page-geraete .device-main,#page-geraete .details{padding-top:.75rem}'
        '#page-geraete .device-main>h2,#page-geraete .details>h2{margin-top:0}'
        '#page-bibliotheken.active{position:absolute;inset:0;display:flex;flex-direction:column;'
        'min-height:0;overflow:hidden;padding:0}'
        '.library-list-scroll{flex:1 1 auto;min-height:0;overflow:hidden;scrollbar-gutter:stable}'
        '.library-workspace{display:grid;grid-template-columns:minmax(0,1fr) 430px;'
        'height:100%;min-height:0;overflow:hidden}'
        '.library-main,.library-details{min-width:0;min-height:0;padding:1rem}'
        '.library-main{display:flex;flex-direction:column;overflow:hidden}'
        '.library-details{overflow:auto;border-left:1px solid #8886}'
        '.library-page-title{margin:0 0 .85rem;flex:0 0 auto}'
        '.library-page-title small{font-size:.62em;font-weight:400;opacity:.75}'
        '.library-main>h3,.library-details>h2{margin-top:0}'
        '.library-main>h3{flex:0 0 auto}'
        '.library-details>.library-card{margin:0;padding:.85rem}'
        '.library-filters{display:grid;grid-template-columns:repeat(5,minmax(120px,1fr));'
        'gap:.6rem;margin-bottom:.8rem;flex:0 0 auto}'
        '.library-overview-wrap{flex:1 1 auto;min-height:0;overflow:auto;border:1px solid #8886}'
        '.library-overview-table{border-collapse:collapse;width:100%;min-width:820px}'
        '.library-overview-table th,.library-overview-table td{padding:.55rem .65rem;'
        'border-bottom:1px solid #8884;text-align:left;white-space:nowrap}'
        '.library-overview-table thead th{position:sticky;top:0;background:Canvas;z-index:1}'
        '.library-row{cursor:pointer}'
        '.library-row:hover{background:#2878c812}'
        '.library-row.selected{background:#2878c81f;font-weight:700}'
        '.library-result-count{margin:.65rem 0 0;font-size:.9rem;opacity:.8;flex:0 0 auto}'
        '.library-properties{margin-top:0}'
        '.library-symbol-table-wrap{overflow:auto;border:1px solid #8886;border-radius:.35rem}'
        '.library-symbol-table-wrap .library-table{border-collapse:collapse;width:100%;min-width:780px}'
        '.library-symbol-table-wrap .library-table th,.library-symbol-table-wrap .library-table td{padding:.5rem .6rem;'
        'border-bottom:1px solid #8884;text-align:left;white-space:nowrap}'
        '.library-symbol-table-wrap .library-table thead th{position:sticky;top:0;background:Canvas}'
        '.library-symbol-table-wrap .library-table th[scope="row"]{position:static;background:transparent}'
        '.library-empty{padding:1rem;border:1px dashed #8888;text-align:center}'
        '@media(max-width:1050px){.library-workspace{grid-template-columns:1fr}'
        '.library-details{border-left:0;border-top:1px solid #8886}'
        '.library-filters{grid-template-columns:repeat(2,minmax(120px,1fr))}}'
        '</style>'
        '<section class="page" id="page-bibliotheken">'
        '<div class="library-list-scroll"><div class="library-workspace">'
        '<div class="library-main">'
        '<h2 class="library-page-title">Bibliotheken '
        '<small>(Übersicht aus Symbolbibliotheken, Gerätekatalog, Footprint-Zuordnung und erzeugten Vorschauen.)</small></h2>'
        '<h3>Bibliotheksliste</h3>'
        '<div class="library-filters">'
        f'<label>Bibliothek ({len(items)})<select id="library-filter-name"><option value="">Alle</option>'
        f'{_select_options(library_names)}</select></label>'
        f'<label>Symbole vorhanden ({total_symbols})<select id="library-filter-symbols"><option value="">Alle</option>'
        '<option>Ja</option><option>Nein</option></select></label>'
        f'<label>Gerätezuordnung ({total_devices})<select id="library-filter-devices"><option value="">Alle</option>'
        '<option>Ja</option><option>Nein</option></select></label>'
        f'<label>Footprints ({total_footprints})<select id="library-filter-footprints"><option value="">Alle</option>'
        '<option>Ja</option><option>Nein</option></select></label>'
        f'<label>Vorschauen ({total_complete})<select id="library-filter-preview"><option value="">Alle</option>'
        f'{_select_options(preview_states)}</select></label>'
        '</div>'
        '<div class="library-overview-wrap"><table class="library-overview-table" id="library-overview">'
        '<thead><tr><th>Bibliothek</th><th>Symbole</th><th>Gerätezuordnungen</th>'
        '<th>Footprints</th><th>Vorschaupaare</th><th>Vorschau-Status</th></tr></thead>'
        f'<tbody>{"".join(overview_rows)}</tbody></table></div>'
        f'<p class="library-result-count" id="library-result-count">{len(items)} Bibliothek(en)</p>'
        '</div>'
        '<section class="library-details"><h2>Bibliotheksdetails</h2>'
        '<div class="library-card"><div id="library-detail-content">'
        '<p>Bitte eine Bibliothek auswählen.</p></div></div>'
        f'{"".join(detail_templates)}</section></div></div>'
        '</section>'
        '<script type="text/javascript">'
        '(()=>{'
        'const rows=[...document.querySelectorAll("#library-overview .library-row")];'
        'const detail=document.getElementById("library-detail-content");'
        'const count=document.getElementById("library-result-count");'
        'const filters={'
        'library:[document.getElementById("library-filter-name"),"library"],'
        'symbols:[document.getElementById("library-filter-symbols"),"symbols"],'
        'devices:[document.getElementById("library-filter-devices"),"devices"],'
        'footprints:[document.getElementById("library-filter-footprints"),"footprints"],'
        'preview:[document.getElementById("library-filter-preview"),"preview"]};'
        'let selected=null;'
        'function clearSelection(){rows.forEach(row=>row.classList.remove("selected"));selected=null;'
        'detail.innerHTML="<p>Bitte eine Bibliothek auswählen.</p>";}'
        'function applyFilters(){let visible=0;rows.forEach(row=>{const show=Object.values(filters).every('
        '([select,key])=>!select.value||row.dataset[key]===select.value);row.hidden=!show;if(show)visible+=1;});'
        'count.textContent=`${visible} Bibliothek(en)`;if(selected&&selected.hidden)clearSelection();}'
        'Object.values(filters).forEach(([select])=>select.addEventListener("change",applyFilters));'
        'rows.forEach(row=>row.addEventListener("click",()=>{rows.forEach(item=>item.classList.remove("selected"));'
        'row.classList.add("selected");selected=row;const template=document.getElementById(row.dataset.detailTemplate);'
        'detail.innerHTML=template?template.innerHTML:"<p>Keine Detaildaten verfügbar.</p>";}));'
        'applyFilters();'
        '})();'
        '</script>'
    )
