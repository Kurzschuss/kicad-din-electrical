"""Audit trail for DIN/KiCad synchronization decisions."""
from datetime import datetime, timezone


class DinSyncLog:
    def __init__(self):
        self.entries: list[dict] = []

    def record(self, reference: str, source: str, value: str, action: str) -> dict:
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "reference": str(reference),
            "source": str(source),
            "value": str(value),
            "action": str(action),
        }
        self.entries.append(entry)
        return dict(entry)

    def clear(self) -> None:
        self.entries.clear()

    def export(self) -> list[dict]:
        return [dict(entry) for entry in self.entries]
