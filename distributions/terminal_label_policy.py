"""Per-terminal label policy: auto, manual, or locked."""

POLICIES = {"AUTO", "MANUAL", "LOCKED"}


def set_label_policy(terminal: dict, policy: str) -> dict:
    policy = str(policy).upper()
    if policy not in POLICIES:
        raise ValueError(f"unknown label policy: {policy}")
    item = dict(terminal)
    item["terminal_label_policy"] = policy
    item["can_edit_label"] = policy != "LOCKED"
    return item


def can_change_label(terminal: dict) -> bool:
    return terminal.get("terminal_label_policy", "AUTO") != "LOCKED"
