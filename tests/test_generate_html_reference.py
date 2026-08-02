from pathlib import Path

from tools.generate_html_reference import collect_site_data, render_html


def test_collect_site_data_lists_symbols_and_footprints(tmp_path: Path):
    symbols = tmp_path / "symbols"
    footprints = tmp_path / "footprints"
    symbols.mkdir()
    pretty = footprints / "Z_Test.pretty"
    pretty.mkdir(parents=True)

    (symbols / "Z_Test.kicad_sym").write_text(
        '''(kicad_symbol_lib
  (symbol "Switch"
    (property "Footprint" "Z_Test:Switch")
    (property "Footprint Policy" "required")
    (property "Description" "Test")
  )
)\n''',
        encoding="utf-8",
    )
    (pretty / "Switch.kicad_mod").write_text('(footprint "Switch")\n', encoding="utf-8")

    data = collect_site_data(symbols, footprints)

    assert data["symbols"][0]["library"] == "Z_Test"
    assert data["symbols"][0]["symbols"] == ["Switch"]
    assert data["symbols"][0]["policy"] == "required"
    assert data["footprints"][0]["count"] == 1


def test_render_html_escapes_content_and_contains_search():
    data = {
        "statistics": {
            "symbol_libraries": 1,
            "symbols": 1,
            "footprint_libraries": 1,
            "footprints": 0,
            "errors": [],
            "warnings": [],
        },
        "symbols": [
            {
                "library": "Z_<Test>",
                "status": "befüllt",
                "symbols": ["A&B"],
                "policy": "optional",
                "footprint": "—",
            }
        ],
        "footprints": [{"library": "Z_Test", "count": 0, "footprints": []}],
    }

    html = render_html(data)

    assert '<html lang="de">' in html
    assert 'id="search"' in html
    assert "Z_&lt;Test&gt;" in html
    assert "A&amp;B" in html
    assert "Keine blockierenden Fehler" in html
