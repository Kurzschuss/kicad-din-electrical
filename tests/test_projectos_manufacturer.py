import pytest

from projectos.identifiers import BusinessId, ObjectId
from projectos.manufacturer import (
    Manufacturer,
    ManufacturerReference,
    ManufacturerStatus,
    ProductSeries,
    ensure_unique_series_name,
)


def _manufacturer(**changes):
    values = {
        "object_id": ObjectId.new(),
        "manufacturer_id": BusinessId("MAN-ABB"),
        "name": "ABB",
        "short_name": "ABB",
        "country_code": "CH",
        "website": "https://global.abb",
    }
    values.update(changes)
    return Manufacturer(**values)


def _series(manufacturer_id=BusinessId("MAN-ABB"), **changes):
    values = {
        "object_id": ObjectId.new(),
        "series_id": BusinessId("SER-S200"),
        "manufacturer_id": manufacturer_id,
        "name": "S200",
    }
    values.update(changes)
    return ProductSeries(**values)


def test_hersteller_normalisiert_name_land_und_urls():
    manufacturer = _manufacturer(name="  ABB  ", country_code="ch")
    assert manufacturer.name == "ABB"
    assert manufacturer.country_code == "CH"
    assert manufacturer.status is ManufacturerStatus.ACTIVE


def test_hersteller_benoetigt_name():
    with pytest.raises(ValueError, match="ERR-MAN-0001"):
        _manufacturer(name="   ")


def test_ungueltige_website_wird_abgelehnt():
    with pytest.raises(ValueError, match="website"):
        _manufacturer(website="abb.example")


def test_umbenennung_und_statuswechsel_erhoehen_revision():
    manufacturer = _manufacturer()
    renamed = manufacturer.rename("ABB Schweiz", short_name="ABB")
    inactive = renamed.deactivate()
    active = inactive.activate()
    assert renamed.revision == 1
    assert inactive.revision == 2
    assert active.revision == 3
    assert active.status is ManufacturerStatus.ACTIVE


def test_serienname_ist_je_hersteller_eindeutig():
    existing = (_series(),)
    duplicate = _series(series_id=BusinessId("SER-S200-ALT"), name="s200")
    with pytest.raises(ValueError, match="ERR-MAN-0004"):
        ensure_unique_series_name(existing, duplicate)


def test_gleicher_serienname_bei_anderem_hersteller_ist_zulaessig():
    existing = (_series(),)
    candidate = _series(
        manufacturer_id=BusinessId("MAN-SIEMENS"),
        series_id=BusinessId("SER-SIEMENS-S200"),
    )
    ensure_unique_series_name(existing, candidate)


def test_herstellerreferenz_verknuepft_kataloggeraet_hersteller_und_serie():
    manufacturer = _manufacturer()
    series = _series()
    reference = ManufacturerReference.create(
        object_id=ObjectId.new(),
        reference_id=BusinessId("MREF-0001"),
        catalog_device_id=BusinessId("CAT-MCB-B16-1P"),
        manufacturer=manufacturer,
        series=series,
        product_name="S201-B16",
    )
    assert reference.manufacturer_id == manufacturer.manufacturer_id
    assert reference.series_id == series.series_id
    assert reference.product_name == "S201-B16"


def test_serie_eines_anderen_herstellers_wird_abgelehnt():
    manufacturer = _manufacturer()
    foreign_series = _series(manufacturer_id=BusinessId("MAN-SIEMENS"))
    with pytest.raises(ValueError, match="ERR-MAN-0002"):
        ManufacturerReference.create(
            object_id=ObjectId.new(),
            reference_id=BusinessId("MREF-0002"),
            catalog_device_id=BusinessId("CAT-MCB-B16-1P"),
            manufacturer=manufacturer,
            series=foreign_series,
        )


def test_inaktiver_hersteller_und_inaktive_serie_werden_abgelehnt():
    with pytest.raises(ValueError, match="ERR-MAN-0003"):
        ManufacturerReference.create(
            object_id=ObjectId.new(),
            reference_id=BusinessId("MREF-0003"),
            catalog_device_id=BusinessId("CAT-MCB-B16-1P"),
            manufacturer=_manufacturer().deactivate(),
        )

    with pytest.raises(ValueError, match="ERR-MAN-0003"):
        ManufacturerReference.create(
            object_id=ObjectId.new(),
            reference_id=BusinessId("MREF-0004"),
            catalog_device_id=BusinessId("CAT-MCB-B16-1P"),
            manufacturer=_manufacturer(),
            series=_series().deactivate(),
        )
