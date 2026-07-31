"""Build a terminal schedule from validated DIN wiring connections."""


def build_terminal_schedule(terminals: list[dict], connections: list[dict]) -> list[dict]:
    labels = {str(t.get("reference")): t.get("label") or t.get("terminal_label") for t in terminals}
    schedule = []
    for index, item in enumerate(connections, 1):
        target_ref = str(item.get("target_ref", ""))
        schedule.append({
            "row": index,
            "terminal_reference": target_ref,
            "terminal_label": labels.get(target_ref, target_ref),
            "terminal_pin": str(item.get("target_pin", "")),
            "source_reference": str(item.get("source_ref", "")),
            "source_pin": str(item.get("source_pin", "")),
            "source_pin_name": item.get("source_pin_name"),
            "net": str(item.get("net", "")),
        })
    return schedule


def validate_terminal_schedule(schedule: list[dict]) -> list[str]:
    errors = []
    for row in schedule:
        missing = [key for key in ("terminal_reference", "terminal_pin", "source_reference", "source_pin", "net") if not row.get(key)]
        if missing:
            errors.append(f"row {row.get('row', '?')}: missing {', '.join(missing)}")
    return errors
