from tools.generate_z_cockpit import cockpit_devices, render_html


def test_cockpit_uses_catalog_devices():
    devices = cockpit_devices()
    assert devices
    assert any(item["id"] == "generic.mcb-1p-b16-template" for item in devices)
    assert all(item["family"] for item in devices)
    assert all(item["symbol"] for item in devices)


def test_generic_manufacturer_is_shown_in_german():
    device = next(item for item in cockpit_devices() if item["id"] == "generic.mcb-1p-b16-template")
    assert device["manufacturer"] == "Herstellerneutral"
    assert device["name"] == "Leitungsschutzschalter"
    assert device["current"] == "16 A"
    assert device["curve"] == "B"


def test_rendered_cockpit_contains_filters_and_catalog_data():
    html = render_html(cockpit_devices())
    assert 'lang="de"' in html
    assert "Gerätefamilie" in html
    assert "Hersteller" in html
    assert "Charakteristik" in html
    assert "generic.mcb-1p-b16-template" in html
    assert "Datenquelle: technischer Gerätekatalog" in html
