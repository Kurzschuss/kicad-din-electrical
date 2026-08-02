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
    assert device["breaking_capacity_ka"] == 6
    assert device["modules"] == 1


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
    assert "16 A" in html
    assert "6 kA" in html
    assert "1 TE" in html
    assert "Ausschaltvermögen" in html
