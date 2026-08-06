from uuid import UUID

import pytest

from projectos.identifiers import BusinessId, ObjectId
from projectos.kicad_assets import (
    KiCadAssetReference, KiCadAssetStatus, KiCadAssetTargetType,
    KiCadAssetType, KiCadLibraryReference,
)
from projectos.kicad_connections import (
    DeviceTerminal, KiCadPinElectricalType, KiCadStandardConformance,
    KiCadSymbolPin, TerminalFunction, TerminalPinAssignment,
    ensure_unique_terminal_pin_assignment, validate_required_terminal_assignments,
)


def oid(value: int) -> ObjectId:
    return ObjectId(UUID(int=value))


def terminal(number: int = 1, required: bool = True) -> DeviceTerminal:
    return DeviceTerminal(
        object_id=oid(number), terminal_id=BusinessId(f"TERM-{number:04d}"),
        target_type=KiCadAssetTargetType.CATALOG_DEVICE,
        target_id=BusinessId("CAT-MCB-B16"), designation=str(number),
        function=TerminalFunction.POWER, required=required,
    )


def symbol(active: bool = True, target_id: str = "CAT-MCB-B16") -> KiCadAssetReference:
    return KiCadAssetReference(
        object_id=oid(100), asset_id=BusinessId("KICAD-SYM-0001"),
        asset_type=KiCadAssetType.SYMBOL,
        target_type=KiCadAssetTargetType.CATALOG_DEVICE,
        target_id=BusinessId(target_id),
        reference=KiCadLibraryReference("DIN_Protection", "MCB_1P"),
        status=KiCadAssetStatus.ACTIVE if active else KiCadAssetStatus.DRAFT,
    )


def assignment(term: DeviceTerminal, pin: str, number: int) -> TerminalPinAssignment:
    return TerminalPinAssignment.create(
        object_id=oid(200 + number), assignment_id=BusinessId(f"MAP-{number:04d}"),
        terminal=term, symbol_asset=symbol(),
        pin=KiCadSymbolPin(pin, term.designation, KiCadPinElectricalType.PASSIVE),
    )


def test_standardkonforme_zuordnung_ist_der_regelfall():
    result = assignment(terminal(), "1", 1)
    assert result.conformance is KiCadStandardConformance.STANDARD
    assert result.exception_reason is None


def test_abweichung_benoetigt_begruendung():
    with pytest.raises(ValueError, match="ERR-KICAD-0016"):
        TerminalPinAssignment.create(
            object_id=oid(201), assignment_id=BusinessId("MAP-0001"),
            terminal=terminal(), symbol_asset=symbol(), pin=KiCadSymbolPin("1", "1"),
            conformance=KiCadStandardConformance.EXCEPTION,
        )


def test_standardeintrag_darf_keinen_ausnahmegrund_enthalten():
    with pytest.raises(ValueError, match="ERR-KICAD-0017"):
        TerminalPinAssignment.create(
            object_id=oid(202), assignment_id=BusinessId("MAP-0002"),
            terminal=terminal(), symbol_asset=symbol(), pin=KiCadSymbolPin("1", "1"),
            exception_reason="Sonderfall",
        )


def test_begruendete_ausnahme_wird_akzeptiert():
    result = TerminalPinAssignment.create(
        object_id=oid(203), assignment_id=BusinessId("MAP-0003"),
        terminal=terminal(), symbol_asset=symbol(), pin=KiCadSymbolPin("A", "Sonderpin"),
        conformance=KiCadStandardConformance.EXCEPTION,
        exception_reason="Herstellerbibliothek verwendet abweichende Pinnummer.",
    )
    assert result.exception_reason.startswith("Herstellerbibliothek")


def test_nur_aktive_symbole_desselben_ziels_sind_zulaessig():
    with pytest.raises(ValueError, match="ERR-KICAD-0012"):
        TerminalPinAssignment.create(
            object_id=oid(204), assignment_id=BusinessId("MAP-0004"),
            terminal=terminal(), symbol_asset=symbol(active=False), pin=KiCadSymbolPin("1", "1"),
        )
    with pytest.raises(ValueError, match="ERR-KICAD-0013"):
        TerminalPinAssignment.create(
            object_id=oid(205), assignment_id=BusinessId("MAP-0005"),
            terminal=terminal(), symbol_asset=symbol(target_id="CAT-RCCB-40A"),
            pin=KiCadSymbolPin("1", "1"),
        )


def test_anschluss_und_pin_sind_je_symbol_eindeutig():
    first = assignment(terminal(1), "1", 1)
    with pytest.raises(ValueError, match="ERR-KICAD-0014"):
        ensure_unique_terminal_pin_assignment((first,), assignment(terminal(1), "2", 2))
    with pytest.raises(ValueError, match="ERR-KICAD-0015"):
        ensure_unique_terminal_pin_assignment((first,), assignment(terminal(2), "1", 3))


def test_erforderliche_nicht_zugeordnete_anschluesse_werden_gemeldet():
    terminals = (terminal(1), terminal(2), terminal(3, required=False))
    mappings = (assignment(terminals[0], "1", 1),)
    assert validate_required_terminal_assignments(terminals, mappings, symbol()) == (
        terminals[1].terminal_id,
    )


def test_kicad_pin_typen_enthalten_tri_state_und_free():
    assert KiCadPinElectricalType.TRI_STATE.value == "TRI_STATE"
    assert KiCadPinElectricalType.FREE.value == "FREE"
