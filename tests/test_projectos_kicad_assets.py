import pytest

from projectos.identifiers import BusinessId, ObjectId
from projectos.kicad_assets import (
    KiCadAssetReference,
    KiCadAssetStatus,
    KiCadAssetTargetType,
    KiCadAssetType,
    KiCadLibraryReference,
    ensure_unique_kicad_asset,
)


def _asset(*, asset_id="KICAD-ASSET-0001", status=KiCadAssetStatus.DRAFT):
    return KiCadAssetReference(
        object_id=ObjectId.new(),
        asset_id=BusinessId(asset_id),
        asset_type=KiCadAssetType.SYMBOL,
        target_type=KiCadAssetTargetType.CATALOG_DEVICE,
        target_id=BusinessId("CAT-MCB-0001"),
        reference=KiCadLibraryReference("ProjectOS", "MCB_1P", "symbols/projectos.kicad_sym"),
        status=status,
    )


def test_bibliotheksreferenz_liefert_qualifizierten_namen():
    reference = KiCadLibraryReference("ProjectOS", "MCB_1P")
    assert reference.qualified_name == "ProjectOS:MCB_1P"


def test_absolute_und_aufsteigende_pfade_werden_abgelehnt():
    with pytest.raises(ValueError, match="ERR-KICAD-0003"):
        KiCadLibraryReference("ProjectOS", "MCB_1P", "/tmp/model.step")
    with pytest.raises(ValueError, match="ERR-KICAD-0003"):
        KiCadLibraryReference("ProjectOS", "MCB_1P", "../model.step")


def test_aktivierung_und_ausmusterung_erhoehen_revision():
    active = _asset().activate()
    retired = active.retire()
    assert active.status is KiCadAssetStatus.ACTIVE
    assert active.revision == 1
    assert retired.status is KiCadAssetStatus.RETIRED
    assert retired.revision == 2


def test_ausgemustertes_artefakt_darf_nicht_reaktiviert_werden():
    with pytest.raises(ValueError, match="ERR-KICAD-0005"):
        _asset(status=KiCadAssetStatus.RETIRED).activate()


def test_sha256_wird_validiert_und_normalisiert():
    checksum = "A" * 64
    asset = KiCadAssetReference(
        object_id=ObjectId.new(),
        asset_id=BusinessId("KICAD-ASSET-0002"),
        asset_type=KiCadAssetType.MODEL_3D,
        target_type=KiCadAssetTargetType.MANUFACTURER_PRODUCT,
        target_id=BusinessId("PRD-0001"),
        reference=KiCadLibraryReference("ProjectOS3D", "S201-B16", "models/s201-b16.step"),
        checksum_sha256=checksum,
    )
    assert asset.checksum_sha256 == checksum.lower()


def test_doppelte_zuordnung_wird_abgelehnt():
    first = _asset()
    second = _asset(asset_id="KICAD-ASSET-0003")
    with pytest.raises(ValueError, match="ERR-KICAD-0007"):
        ensure_unique_kicad_asset((first,), second)
