"""Conflict model for DIN/KiCad synchronization."""


def build_conflict_list(local_components: list[dict], kicad_fields: list[dict]) -> list[dict]:
    local = {str(c.get("reference")): str(c.get("label") or c.get("terminal_label") or "").strip() for c in local_components if c.get("component_type") == "DIN_RAIL_TERMINAL_BLOCK"}
    conflicts = []
    for field in kicad_fields:
        if not isinstance(field, dict):
            continue
        ref = str(field.get("reference", "")).strip()
        incoming = str(field.get("label", "")).strip()
        if ref in local and incoming and local[ref] and incoming != local[ref]:
            conflicts.append({"reference": ref, "local_label": local[ref], "kicad_label": incoming})
    return conflicts


def resolve_conflicts(local_components: list[dict], conflicts: list[dict], choice: str = "kicad") -> list[dict]:
    if choice not in {"kicad", "local"}:
        raise ValueError("choice must be 'kicad' or 'local'")
    result = [dict(c) for c in local_components]
    if choice == "local":
        return result

    incoming: dict[str, str] = {}
    for conflict in conflicts:
        if not isinstance(conflict, dict):
            raise ValueError("conflict must be an object")
        reference = str(conflict.get("reference", "")).strip()
        label = str(conflict.get("kicad_label", "")).strip()
        if not reference or not label:
            raise ValueError("conflict requires reference and kicad_label")
        if reference in incoming and incoming[reference] != label:
            raise ValueError(f"ambiguous KiCad conflict for reference {reference}")
        incoming[reference] = label

    for item in result:
        ref = str(item.get("reference", ""))
        if ref in incoming and item.get("component_type") == "DIN_RAIL_TERMINAL_BLOCK":
            item["label"] = incoming[ref]
            item["terminal_label"] = incoming[ref]
    return result
