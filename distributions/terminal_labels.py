"""Customizable terminal naming and numbering."""

DEFAULT_SCHEMA = {
    "rail_prefix": "X",
    "separator": ".",
    "number_width": 2,
}


def terminal_label(rail: str, number: int, schema: dict | None = None, custom: str | None = None) -> str:
    """Return a user-defined label, or generate one from the naming schema."""
    if custom is not None and str(custom).strip():
        return str(custom).strip()
    cfg = {**DEFAULT_SCHEMA, **(schema or {})}
    width = int(cfg["number_width"])
    separator = str(cfg["separator"])
    return f"{cfg['rail_prefix']}{rail.lstrip('X')}{separator}{number:0{width}d}"


def apply_terminal_labels(terminals: list[dict], schema: dict | None = None) -> list[dict]:
    result = []
    for index, terminal in enumerate(terminals, 1):
        rail = terminal.get("terminal_rail", "X1")
        number = terminal.get("terminal_number", index)
        custom = terminal.get("custom_terminal_label")
        result.append({
            **terminal,
            "terminal_label": terminal_label(rail, int(number), schema, custom),
            "terminal_label_custom": bool(custom and str(custom).strip()),
        })
    return result
