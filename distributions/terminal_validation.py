"""Validate editable terminal labels before KiCad export."""
import re

LABEL_RE = re.compile(r"^[A-Za-zÄÖÜäöüß0-9_.:/+\- ]{1,64}$")


def validate_terminal_labels(terminals: list[dict]) -> list[dict]:
    """Return terminals with validation status; do not alter user labels."""
    result = []
    seen = set()
    for terminal in terminals:
        label = str(terminal.get("terminal_label", terminal.get("terminal", ""))).strip()
        errors = []
        if not label:
            errors.append("Klemmenbezeichnung fehlt")
        elif not LABEL_RE.fullmatch(label):
            errors.append("ungültige Zeichen in Klemmenbezeichnung")
        if label in seen:
            errors.append("Klemmenbezeichnung doppelt vergeben")
        if label:
            seen.add(label)
        result.append({**terminal, "terminal_label": label, "terminal_label_valid": not errors, "terminal_label_errors": errors})
    return result
