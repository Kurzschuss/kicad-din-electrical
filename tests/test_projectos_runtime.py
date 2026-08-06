from datetime import timezone

import pytest

from projectos import RuntimeInfo, create_runtime_info


def test_runtime_info_uses_projectos_architecture_defaults() -> None:
    runtime = create_runtime_info(version="0.1.0")

    assert isinstance(runtime, RuntimeInfo)
    assert runtime.name == "ProjectOS"
    assert runtime.version == "0.1.0"
    assert runtime.language == "de-DE"
    assert runtime.offline_first is True
    assert runtime.simulation_first is True
    assert runtime.started_at_utc.tzinfo == timezone.utc
    assert runtime.python_version


def test_runtime_info_normalizes_version() -> None:
    assert create_runtime_info(version=" 0.2.0 ").version == "0.2.0"


def test_runtime_info_rejects_empty_version() -> None:
    with pytest.raises(ValueError, match="Version"):
        create_runtime_info(version="   ")


def test_runtime_info_is_immutable() -> None:
    runtime = create_runtime_info()

    with pytest.raises(AttributeError):
        runtime.version = "9.9.9"  # type: ignore[misc]
