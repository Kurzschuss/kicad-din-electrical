"""Tests for rejecting future synchronization log timestamps."""
import json
from datetime import datetime, timedelta, timezone

import pytest

from .din_editor_sync_log import DinSyncLog


def test_load_rejects_future_timestamp(tmp_path):
    path = tmp_path / "sync-log.json"
    future = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
    path.write_text(json.dumps([{
        "timestamp": future,
        "reference": "X5",
        "source": "KiCad",
        "value": "24V",
        "action": "imported",
    }]), encoding="utf-8")

    with pytest.raises(ValueError, match="cannot be in the future"):
        DinSyncLog().load(path)
