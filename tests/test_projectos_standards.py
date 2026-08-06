from datetime import date

import pytest

from projectos.identifiers import BusinessId, ObjectId
from projectos.standards import (
    ConformityReference,
    ConformityStatus,
    ConformityTargetType,
    StandardBody,
    StandardReference,
    StandardStatus,
    ensure_unique_standard_edition,
)


def _standard(status=StandardStatus.DRAFT):
    return StandardReference(
        object_id=ObjectId.new(),
        standard_id=BusinessId("STD-0001"),
        body=StandardBody.IEC,
        designation="IEC 60898-1",
        title="Leitungsschutzschalter",
        edition="2025",
        publication_date=date(2025, 1, 1),
        status=status,
    )


def test_norm_wird_normalisiert_und_aktiviert():
    standard = StandardReference(
        object_id=ObjectId.new(), standard_id=BusinessId("STD-0001"), body=StandardBody.IEC,
        designation=" IEC 60898-1 ", title=" Leitungsschutzschalter ", edition=" 2025 ",
    )
    active = standard.activate()
    assert active.designation == "IEC 60898-1"
    assert active.status is StandardStatus.ACTIVE
    assert active.revision == 1


def test_zurueckgezogene_norm_darf_nicht_reaktiviert_werden():
    with pytest.raises(ValueError, match="ERR-STD-0004"):
        _standard(StandardStatus.ACTIVE).withdraw().activate()


def test_verifizierte_konformitaet_benoetigt_nachweis():
    with pytest.raises(ValueError, match="ERR-STD-0005"):
        ConformityReference.create(
            object_id=ObjectId.new(), conformity_id=BusinessId("CONF-0001"),
            target_type=ConformityTargetType.CATALOG_DEVICE,
            target_id=BusinessId("CAT-0001"), standard=_standard(StandardStatus.ACTIVE),
            status=ConformityStatus.VERIFIED,
        )


def test_konformitaet_verweist_nur_auf_aktive_norm():
    with pytest.raises(ValueError, match="ERR-STD-0007"):
        ConformityReference.create(
            object_id=ObjectId.new(), conformity_id=BusinessId("CONF-0001"),
            target_type=ConformityTargetType.MANUFACTURER_PRODUCT,
            target_id=BusinessId("PRD-0001"), standard=_standard(),
        )


def test_gueltigkeitszeitraum_wird_geprueft():
    with pytest.raises(ValueError, match="ERR-STD-0006"):
        ConformityReference.create(
            object_id=ObjectId.new(), conformity_id=BusinessId("CONF-0001"),
            target_type=ConformityTargetType.CATALOG_DEVICE,
            target_id=BusinessId("CAT-0001"), standard=_standard(StandardStatus.ACTIVE),
            valid_from=date(2026, 2, 1), valid_until=date(2026, 1, 1),
        )


def test_normausgabe_muss_eindeutig_sein():
    first = _standard()
    duplicate = StandardReference(
        object_id=ObjectId.new(), standard_id=BusinessId("STD-0002"), body=StandardBody.IEC,
        designation="iec 60898-1", title="Andere Beschreibung", edition="2025",
    )
    with pytest.raises(ValueError, match="ERR-STD-0008"):
        ensure_unique_standard_edition((first,), duplicate)
