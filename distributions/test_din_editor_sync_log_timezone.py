"""Tests for synchronization log timestamp normalization."""
import json

from .din_editor_sync_log import DinSyncLog


def test_load_normalizes_offset_timestamp_to_utc(tmp_path):
    path = tmp_path / "sync-log.json"
    path.write_text(json.dumps([{
        "timestamp": "2026-07-31T14:00:00+02:00",
        "reference": "X5",
        "source": "KiCad",
        "value": "24V",
        "action": "imported",
    }]), encoding="utf-8")

    log = DinSyncLog()
    log.load(path)

    assert log.entries[0]["timestamp"] == "2026-07-31T12:00:00+00:00"


def test_load_normalizes_z_timestamp_to_explicit_utc(tmp_path):
    path = tmp_path / "sync-log.json"
    path.write_text(json.dumps([{
        "timestamp": "2026-07-31T12:00:00Z",
        "reference": "X5",
        "source": "KiCad",
        "value": "24V",
        "action": "imported",
    }]), encoding="utf-8")

    log = DinSyncLog()
    log.load(path)

    assert log.entries[0]["timestamp"] == "2026-07-31T12:00:00+00:00"
