from __future__ import annotations

from html import escape

from .library_browser import SymbolLibrary, collect_symbol_libraries


def _state(value: bool, present: str = "Vorhanden", missing: str = "Fehlt") -> str:
    return present if value else missing


def library_page_html(libraries: tuple[SymbolLibrary, ...] | None = None) -> str:
    """Rendert die geprüften Bibliotheksdaten als eigenständige Cockpit-Seite."""
    items = collect_symbol_libraries() if libraries is None else libraries
    total_symbols = sum(library.symbol_count for library in items)
    total_devices = sum(library.device_count for library in items)
    total_footprints = sum(library.footprint_count for library in items)
    total_complete = sum(library.complete_preview_count for library in items)

    cards: list[str] = []
    for library in items:
        symbols: list[str] = []
        for symbol in library.symbols:
            devices = ", ".join(escape(device_id) for device_id in symbol.device_ids) or "Keine Gerätezuordnung"
            footprint = escape(symbol.footprint_name) if symbol.footprint_name else "Nicht zugeordnet"
            symbols.append(
                f'<tr data-symbol="{escape(symbol.reference)}">'
                f'<th scope="row"><code>{escape(symbol.reference)}</code></th>'
                f'<td>{symbol.device_count}</td><td>{footprint}</td>'
                f'<td>{_state(symbol.symbol_preview_available)}</td>'
                f'<td>{_state(symbol.footprint_preview_available)}</td>'
                f'<td>{devices}</td></tr>'
            )
        cards.append(
            f'<details class="library-card" data-library="{escape(library.name)}">'
            f'<summary><strong>{escape(library.name)}</strong>'
            f'<span>{library.symbol_count} Symbol(e) · {library.device_count} Gerät(e) · '
            f'{library.footprint_count} Footprint(s) · {library.complete_preview_count} vollständige Vorschaupaare</span></summary>'
            '<div class="library-table-wrap"><table class="library-table">'
            '<thead><tr><th>Symbol</th><th>Geräte</th><th>Footprint</th>'
            '<th>Symbolvorschau</th><th>Footprintvorschau</th><th>Geräte-IDs</th></tr></thead>'
            f'<tbody>{"".join(symbols)}</tbody></table></div></details>'
        )

    return (
        '<style>'
        '.workspace{position:relative}'
        '#page-bibliotheken.active{position:absolute;inset:0;display:flex;flex-direction:column;'
        'min-height:0;overflow:hidden;padding:0}'
        '.library-page-summary{flex:0 0 auto;padding:1rem 1rem .75rem;background:Canvas;'
        'border-bottom:1px solid #8884;z-index:2}'
        '.library-page-summary h2{margin-top:0}'
        '.library-page-summary p{margin-bottom:1rem}'
        '.library-list-scroll{flex:1 1 auto;min-height:0;overflow-y:auto;padding:0 1rem 1rem;'
        'scrollbar-gutter:stable}'
        '.library-list-scroll .library-list{margin-top:1rem}'
        '</style>'
        '<section class="page" id="page-bibliotheken">'
        '<div class="library-page-summary"><h2>Bibliotheken</h2>'
        '<p>Übersicht aus Symbolbibliotheken, Gerätekatalog, Footprint-Zuordnung und erzeugten Vorschauen.</p>'
        '<div class="cards library-summary">'
        f'<div class="card">Bibliotheken<strong>{len(items)}</strong></div>'
        f'<div class="card">Symbole<strong>{total_symbols}</strong></div>'
        f'<div class="card">Gerätezuordnungen<strong>{total_devices}</strong></div>'
        f'<div class="card">Footprints<strong>{total_footprints}</strong></div>'
        f'<div class="card">Vorschaupaare<strong>{total_complete}</strong></div></div></div>'
        f'<div class="library-list-scroll"><div class="library-list">{"".join(cards)}</div></div>'
        '</section>'
    )
