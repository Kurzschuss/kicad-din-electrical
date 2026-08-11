from tools.z_cockpit.manufacturer_page import collect_manufacturers, manufacturer_page_html


def _devices():
    return [
        {
            "id": "generic.mcb.b16",
            "manufacturer": "Generic",
            "series": "MCB 1P",
            "family": "Leitungsschutzschalter",
            "source_status": "template",
        },
        {
            "id": "generic.mcb.c16",
            "manufacturer": "Generic",
            "series": "MCB 1P",
            "family": "Leitungsschutzschalter",
            "source_status": "template",
        },
        {
            "id": "abb.s200.b16",
            "manufacturer": "ABB",
            "series": "S200",
            "family": "Leitungsschutzschalter",
            "source_status": "verified",
        },
        {
            "id": "abb.f200.a40",
            "manufacturer": "ABB",
            "series": "F200",
            "family": "Fehlerstrom-Schutzeinrichtungen",
            "source_status": "verified",
        },
    ]


def test_collect_manufacturers_groups_catalog_devices_by_manufacturer_and_series():
    manufacturers = collect_manufacturers(_devices())
    assert [item.display_name for item in manufacturers] == ["ABB", "Herstellerneutral"]

    abb = manufacturers[0]
    assert abb.catalog_name == "ABB"
    assert abb.registry_status == "CATALOG_ONLY"
    assert abb.series_count == 2
    assert abb.device_count == 2
    assert [series.name for series in abb.series] == ["F200", "S200"]
    assert abb.families == ("Fehlerstrom-Schutzeinrichtungen", "Leitungsschutzschalter")
    assert abb.source_states == ("verified",)

    generic = manufacturers[1]
    assert generic.catalog_name == "Generic"
    assert generic.display_name == "Herstellerneutral"
    assert generic.registry_status == "GENERIC"
    assert generic.series_count == 1
    assert generic.series[0].device_count == 2


def test_manufacturer_page_contains_filters_table_and_fixed_inspector():
    html = manufacturer_page_html(collect_manufacturers(_devices()))
    assert 'id="page-hersteller"' in html
    assert 'id="manufacturer-overview"' in html
    assert 'id="manufacturer-page-filter-name"' in html
    assert 'id="manufacturer-page-filter-status"' in html
    assert 'id="manufacturer-page-filter-series"' in html
    assert 'id="manufacturer-page-filter-family"' in html
    assert 'id="manufacturer-page-filter-source"' in html
    assert 'class="manufacturer-inspector"' in html
    assert 'id="manufacturer-inspector-content"' in html
    assert "Herstellerneutral" in html
    assert "ABB" in html
    assert "S200" in html
    assert "F200" in html
    assert "Verifiziert" in html
    assert "Vorlage" in html
    assert "abb.s200.b16" in html
    assert "Nur Gerätekatalog" in html


def test_manufacturer_page_escapes_catalog_values():
    manufacturers = collect_manufacturers(
        [
            {
                "id": "device.safe",
                "manufacturer": "<script>",
                "series": "<Serie>",
                "family": "<Familie>",
                "source_status": "verified",
            }
        ]
    )
    html = manufacturer_page_html(manufacturers)
    assert "<script>" not in html
    assert "&lt;script&gt;" in html
    assert "&lt;Serie&gt;" in html
    assert "&lt;Familie&gt;" in html


def test_repository_manufacturer_page_uses_registry_and_real_catalog():
    manufacturers = collect_manufacturers()
    assert manufacturers
    assert sum(item.device_count for item in manufacturers) > 0

    names = {item.display_name for item in manufacturers}
    assert {
        "ABB",
        "Siemens",
        "Hager",
        "Eaton",
        "Schneider Electric",
        "Doepke",
        "Siedle",
        "Shelly",
        "Theben",
        "Eltako",
        "Klöckner-Moeller",
        "LCN",
        "Phoenix Contact",
        "WAGO",
        "Weidmüller",
        "Pollmann",
        "Herstellerneutral",
    } <= names

    lcn = next(item for item in manufacturers if item.display_name == "LCN")
    assert lcn.legal_name == "Issendorff KG"
    assert lcn.device_count == 0
    assert lcn.series_count == 0
    assert lcn.registry_status == "ACTIVE"

    legacy = next(item for item in manufacturers if item.display_name == "Klöckner-Moeller")
    assert legacy.registry_status == "INACTIVE"
    assert legacy.note and "Eaton" in legacy.note

    html = manufacturer_page_html(manufacturers)
    assert "verifizierten Hersteller-Stammdaten" in html
    assert "Noch keine Gerätezuordnung" in html
    assert "Historisch / inaktiv" in html
    assert "Offizielle Quelle" in html
