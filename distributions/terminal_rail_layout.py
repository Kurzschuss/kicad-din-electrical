"""Physical planning of terminal strips, separate from protective devices."""

MAX_TERMINAL_RAILS = 18
TERMINALS_PER_RAIL = 12


def allocate_terminal_rails(terminals: list[dict], terminals_per_rail: int = TERMINALS_PER_RAIL) -> list[dict]:
    if not 1 <= terminals_per_rail <= TERMINALS_PER_RAIL:
        raise ValueError(f"terminals_per_rail must be 1..{TERMINALS_PER_RAIL}")
    result = []
    for index, terminal in enumerate(terminals):
        rail_index = index // terminals_per_rail + 1
        if rail_index > MAX_TERMINAL_RAILS:
            raise ValueError("terminal layout exceeds configured rail count")
        slot = index % terminals_per_rail + 1
        result.append({
            **terminal,
            "terminal_rail": terminal.get("terminal_rail", f"X{rail_index}"),
            "terminal_rail_number": rail_index,
            "terminal_slot": slot,
        })
    return result
