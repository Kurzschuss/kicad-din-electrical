from uuid import UUID

import pytest

from projectos.device_catalog import (
    CatalogDevice,
    CatalogDeviceStatus,
    DeviceCategory,
    DeviceProperty,
)
from projectos.identifiers import BusinessId, ObjectId


def _device(*, properties=(), status=CatalogDeviceStatus.DRAFT):
    return CatalogDevice(
        object_id=ObjectId(UUID("11111111-1111-4111-8111-111111111111")),
        catalog_id=BusinessId("CAT-DEVICE-0001"),
        name="Leitungsschutzschalter",
        category=DeviceCategory.MCB,
        description="Herstellerunabhängiger Katalogeintrag",
        properties=properties,
        tags=frozenset({" Schutzgerät ", "DIN"}),
        status=status,
    )


def test_kataloggeraet_normalisiert_text_tags_und_eigenschaften():
    device = _device(properties=(DeviceProperty("nominal_current", "16", "A"),))

    assert device.name == "Leitungsschutzschalter"
    assert device.tags == frozenset({"schutzgerät", "din"})
    assert device.properties[0].key == "nominal_current"


def test_eigenschaftsschluessel_muessen_snake_case_verwenden():
    with pytest.raises(ValueError, match="snake_case"):
        DeviceProperty("Nominal Current", "16", "A")


def test_doppelte_eigenschaftsschluessel_werden_abgelehnt():
    with pytest.raises(ValueError, match="eindeutig"):
        _device(
            properties=(
                DeviceProperty("nominal_current", "16", "A"),
                DeviceProperty("nominal_current", "20", "A"),
            )
        )


def test_eigenschaft_wird_deterministisch_gesetzt_und_revision_erhoeht():
    device = _device(properties=(DeviceProperty("rated_voltage", "230", "V"),))

    changed = device.set_property(DeviceProperty("nominal_current", "16", "A"))

    assert tuple(item.key for item in changed.properties) == ("nominal_current", "rated_voltage")
    assert changed.revision == 1
    assert device.revision == 0


def test_aktivierung_benoetigt_mindestens_eine_technische_eigenschaft():
    with pytest.raises(ValueError, match="ERR-CAT-0004"):
        _device().activate()


def test_geraet_kann_aktiviert_und_ausgemustert_werden():
    device = _device(properties=(DeviceProperty("nominal_current", "16", "A"),))

    active = device.activate()
    retired = active.retire()

    assert active.status is CatalogDeviceStatus.ACTIVE
    assert active.revision == 1
    assert retired.status is CatalogDeviceStatus.RETIRED
    assert retired.revision == 2


def test_ausgemustertes_geraet_kann_nicht_reaktiviert_werden():
    device = _device(properties=(DeviceProperty("nominal_current", "16", "A"),)).retire()

    with pytest.raises(ValueError, match="ERR-CAT-0003"):
        device.activate()


def test_letzte_eigenschaft_eines_aktiven_geraets_darf_nicht_entfernt_werden():
    device = _device(
        properties=(DeviceProperty("nominal_current", "16", "A"),),
        status=CatalogDeviceStatus.ACTIVE,
    )

    with pytest.raises(ValueError, match="ERR-CAT-0002"):
        device.remove_property("nominal_current")


def test_umbenennung_ist_unveraenderlich_und_revisionswirksam():
    device = _device()

    renamed = device.rename("MCB 16 A")

    assert renamed.name == "MCB 16 A"
    assert renamed.revision == 1
    assert device.name == "Leitungsschutzschalter"
