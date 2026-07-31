"""Checks for logical FI/MCB group metadata."""
from .device_catalog import DEVICE_WIDTHS

RCD_TYPES = {"RCD_2P", "RCD_4P"}
RCBO_TYPES = {"RCBO_1P_N"}


def validate_groups(groups: list[dict]) -> list[str]:
    warnings = []
    neutral_groups = {}
    for group in groups:
        protective = group.get("protective_device")
        neutral = group.get("neutral_group")
        if protective not in DEVICE_WIDTHS:
            warnings.append(f"Unbekanntes Schutzgerät: {protective}")
        if protective in RCD_TYPES and not neutral:
            warnings.append(f"FI/RCD-Gruppe '{group.get('name', '')}' hat keine N-Gruppe")
        if protective in RCBO_TYPES and not neutral:
            warnings.append(f"FI/LS-Gruppe '{group.get('name', '')}' hat keine N-Zuordnung")
        if neutral:
            neutral_groups.setdefault(neutral, []).append(group.get("name", ""))
    for neutral, names in neutral_groups.items():
        if len(names) > 1:
            warnings.append(f"N-Gruppe '{neutral}' wird mehreren Gruppen zugeordnet: {', '.join(names)}")
    return warnings
