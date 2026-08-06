"""Unveränderliche Kennungswertobjekte für ProjectOS."""

from __future__ import annotations

from dataclasses import dataclass
import re
from uuid import UUID, uuid4

_BUSINESS_ID_PATTERN = re.compile(r"^[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*$")
_CORRELATION_ID_PATTERN = re.compile(r"^COR-[0-9]{8}$")


@dataclass(frozen=True, slots=True)
class ObjectId:
    """Technische, global eindeutige Identität auf UUID-Basis."""

    value: UUID

    @classmethod
    def new(cls) -> "ObjectId":
        return cls(uuid4())

    @classmethod
    def parse(cls, value: str) -> "ObjectId":
        if not isinstance(value, str) or not value.strip():
            raise ValueError("ObjectId muss als nicht leerer Text angegeben werden.")
        parsed = UUID(value)
        if parsed.int == 0:
            raise ValueError("Die Null-UUID ist als ObjectId nicht zulässig.")
        return cls(parsed)

    def __post_init__(self) -> None:
        if not isinstance(self.value, UUID):
            raise TypeError("ObjectId.value muss eine UUID sein.")
        if self.value.int == 0:
            raise ValueError("Die Null-UUID ist als ObjectId nicht zulässig.")

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True, slots=True)
class BusinessId:
    """Stabile, menschenlesbare fachliche Kennung gemäß ADR-0001."""

    value: str

    @classmethod
    def parse(cls, value: str) -> "BusinessId":
        return cls(value)

    def __post_init__(self) -> None:
        if not isinstance(self.value, str):
            raise TypeError("BusinessId.value muss Text sein.")
        normalized = self.value.strip().upper()
        if not normalized:
            raise ValueError("BusinessId darf nicht leer sein.")
        if not _BUSINESS_ID_PATTERN.fullmatch(normalized):
            raise ValueError(
                "BusinessId darf nur Großbuchstaben, Ziffern und Bindestriche enthalten."
            )
        object.__setattr__(self, "value", normalized)

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class CorrelationId:
    """Kennung zur Verknüpfung zusammengehöriger Vorgänge."""

    value: str

    @classmethod
    def from_sequence(cls, sequence: int) -> "CorrelationId":
        if not isinstance(sequence, int) or isinstance(sequence, bool):
            raise TypeError("Die Korrelationssequenz muss eine Ganzzahl sein.")
        if sequence < 1 or sequence > 99_999_999:
            raise ValueError("Die Korrelationssequenz muss zwischen 1 und 99.999.999 liegen.")
        return cls(f"COR-{sequence:08d}")

    @classmethod
    def parse(cls, value: str) -> "CorrelationId":
        return cls(value)

    def __post_init__(self) -> None:
        if not isinstance(self.value, str):
            raise TypeError("CorrelationId.value muss Text sein.")
        normalized = self.value.strip().upper()
        if not _CORRELATION_ID_PATTERN.fullmatch(normalized):
            raise ValueError("CorrelationId muss dem Format COR-00000001 entsprechen.")
        if normalized == "COR-00000000":
            raise ValueError("Die Korrelationssequenz 0 ist nicht zulässig.")
        object.__setattr__(self, "value", normalized)

    def __str__(self) -> str:
        return self.value
