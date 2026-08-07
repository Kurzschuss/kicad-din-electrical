from uuid import UUID

from projectos import (
    BusinessId, DeviceTerminal, KiCadAssetReference, KiCadAssetStatus,
    KiCadAssetTargetType, KiCadAssetType, KiCadLibraryReference,
    KiCadLibraryTable, KiCadLibraryTableEntry, KiCadLibraryTableType,
    KiCadLocalFileSet, KiCadPinElectricalType, KiCadProjectValidationPipeline,
    KiCadProjectValidationTarget, KiCadStandardConformance, KiCadSymbolPin,
    ObjectId, TerminalFunction, TerminalPinAssignment,
)


def oid(value: int) -> ObjectId:
    return ObjectId(UUID(int=value))


def symbol() -> KiCadAssetReference:
    return KiCadAssetReference(
        object_id=oid(1), asset_id=BusinessId("KICAD-SYM-0001"),
        asset_type=KiCadAssetType.SYMBOL,
        target_type=KiCadAssetTargetType.CATALOG_DEVICE,
        target_id=BusinessId("CAT-MCB-B16"),
        reference=KiCadLibraryReference("ProjectSymbols", "DIN_MCB"),
        status=KiCadAssetStatus.ACTIVE,
    )


def terminal(number: int) -> DeviceTerminal:
    return DeviceTerminal(
        object_id=oid(10 + number), terminal_id=BusinessId(f"TERM-{number:04d}"),
        target_type=KiCadAssetTargetType.CATALOG_DEVICE,
        target_id=BusinessId("CAT-MCB-B16"), designation=str(number),
        function=TerminalFunction.POWER,
    )


def assignment(term: DeviceTerminal, *, exception: bool = False) -> TerminalPinAssignment:
    return TerminalPinAssignment.create(
        object_id=oid(20 + int(term.designation)),
        assignment_id=BusinessId(f"MAP-{int(term.designation):04d}"),
        terminal=term,
        symbol_asset=symbol(),
        pin=KiCadSymbolPin(term.designation, term.designation, KiCadPinElectricalType.PASSIVE),
        conformance=KiCadStandardConformance.EXCEPTION if exception else KiCadStandardConformance.STANDARD,
        exception_reason="Herstellerbibliothek verwendet eine bestätigte Sonderzuordnung." if exception else None,
    )


def symbol_table() -> KiCadLibraryTable:
    return KiCadLibraryTable(
        KiCadLibraryTableType.SYMBOL,
        (KiCadLibraryTableEntry(
            KiCadLibraryTableType.SYMBOL, "ProjectSymbols", "KiCad",
            "${KIPRJMOD}/symbols/project.kicad_sym",
            "/project/symbols/project.kicad_sym",
        ),),
    )


def files() -> KiCadLocalFileSet:
    return KiCadLocalFileSet({
        "/project/symbols/project.kicad_sym": b'''(kicad_symbol_lib (version 20231120)
          (symbol "DIN_MCB" (symbol "DIN_MCB_1_1"
            (pin passive line (name "1") (number "1"))
            (pin passive line (name "2") (number "2")))))''',
    })


def test_validates_complete_project_target() -> None:
    terminals = (terminal(1), terminal(2))
    target = KiCadProjectValidationTarget(
        KiCadAssetTargetType.CATALOG_DEVICE,
        BusinessId("CAT-MCB-B16"),
        (symbol(),), terminals, (assignment(terminals[0]), assignment(terminals[1])),
    )

    result = KiCadProjectValidationPipeline().validate(
        files=files(), targets=(target,), symbol_table=symbol_table(),
    )

    assert result.valid
    assert result.target_count == 1
    assert result.snapshot is not None


def test_reports_missing_required_terminal_assignment() -> None:
    terminals = (terminal(1), terminal(2))
    target = KiCadProjectValidationTarget(
        KiCadAssetTargetType.CATALOG_DEVICE,
        BusinessId("CAT-MCB-B16"),
        (symbol(),), terminals, (assignment(terminals[0]),),
    )

    result = KiCadProjectValidationPipeline().validate(
        files=files(), targets=(target,), symbol_table=symbol_table(),
    )

    assert not result.valid
    assert any(item.code == "ERR-KICAD-0054" for item in result.findings)


def test_documented_exception_is_visible_but_not_invalid() -> None:
    term = terminal(1)
    target = KiCadProjectValidationTarget(
        KiCadAssetTargetType.CATALOG_DEVICE,
        BusinessId("CAT-MCB-B16"),
        (symbol(),), (term,), (assignment(term, exception=True),),
    )

    result = KiCadProjectValidationPipeline().validate(
        files=files(), targets=(target,), symbol_table=symbol_table(),
    )

    assert result.valid
    assert result.exception_count == 1
    assert any(item.code == "INFO-KICAD-0001" for item in result.findings)


def test_symbol_only_project_remains_valid_without_footprint_table() -> None:
    target = KiCadProjectValidationTarget(
        KiCadAssetTargetType.CATALOG_DEVICE,
        BusinessId("CAT-MCB-B16"),
        (symbol(),),
    )

    result = KiCadProjectValidationPipeline().validate(
        files=files(), targets=(target,), symbol_table=symbol_table(),
    )

    assert result.valid
    assert result.snapshot is not None
    assert result.snapshot.footprint_library_count == 0


def test_snapshot_build_failure_becomes_structured_finding() -> None:
    result = KiCadProjectValidationPipeline().validate(
        files=KiCadLocalFileSet({}), targets=(), symbol_table=symbol_table(),
    )

    assert not result.valid
    assert result.snapshot is None
    assert result.findings[0].code == "ERR-KICAD-0047"
