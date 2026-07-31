"""Audit trail for DIN/KiCad synchronization decisions."""
from datetime import datetime, timezone
import json
from pathlib import Path


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

    def save(self, path: str | Path) -> Path:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(self.export(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return target

    def load(self, path: str | Path) -> None:
        source = Path(path)
        data = json.loads(source.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            raise ValueError("invalid DIN synchronization log")
        self.entries = [dict(entry) for entry in data]
