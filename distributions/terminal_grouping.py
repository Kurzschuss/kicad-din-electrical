"""Group and renumber DIN rail terminal blocks while preserving electrical identity."""


def group_terminals(components: list[dict], rail: int | None = None) -> list[list[dict]]:
    terminals = [c for c in components if c.get("component_type") == "DIN_RAIL_TERMINAL_BLOCK"]
    if rail is not None:
        terminals = [c for c in terminals if int(c.get("rail", 1)) == int(rail)]
    groups: dict[tuple, list[dict]] = {}
    for terminal in terminals:
        key = (terminal.get("terminal_function"), terminal.get("manufacturer"), terminal.get("part_number"))
        groups.setdefault(key, []).append(dict(terminal))
    return list(groups.values())


def renumber_terminal_labels(terminals: list[dict], prefix: str = "X", start: int = 1) -> list[dict]:
    result = []
    for offset, terminal in enumerate(terminals):
        item = dict(terminal)
        item["reference"] = f"{prefix}{int(start) + offset}"
        # Keep the user-facing label untouched.
        item["label"] = item.get("label") or item.get("terminal_label") or item["reference"]
        item["terminal_label"] = item["label"]
        result.append(item)
    return result
