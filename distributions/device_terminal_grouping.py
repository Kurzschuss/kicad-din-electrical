"""Group terminals by source device and terminal function."""


def group_terminals_by_device(terminals: list[dict]) -> dict[str, list[dict]]:
    groups: dict[str, list[dict]] = {}
    for terminal in terminals:
        device_id = str(terminal.get("device_id") or terminal.get("source_device_id") or "UNASSIGNED")
        groups.setdefault(device_id, []).append(dict(terminal))
    return groups


def assign_terminal_functions(terminals: list[dict], device_id: str, functions: list[str]) -> list[dict]:
    result = [dict(t) for t in terminals]
    matching = [i for i, t in enumerate(result) if str(t.get("device_id") or t.get("source_device_id")) == str(device_id)]
    for index, function in zip(matching, functions):
        result[index]["terminal_function"] = str(function)
    return result
