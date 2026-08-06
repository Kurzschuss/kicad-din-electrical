"""Minimales ausführbares Runtime-Gerüst für ProjectOS."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from platform import python_version


@dataclass(frozen=True, slots=True)
class RuntimeInfo:
    """Unveränderliche Diagnoseinformationen der ProjectOS-Runtime."""

    name: str
    version: str
    language: str
    offline_first: bool
    simulation_first: bool
    python_version: str
    started_at_utc: datetime


def create_runtime_info(*, version: str = "0.1.0") -> RuntimeInfo:
    """Erzeugt einen validierten Runtime-Snapshot.

    Args:
        version: Semantische ProjectOS-Version.

    Raises:
        ValueError: Wenn keine Version angegeben wurde.
    """

    normalized_version = version.strip()
    if not normalized_version:
        raise ValueError("Die ProjectOS-Version darf nicht leer sein.")

    return RuntimeInfo(
        name="ProjectOS",
        version=normalized_version,
        language="de-DE",
        offline_first=True,
        simulation_first=True,
        python_version=python_version(),
        started_at_utc=datetime.now(timezone.utc),
    )
