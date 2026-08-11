from projectos.manufacturer import ManufacturerStatus
from projectos.manufacturer_registry import find_manufacturer_entry, load_manufacturer_registry


def test_manufacturer_registry_contains_requested_verified_seed_set():
    entries = load_manufacturer_registry()

    assert len(entries) == 16
    assert {entry.catalog_name for entry in entries} == {
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
    }
    assert len({str(entry.manufacturer.manufacturer_id) for entry in entries}) == len(entries)
    assert len({str(entry.manufacturer.object_id) for entry in entries}) == len(entries)
    assert all(entry.source_status == "verified" for entry in entries)
    assert all(entry.source_url and entry.source_url.startswith("https://") for entry in entries)
    assert all(entry.manufacturer.website and entry.manufacturer.website.startswith("https://") for entry in entries)


def test_manufacturer_registry_resolves_user_facing_aliases():
    assert find_manufacturer_entry("Phönix Kontakt").catalog_name == "Phoenix Contact"
    assert find_manufacturer_entry("LCN Issendorf").manufacturer.name == "Issendorff KG"
    assert find_manufacturer_entry("Klöckner-Möller").catalog_name == "Klöckner-Moeller"
    assert find_manufacturer_entry("Weidmueller").catalog_name == "Weidmüller"
    assert find_manufacturer_entry("ELTAKO").catalog_name == "Eltako"


def test_kloeckner_moeller_is_kept_as_historical_manufacturer():
    entry = find_manufacturer_entry("Klöckner-Moeller")
    assert entry is not None
    assert entry.manufacturer.status is ManufacturerStatus.INACTIVE
    assert entry.note is not None
    assert "Eaton" in entry.note


def test_lcn_uses_official_issendorff_spelling():
    entry = find_manufacturer_entry("LCN")
    assert entry is not None
    assert entry.manufacturer.name == "Issendorff KG"
    assert entry.manufacturer.country_code == "DE"
    assert "LCN Issendorf" in entry.aliases
