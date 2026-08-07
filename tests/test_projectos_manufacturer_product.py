from projectos.identifiers import BusinessId, ObjectId
from projectos.manufacturer import Manufacturer, ProductSeries
from projectos.manufacturer_product import (
    ManufacturerProduct,
    ProductIdentifier,
    ProductIdentifierType,
    ProductStatus,
    ensure_unique_product_identifiers,
)


def _manufacturer():
    return Manufacturer(ObjectId.new(), BusinessId("MAN-ABB"), "ABB")


def _series(manufacturer):
    return ProductSeries(ObjectId.new(), BusinessId("SER-S200"), manufacturer.manufacturer_id, "S200")


def _mpn(value="S201-B16"):
    return ProductIdentifier(ProductIdentifierType.MANUFACTURER_PART_NUMBER, value)


def test_herstellerprodukt_wird_mit_serie_erstellt():
    manufacturer = _manufacturer()
    product = ManufacturerProduct.create(
        object_id=ObjectId.new(),
        product_id=BusinessId("PRD-ABB-S201-B16"),
        catalog_device_id=BusinessId("CAT-MCB-B16-1P"),
        manufacturer=manufacturer,
        series=_series(manufacturer),
        name="S201-B16",
        identifiers=(_mpn(),),
    )
    assert product.manufacturer_id == manufacturer.manufacturer_id
    assert product.series_id == BusinessId("SER-S200")
    assert product.status is ProductStatus.DRAFT


def test_aktives_produkt_benoetigt_kennung():
    product = ManufacturerProduct.create(
        object_id=ObjectId.new(), product_id=BusinessId("PRD-EMPTY"),
        catalog_device_id=BusinessId("CAT-MCB"), manufacturer=_manufacturer(),
        name="Entwurf", identifiers=(),
    )
    try:
        product.activate()
    except ValueError as exc:
        assert "ERR-PRD-0008" in str(exc)
    else:
        raise AssertionError("Aktivierung ohne Kennung hätte fehlschlagen müssen")


def test_gtin_wird_formal_validiert():
    try:
        ProductIdentifier(ProductIdentifierType.GTIN, "ABC")
    except ValueError as exc:
        assert "ERR-PRD-0002" in str(exc)
    else:
        raise AssertionError("Ungültige GTIN hätte fehlschlagen müssen")


def test_kennungstyp_ist_pro_produkt_eindeutig():
    try:
        ManufacturerProduct.create(
            object_id=ObjectId.new(), product_id=BusinessId("PRD-DUP"),
            catalog_device_id=BusinessId("CAT-MCB"), manufacturer=_manufacturer(),
            name="Doppelt", identifiers=(_mpn("A"), _mpn("B")),
        )
    except ValueError as exc:
        assert "ERR-PRD-0012" in str(exc)
    else:
        raise AssertionError("Doppelter Kennungstyp hätte fehlschlagen müssen")


def test_letzte_kennung_eines_aktiven_produkts_bleibt_erhalten():
    product = ManufacturerProduct.create(
        object_id=ObjectId.new(), product_id=BusinessId("PRD-ACTIVE"),
        catalog_device_id=BusinessId("CAT-MCB"), manufacturer=_manufacturer(),
        name="Aktiv", identifiers=(_mpn(),),
    ).activate()
    try:
        product.remove_identifier(ProductIdentifierType.MANUFACTURER_PART_NUMBER)
    except ValueError as exc:
        assert "ERR-PRD-0010" in str(exc)
    else:
        raise AssertionError("Entfernen der letzten Kennung hätte fehlschlagen müssen")


def test_abgekuendigtes_produkt_wird_nicht_reaktiviert():
    product = ManufacturerProduct.create(
        object_id=ObjectId.new(), product_id=BusinessId("PRD-OLD"),
        catalog_device_id=BusinessId("CAT-MCB"), manufacturer=_manufacturer(),
        name="Alt", identifiers=(_mpn(),),
    ).activate().discontinue()
    try:
        product.activate()
    except ValueError as exc:
        assert "ERR-PRD-0007" in str(exc)
    else:
        raise AssertionError("Reaktivierung hätte fehlschlagen müssen")


def test_externe_kennung_ist_produktuebergreifend_eindeutig():
    manufacturer = _manufacturer()
    first = ManufacturerProduct.create(
        object_id=ObjectId.new(), product_id=BusinessId("PRD-FIRST"),
        catalog_device_id=BusinessId("CAT-MCB"), manufacturer=manufacturer,
        name="Erstes", identifiers=(_mpn(),),
    )
    second = ManufacturerProduct.create(
        object_id=ObjectId.new(), product_id=BusinessId("PRD-SECOND"),
        catalog_device_id=BusinessId("CAT-MCB"), manufacturer=manufacturer,
        name="Zweites", identifiers=(_mpn(),),
    )
    try:
        ensure_unique_product_identifiers((first,), second)
    except ValueError as exc:
        assert "ERR-PRD-0011" in str(exc)
    else:
        raise AssertionError("Doppelte Produktkennung hätte fehlschlagen müssen")
