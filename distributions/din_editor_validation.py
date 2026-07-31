"""Pre-save and pre-export validation for DIN editor projects."""
from dataclasses import dataclass
from .din_kicad_sync import terminal_sync_report
from .din_editor_session import DinEditorSession


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    message: str
    reference: str | None = None


def validate_session(session: DinEditorSession) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    seen: set[str] = set()
    for component in session.components:
        reference = str(component.get("reference", "")).strip()
        if not reference:
            issues.append(ValidationIssue("MISSING_REFERENCE", "Component has no reference"))
            continue
        if reference in seen:
            issues.append(ValidationIssue("DUPLICATE_REFERENCE", f"Duplicate reference: {reference}", reference))
        seen.add(reference)
        if component.get("component_type") == "DIN_RAIL_TERMINAL_BLOCK":
            label = str(component.get("label") or component.get("terminal_label") or "").strip()
            if component.get("can_edit_label", True) and not label:
                issues.append(ValidationIssue("MISSING_TERMINAL_LABEL", f"Terminal label missing: {reference}", reference))
    report = terminal_sync_report(session.components)
    for conflict in report.get("conflicts", []):
        issues.append(ValidationIssue("SYNC_CONFLICT", f"KiCad/DIN label conflict: {conflict['reference']}", str(conflict["reference"])))
    return issues


def assert_valid(session: DinEditorSession) -> None:
    issues = validate_session(session)
    if issues:
        raise ValueError("DIN project validation failed: " + "; ".join(issue.message for issue in issues))
