"""Tests for synchronization log loading validation."""
import json
import pytest

from .din_editor_sync_log import DinSyncLog


def _write(tmp_path, data):
    path = tmp_path / "sync-log.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def test_load_rejects_naive_timestamp(tmp_path):
    path = _write(tmp_path, [{
        "timestamp": "2026-07-31T12:00:00",
        "reference": "X5",
        "source": "KiCad",
        "value": "24V",
        "action": "imported",
    }])

    with pytest.raises(ValueError, match="requires timezone"):
        DinSyncLog().load(path)


def test_load_accepts_z_timestamp(tmp_path):
    path = _write(tmp_path, [{
        "timestamp": "2026-07-31T12:00:00Z",
        "reference": "X5",
        "source": "KiCad",
        "value": "24V",
        "action": "imported",
    }])

    log = DinSyncLog()
    log.load(path)
    assert log.entries[0]["reference"] == "X5"


def test_load_rejects_missing_entry_fields(tmp_path):
    path = _write(tmp_path, [{"timestamp": "2026-07-31T12:00:00+00:00"}])

    with pytest.raises(ValueError, match="invalid DIN synchronization log entry"):
        DinSyncLog().load(path)


def test_load_is_atomic_on_validation_error(tmp_path):
    log = DinSyncLog()
    log.record("X1", "DIN", "old", "kept")
    path = _write(tmp_path, [{
        "timestamp": "2026-07-31T12:00:00",
        "reference": "X5",
        "source": "KiCad",
        "value": "24V",
        "action": "imported",
    }])

    with pytest.raises(ValueError):
        log.load(path)

    assert len(log.entries) == 1
    assert log.entries[0]["reference"] == "X1"
