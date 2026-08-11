import json
from pathlib import Path

from tools.generate_device_catalog_html import collect_devices, render_html


def test_collect_devices_includes_technical_values(tmp_path: Path):
    device_root = tmp_path / "devices"
    device_root.mkdir()
    taxonomy = tmp_path / "families.json"
    taxonomy.write_text(
        json.dumps({"families": [{"id": "protection.mcb", "group": "Schutzgeräte", "name": "Leitungsschutzschalter"}]}),
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
            "poles": 1,
            "rated_current_a": 16,
            "trip_curve": "B",
            "breaking_capacity_ka": 6,
            "modules": 1,
            "symbol": "Z_MCB:MCB",
            "footprint_policy": "optional",
            "source_status": "template"
        }),
        encoding="utf-8",
    )

    data = collect_devices(device_root, taxonomy)
    device = data["devices"][0]

    assert data["groups"] == ["Schutzgeräte"]
    assert data["families"] == ["Leitungsschutzschalter"]
    assert data["source_states"] == ["template"]
    assert device["rated_current_a"] == 16
    assert device["residual_current_ma"] is None
    assert device["rcd_type"] is None
    assert device["breaking_capacity_ka"] == 6
    assert device["modules"] == 1


def test_collect_devices_includes_rcd_values(tmp_path: Path):
    device_root = tmp_path / "devices"
    device_root.mkdir()
    taxonomy = tmp_path / "families.json"
    taxonomy.write_text(
        json.dumps({"families": [{"id": "protection.rcd", "group": "Schutzgeräte", "name": "Fehlerstrom-Schutzeinrichtungen"}]}),
        encoding="utf-8",
    )
    (device_root / "rcd.yaml").write_text(
        json.dumps({
            "id": "generic.rcd.b40-30ma",
            "manufacturer": "Generic",
            "series": "Template RCD",
            "part_number": "RCD-B-40-30",
            "device_type": "Fehlerstrom-Schutzschalter",
            "function_group": "protection.rcd",
            "poles": 2,
            "rated_current_a": 40,
            "residual_current_ma": 30,
            "rcd_type": "B",
            "modules": 2,
            "symbol": "Z_RCD:RCD",
            "footprint_policy": "optional",
            "source_status": "template"
        }),
        encoding="utf-8",
    )

    data = collect_devices(device_root, taxonomy)
    device = data["devices"][0]

    assert device["rcd_type"] == "B"
    assert device["residual_current_ma"] == 30
    assert data["rcd_types"] == ["B"]
    assert data["residual_currents_ma"] == [30]


def test_render_html_contains_technical_columns_and_filters():
    data = {
        "devices": [{
            "id": "generic.mcb.b16",
            "group": "Schutzgeräte",
            "family": "Leitungsschutzschalter",
            "family_id": "protection.mcb",
            "manufacturer": "Generic",
            "series": "Template",
            "part_number": "B16",
            "device_type": "Leitungsschutzschalter",
            "poles": 1,
            "rated_current_a": 16,
            "trip_curve": "B",
            "breaking_capacity_ka": 6,
            "modules": 1,
            "symbol": "Z_MCB:MCB",
            "footprint_policy": "optional",
            "source_status": "template",
        }],
        "groups": ["Schutzgeräte"],
        "families": ["Leitungsschutzschalter"],
        "source_states": ["template"],
    }

    html = render_html(data)

    assert '<html lang="de">' in html
    assert 'id="group"' in html
    assert 'id="family"' in html
    assert 'id="source"' in html
    assert 'id="rcd-type"' in html
    assert 'id="residual-current"' in html
    assert "RCD-Typ" in html
    assert "IΔn" in html
    assert "Alle RCD-Typen" in html
    assert "Alle IΔn" in html
    assert "16 A" in html
    assert "6 kA" in html
    assert "1 TE" in html
    assert "Ausschaltvermögen" in html


def test_render_html_contains_rcd_filter_values_and_row_data():
    data = {
        "devices": [{
            "id": "generic.rcd.b40-30ma",
            "group": "Schutzgeräte",
            "family": "Fehlerstrom-Schutzeinrichtungen",
            "family_id": "protection.rcd",
            "manufacturer": "Generic",
            "series": "Template RCD",
            "part_number": "RCD-B-40-30",
            "device_type": "Fehlerstrom-Schutzschalter",
            "poles": 2,
            "rated_current_a": 40,
            "residual_current_ma": 30,
            "rcd_type": "B",
            "trip_curve": None,
            "breaking_capacity_ka": None,
            "modules": 2,
            "symbol": "Z_RCD:RCD",
            "footprint_policy": "optional",
            "source_status": "template",
        }],
        "groups": ["Schutzgeräte"],
        "families": ["Fehlerstrom-Schutzeinrichtungen"],
        "rcd_types": ["B"],
        "residual_currents_ma": [30],
        "source_states": ["template"],
    }

    html = render_html(data)

    assert 'data-rcd-type="B"' in html
    assert 'data-residual-current="30"' in html
    assert '<option value="B">B</option>' in html
    assert '<option value="30">30 mA</option>' in html
    assert "40 A" in html
    assert "30 mA" in html
