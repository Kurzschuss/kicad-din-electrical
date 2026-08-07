from uuid import uuid4

from projectos import (
    BusinessId,
    KiCadAssetReference,
    KiCadAssetRequirement,
    KiCadAssetStatus,
    KiCadAssetTargetType,
    KiCadAssetType,
    KiCadLibraryItemSnapshot,
    KiCadLibraryReference,
    KiCadLibraryValidator,
    KiCadTargetRequirements,
    ObjectId,
)


def asset(asset_type: KiCadAssetType, asset_id: str, name: str) -> KiCadAssetReference:
    return KiCadAssetReference(
        object_id=ObjectId(uuid4()),
        asset_id=BusinessId(asset_id),
        asset_type=asset_type,
        target_type=KiCadAssetTargetType.CATALOG_DEVICE,
        target_id=BusinessId("CAT-DEVICE-1"),
        reference=KiCadLibraryReference("ProjectOS", name),
        status=KiCadAssetStatus.ACTIVE,
    )


def test_symbol_ohne_footprint_ist_standardmaessig_gueltig() -> None:
    symbol = asset(KiCadAssetType.SYMBOL, "ASSET-SYMBOL-1", "MCB")
    validator = KiCadLibraryValidator((
        KiCadLibraryItemSnapshot(KiCadAssetType.SYMBOL, "ProjectOS:MCB", ("1", "2")),
    ))

    result = validator.validate(assets=(symbol,))

    assert result.valid
    assert result.findings == ()


def test_fehlender_footprint_ist_nur_bei_pflicht_ein_fehler() -> None:
    symbol = asset(KiCadAssetType.SYMBOL, "ASSET-SYMBOL-1", "MCB")
    validator = KiCadLibraryValidator((
        KiCadLibraryItemSnapshot(KiCadAssetType.SYMBOL, "ProjectOS:MCB"),
    ))

    result = validator.validate(
        assets=(symbol,),
        requirements=KiCadTargetRequirements(footprint=KiCadAssetRequirement.REQUIRED),
    )

    assert not result.valid
    assert any(item.code == "ERR-KICAD-0019" for item in result.findings)


def test_nicht_anwendbarer_footprint_darf_fehlen() -> None:
    symbol = asset(KiCadAssetType.SYMBOL, "ASSET-SYMBOL-1", "MCB")
    validator = KiCadLibraryValidator((
        KiCadLibraryItemSnapshot(KiCadAssetType.SYMBOL, "ProjectOS:MCB"),
    ))

    result = validator.validate(
        assets=(symbol,),
        requirements=KiCadTargetRequirements(footprint=KiCadAssetRequirement.NOT_APPLICABLE),
    )

    assert result.valid


def test_unbekannter_bibliothekseintrag_wird_abgelehnt() -> None:
    symbol = asset(KiCadAssetType.SYMBOL, "ASSET-SYMBOL-1", "UNKNOWN")
    result = KiCadLibraryValidator(()).validate(assets=(symbol,))

    assert not result.valid
    assert any(item.code == "ERR-KICAD-0020" for item in result.findings)
