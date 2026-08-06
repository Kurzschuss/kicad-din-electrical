from dataclasses import FrozenInstanceError, dataclass

import pytest

from projectos import (
    BusinessId,
    CorrelationId,
    MessageSeverity,
    ResultMessage,
    ValidationProfile,
    Validator,
)


@dataclass(frozen=True)
class PositiveRule:
    rule_id: BusinessId = BusinessId("RULE-CORE-0001")

    def validate(self, value: int):
        if value > 0:
            return ()
        return (
            ResultMessage(
                code=BusinessId("ERR-VAL-0001"),
                severity=MessageSeverity.ERROR,
                text="Der Wert muss größer als null sein.",
            ),
        )


@dataclass(frozen=True)
class WarningRule:
    rule_id: BusinessId = BusinessId("RULE-CORE-0002")

    def validate(self, value: int):
        if value < 100:
            return ()
        return (
            ResultMessage(
                code=BusinessId("WARN-VAL-0001"),
                severity=MessageSeverity.WARNING,
                text="Der Wert ist ungewöhnlich groß.",
            ),
        )


@dataclass(frozen=True)
class CriticalRule:
    rule_id: BusinessId = BusinessId("RULE-CORE-0003")

    def validate(self, value: int):
        return (
            ResultMessage(
                code=BusinessId("ERR-VAL-0002"),
                severity=MessageSeverity.CRITICAL,
                text="Kritischer Prüfzustand.",
            ),
        )


def test_validierung_ohne_meldungen_ist_gueltig():
    profile = ValidationProfile(BusinessId("VAL-PROFILE-0001"), (PositiveRule(),))
    result = Validator[int]().validate(5, profile)

    assert result.is_valid
    assert result.messages == ()
    assert result.executed_rule_ids == (BusinessId("RULE-CORE-0001"),)


def test_fehler_macht_ergebnis_ungueltig():
    profile = ValidationProfile(BusinessId("VAL-PROFILE-0001"), (PositiveRule(),))
    result = Validator[int]().validate(0, profile)

    assert not result.is_valid
    assert len(result.errors) == 1


def test_warnung_verhindert_gueltigkeit_nicht():
    profile = ValidationProfile(BusinessId("VAL-PROFILE-0001"), (WarningRule(),))
    result = Validator[int]().validate(100, profile)

    assert result.is_valid
    assert len(result.warnings) == 1


def test_kritische_meldung_stoppt_folgeregeln():
    profile = ValidationProfile(
        BusinessId("VAL-PROFILE-0001"),
        (CriticalRule(), WarningRule()),
    )
    result = Validator[int]().validate(100, profile)

    assert result.executed_rule_ids == (BusinessId("RULE-CORE-0003"),)


def test_kritische_meldung_kann_weiterlaufen_lassen():
    profile = ValidationProfile(
        BusinessId("VAL-PROFILE-0001"),
        (CriticalRule(), WarningRule()),
        stop_on_critical=False,
    )
    result = Validator[int]().validate(100, profile)

    assert result.executed_rule_ids == (
        BusinessId("RULE-CORE-0003"),
        BusinessId("RULE-CORE-0002"),
    )


def test_korrelation_wird_uebernommen():
    correlation = CorrelationId.from_sequence(42)
    profile = ValidationProfile(BusinessId("VAL-PROFILE-0001"), (PositiveRule(),))

    result = Validator[int]().validate(5, profile, correlation_id=correlation)

    assert result.correlation_id == correlation


def test_leeres_profil_wird_abgewiesen():
    with pytest.raises(ValueError):
        ValidationProfile(BusinessId("VAL-PROFILE-0001"), ())


def test_doppelte_regel_wird_abgewiesen():
    rule = PositiveRule()
    with pytest.raises(ValueError):
        ValidationProfile(BusinessId("VAL-PROFILE-0001"), (rule, rule))


def test_ergebnis_ist_unveraenderlich():
    profile = ValidationProfile(BusinessId("VAL-PROFILE-0001"), (PositiveRule(),))
    result = Validator[int]().validate(5, profile)

    with pytest.raises(FrozenInstanceError):
        result.messages = ()
