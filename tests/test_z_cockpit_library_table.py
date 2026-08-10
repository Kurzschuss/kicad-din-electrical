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
        three_d_model_available=False,
        three_d_preview_available=True,
        three_d_preview_status="Hüllkörper",
    )
    return SymbolLibrary(
        name="Z_Test",
        file=Path("symbols/Z_Test.kicad_sym"),
        symbols=(symbol,),
        symbol_count=1,
        device_count=1,
        footprint_count=1,
        complete_preview_count=1,
        three_d_model_count=0,
        three_d_preview_count=1,
    )


def test_library_page_uses_excel_like_filterable_overview_table():
    html = library_page_html((_library(),))
    assert 'id="library-filter-name"' in html
    assert 'id="library-filter-symbols"' in html
    assert 'id="library-filter-devices"' in html
    assert 'id="library-filter-footprints"' in html
    assert 'id="library-filter-preview"' in html
    assert 'id="library-filter-three-d"' in html
    assert 'id="library-overview"' in html
    assert '<th>Bibliothek</th>' in html
    assert '<th>Gerätezuordnungen</th>' in html
    assert '<th>Vorschau-Status</th>' in html
    assert '<th>3D-Modelle</th>' in html
    assert '<th>3D-Vorschauen</th>' in html
    assert 'class="library-row"' in html
    assert 'data-preview="Vollständig"' in html
    assert 'data-three-d="Ja"' in html
    assert '<details class="library-card"' not in html


def test_library_page_moves_summary_counts_into_filter_labels_and_uses_inline_details():
    html = library_page_html((_library(),))
    assert '#page-bibliotheken.active{position:absolute;inset:0;display:flex;flex-direction:column;' in html
    assert 'class="library-page-summary"' not in html
    assert 'class="library-summary"' not in html
    assert '<h2 class="library-page-title">Bibliotheken <small>(' in html
    assert 'Symbol-, Footprint- und 3D-Vorschauen.' in html
    assert 'Bibliothek (1)<select id="library-filter-name"' in html
    assert 'Symbole vorhanden (1)<select id="library-filter-symbols"' in html
    assert 'Gerätezuordnung (1)<select id="library-filter-devices"' in html
    assert 'Footprints (1)<select id="library-filter-footprints"' in html
    assert 'Vorschauen (1)<select id="library-filter-preview"' in html
    assert '3D-Vorschauen (1)<select id="library-filter-three-d"' in html
    assert 'class="library-workspace"' in html
    assert 'class="library-details"' not in html
    assert '<h2>Bibliotheksdetails</h2>' not in html
    assert 'class="library-detail-row" id="library-detail-0" hidden' in html
    assert 'class="library-card library-inline-detail"' in html
    assert '<td colspan="8">' in html
    assert 'aria-expanded="false"' in html
    assert '<code>Z_Test:TEST</code>' in html
    assert 'row.dataset.detailTemplate' in html
    assert 'toggleSelection(row)' in html


def test_library_symbol_table_uses_fixed_inspector_and_scrollable_device_ids():
    html = library_page_html((_library(),))
    assert 'class="library-inspector"' in html
    assert '<h2>Eigenschaften</h2>' in html
    assert 'id="library-symbol-inspector"' in html
    assert 'class="library-symbol-row"' in html
    assert '<th>Geräte-IDs</th>' not in html
    assert 'data-device-ids="[&quot;generic.test.b16&quot;]"' in html
    assert 'data-preview-url="symbol-previews/Z_Test/TEST.svg"' in html
    assert 'data-three-d-status="Hüllkörper"' in html
    assert 'data-three-d-preview-available="Ja"' in html
    assert 'library-inspector-fixed' in html
    assert 'library-device-id-section' in html
    assert 'library-device-id-scroll' in html
    assert 'library-device-ids' in html
    assert 'JSON.parse(row.dataset.deviceIds||"[]")' in html
    assert 'if(first)selectSymbol(first)' in html
    assert 'previewBlock("Symbolvorschau"' in html
    assert 'previewBlock("3D-Vorschau"' in html
    assert 'idsTitle.textContent="Geräte-IDs"' in html
    assert 'idsScroll.className="library-device-id-scroll"' in html


def test_library_page_compacts_device_page_top_spacing():
    html = library_page_html((_library(),))
    assert '#page-geraete{padding:0}' in html
    assert '#page-geraete .device-main>h2,#page-geraete .details>h2{margin-top:0}' in html
