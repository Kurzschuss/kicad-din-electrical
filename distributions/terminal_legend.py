"""Generate a human-readable terminal legend using editable labels."""
from .terminal_labels import apply_terminal_labels


def build_terminal_legend(terminals: list[dict], schema: dict | None = None) -> list[dict]:
    labeled = apply_terminal_labels(terminals, schema)
    legend = []
    for item in labeled:
        legend.append({
            "terminal": item["terminal_label"],
            "rail": item.get("terminal_rail"),
            "function": item.get("terminal_function"),
            "circuit": item.get("number", item.get("circuit_number")),
            "phase": item.get("phase"),
            "fi_group": item.get("fi_group"),
            "n_group": item.get("n_group"),
            "row": item.get("row"),
            "te": item.get("start_te", item.get("start")),
        })
    return legend
