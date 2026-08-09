from pathlib import Path

from tools.z_cockpit.library_browser import LibrarySymbol, SymbolLibrary
from tools.z_cockpit.library_page import library_page_html


def _library() -> SymbolLibrary:
    symbol = LibrarySymbol(
        reference="Z_Test:TEST",
        name="TEST",
        device_ids=("generic.test.b16",),
        device_count=1,
        symbol_preview_available=True,
        footprint_name="Z_Test:FP",
        footprint_available=True,
        footprint_preview_available=True,
    )
    return SymbolLibrary(
        name="Z_Test",
        file=Path("symbols/Z_Test.kicad_sym"),
        symbols=(symbol,),
        symbol_count=1,
        device_count=1,
        footprint_count=1,
        complete_preview_count=1,
    )


def test_library_page_uses_excel_like_filterable_overview_table():
    html = library_page_html((_library(),))

    assert 'id="library-filter-name"' in html
    assert 'id="library-filter-symbols"' in html
    assert 'id="library-filter-devices"' in html
    assert 'id="library-filter-footprints"' in html
    assert 'id="library-filter-preview"' in html
    assert 'id="library-overview"' in html
    assert '<th>Bibliothek</th>' in html
    assert '<th>Gerätezuordnungen</th>' in html
    assert '<th>Vorschau-Status</th>' in html
    assert 'class="library-row"' in html
    assert 'data-preview="Vollständig"' in html
    assert '<details class="library-card"' not in html


def test_library_page_keeps_fixed_summary_and_selectable_detail_panel():
    html = library_page_html((_library(),))

    assert '#page-bibliotheken.active{position:absolute;inset:0;display:flex;flex-direction:column;' in html
    assert 'class="library-page-summary"' in html
    assert 'class="library-workspace"' in html
    assert '<h2>Bibliotheksdetails</h2>' in html
    assert 'id="library-detail-0"' in html
    assert '<code>Z_Test:TEST</code>' in html
    assert 'generic.test.b16' in html
    assert 'row.dataset.detailTemplate' in html


def test_library_page_compacts_device_page_top_spacing():
    html = library_page_html((_library(),))

    assert '#page-geraete{padding:0}' in html
    assert '#page-geraete .device-main>h2,#page-geraete .details>h2{margin-top:0}' in html
