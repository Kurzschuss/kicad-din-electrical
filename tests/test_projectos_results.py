from dataclasses import FrozenInstanceError

import pytest

from projectos import (
    BusinessId,
    CorrelationId,
    MessageSeverity,
    Result,
    ResultMessage,
)


def message(severity: MessageSeverity = MessageSeverity.ERROR) -> ResultMessage:
    return ResultMessage(
        code=BusinessId("ERR-CORE-0001"),
        severity=severity,
        text="Ein strukturierter Fehler.",
        parameters={"feld": "wert"},
    )


def test_success_result_contains_value() -> None:
    result = Result.success("ok", correlation_id=CorrelationId.from_sequence(12))

    assert result.is_success is True
    assert result.value == "ok"
    assert result.errors == ()
    assert str(result.correlation_id) == "COR-00000012"


def test_failure_requires_error_message() -> None:
    with pytest.raises(ValueError):
        Result.failure(message(MessageSeverity.WARNING))


def test_failure_contains_no_value() -> None:
    result = Result.failure(message())

    assert result.is_success is False
    assert result.value is None
    assert len(result.errors) == 1


def test_success_rejects_error_messages() -> None:
    with pytest.raises(ValueError):
        Result.success("ungueltig", messages=(message(),))


def test_result_message_is_immutable_and_parameters_are_read_only() -> None:
    result_message = message()

    with pytest.raises(FrozenInstanceError):
        result_message.text = "geändert"  # type: ignore[misc]

    with pytest.raises(TypeError):
        result_message.parameters["neu"] = "wert"  # type: ignore[index]


def test_message_text_is_trimmed() -> None:
    result_message = ResultMessage(
        code=BusinessId("ERR-CORE-0002"),
        severity=MessageSeverity.WARNING,
        text="  Warnung  ",
    )

    assert result_message.text == "Warnung"
    assert result_message.is_error is False
