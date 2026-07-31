"""Tests for synchronization log validation in project bundles."""
from datetime import datetime, timedelta, timezone

import pytest

from .din_editor_project_bundle import DinProjectBundleError, import_project_bundle


def _bundle(entry):
    return {"version": 2, "session": {"components": []}, "sync_log": [entry]}


def _entry(timestamp):
    return {"timestamp": timestamp, "reference": "X5", "source": "KiCad", "value": "24V", "action": "imported"}


def test_bundle_normalizes_sync_log_timestamp():
    _, log = import_project_bundle(_bundle(_entry("2026-07-31T14:00:00+02:00")))
    assert log.entries[0]["timestamp"] == "2026-07-31T12:00:00+00:00"


def test_bundle_accepts_z_timestamp():
    _, log = import_project_bundle(_bundle(_entry("2026-07-31T12:00:00Z")))
    assert log.entries[0]["timestamp"] == "2026-07-31T12:00:00+00:00"


def test_bundle_rejects_future_sync_log_timestamp():
    future = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
    with pytest.raises(DinProjectBundleError, match="invalid DIN editor project data"):
        import_project_bundle(_bundle(_entry(future)))
