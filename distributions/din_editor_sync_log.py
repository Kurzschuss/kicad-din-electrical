"""Audit trail for DIN/KiCad synchronization decisions."""
from datetime import datetime, timezone
import json
from pathlib import Path
from uuid import UUID


def _normalize_optional_uuid(value: str | None, field_name: str) -> str | None:
    if value is None:
        return None
    try:
        return str(UUID(str(value)))
    except (ValueError, AttributeError, TypeError) as exc:
        raise ValueError(f"DIN synchronization log {field_name} must be a UUID") from exc


class DinSyncLog:
    def __init__(self):
        self.entries: list[dict] = []

    def record(
        self,
        reference: str,
        source: str,
        value: str,
        action: str,
        *,
        project_id: str | None = None,
        correlation_id: str | None = None,
        causation_id: str | None = None,
    ) -> dict:
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "reference": str(reference),
            "source": str(source),
            "value": str(value),
            "action": str(action),
        }
        for field_name, field_value in (
            ("project_id", project_id),
            ("correlation_id", correlation_id),
            ("causation_id", causation_id),
        ):
            normalized = _normalize_optional_uuid(field_value, field_name)
            if normalized is not None:
                entry[field_name] = normalized
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
        validated = []
        now = datetime.now(timezone.utc)
        for entry in data:
            if not isinstance(entry, dict):
                raise ValueError("invalid DIN synchronization log entry")
            required = {"timestamp", "reference", "source", "value", "action"}
            if not required.issubset(entry):
                raise ValueError("invalid DIN synchronization log entry")
            timestamp = str(entry["timestamp"])
            parsed = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            if parsed.tzinfo is None:
                raise ValueError("DIN synchronization log timestamp requires timezone")
            parsed = parsed.astimezone(timezone.utc)
            if parsed > now:
                raise ValueError("DIN synchronization log timestamp cannot be in the future")
            normalized = parsed.isoformat()
            if not str(entry["reference"]).strip():
                raise ValueError("DIN synchronization log reference is required")
            if not str(entry["source"]).strip():
                raise ValueError("DIN synchronization log source is required")
            if not str(entry["action"]).strip():
                raise ValueError("DIN synchronization log action is required")
            clean = dict(entry)
            clean["timestamp"] = normalized
            for field_name in ("project_id", "correlation_id", "causation_id"):
                if field_name in clean:
                    clean[field_name] = _normalize_optional_uuid(clean[field_name], field_name)
            validated.append(clean)
        self.entries = validated