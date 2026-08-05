from pathlib import Path

from tools.z_cockpit.library_browser import LibrarySymbol, SymbolLibrary
from tools.z_cockpit.library_page import library_page_html


def sample_libraries() -> tuple[SymbolLibrary, ...]:
    symbol = LibrarySymbol(
        reference="Z_Test:Schalter",
        name="Schalter",
        device_ids=("generic.test-device",),
        device_count=1,
        symbol_preview_available=True,
        footprint_name="Z_DIN_Module_18mm",
        footprint_available=True,
        footprint_preview_available=False,
    )
    return (
        SymbolLibrary(
            name="Z_Test",
            file=Path("symbols/Z_Test.kicad_sym"),
            symbols=(symbol,),
            symbol_count=1,
            device_count=1,
            footprint_count=1,
            complete_preview_count=0,
        ),
    )


def test_library_page_contains_summary_and_symbol_details():
    html = library_page_html(sample_libraries())
    assert 'id="page-bibliotheken"' in html
    assert "Bibliotheken" in html
    assert "Gerätezuordnungen" in html
    assert 'data-library="Z_Test"' in html
    assert 'data-symbol="Z_Test:Schalter"' in html
    assert "generic.test-device" in html
    assert "Z_DIN_Module_18mm" in html
    assert "Vorhanden" in html
    assert "Fehlt" in html


def test_library_page_escapes_repository_data():
    unsafe = LibrarySymbol(
        reference="Z_Test:<script>",
        name="<script>",
        device_ids=("<device>",),
        device_count=1,
        symbol_preview_available=False,
        footprint_name="<footprint>",
        footprint_available=False,
        footprint_preview_available=False,
    )
    library = SymbolLibrary(
        name="<library>",
        file=Path("symbols/test.kicad_sym"),
        symbols=(unsafe,),
        symbol_count=1,
        device_count=1,
        footprint_count=0,
        complete_preview_count=0,
    )
    html = library_page_html((library,))
    assert "<script>" not in html
    assert "&lt;script&gt;" in html
    assert "&lt;device&gt;" in html
    assert "&lt;footprint&gt;" in html
