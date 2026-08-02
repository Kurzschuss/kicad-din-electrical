import json
from pathlib import Path

from tools.generate_html_reference import collect_devices, collect_site_data, render_html


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


def test_collect_devices_resolves_german_taxonomy_names(tmp_path: Path):
    device_root = tmp_path / "devices"
    device_root.mkdir()
    taxonomy = tmp_path / "families.json"
    taxonomy.write_text(
        json.dumps({
            "families": [
                {"id": "protection.mcb", "group": "Schutzgeräte", "name": "Leitungsschutzschalter"}
            ]
        }),
        encoding="utf-8",
    )
    (device_root / "test.yaml").write_text(
        json.dumps({
            "id": "generic.mcb.b16",
            "manufacturer": "Generic",
            "series": "Template",
            "part_number": "B16",
            "device_type": "Leitungsschutzschalter",
            "function_group": "protection.mcb",
            "symbol": "Z_MCB:MCB",
            "footprint_policy": "optional",
            "source_status": "template"
        }),
        encoding="utf-8",
    )

    devices, groups = collect_devices(device_root, taxonomy)

    assert groups == ["Schutzgeräte"]
    assert devices[0]["family"] == "Leitungsschutzschalter"
    assert devices[0]["source_status"] == "template"


def test_render_html_escapes_content_and_contains_filters():
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
        "devices": [
            {
                "id": "generic.test",
                "manufacturer": "Generic",
                "series": "Test",
                "part_number": "T-1",
                "device_type": "Testgerät",
                "family_id": "protection.mcb",
                "group": "Schutzgeräte",
                "family": "Leitungsschutzschalter",
                "symbol": "Z_Test:Switch",
                "footprint_policy": "optional",
                "footprint": "—",
                "source_status": "template",
            }
        ],
        "device_groups": ["Schutzgeräte"],
    }

    html = render_html(data)

    assert '<html lang="de">' in html
    assert 'id="search"' in html
    assert 'id="group"' in html
    assert 'id="devices"' in html
    assert "Z_&lt;Test&gt;" in html
    assert "A&amp;B" in html
    assert "Schutzgeräte" in html
    assert "Leitungsschutzschalter" in html
    assert "Keine blockierenden Fehler" in html
