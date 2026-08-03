"""Small, safe, data-driven quality rule engine.

Rules are JSON data and may only select explicitly registered check types.
No Python expressions or shell commands are evaluated.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from fnmatch import fnmatch
import json
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping

VALID_STATUSES = {
    "kicad_conform",
    "z_conform",
    "needs_rework",
    "temporarily_accepted",
}
VALID_SEVERITIES = {"info", "warning", "error", "critical"}


@dataclass(frozen=True)
class Rule:
    id: str
    title: str
    scope: str
    category: str
    severity: str
    status: str
    version: str
    description: str
    recommendation: str
    references: tuple[str, ...]
    check: Mapping[str, Any]


@dataclass(frozen=True)
class Finding:
    element: str
    rule_id: str
    title: str
    severity: str
    status: str
    expected: Any
    actual: Any
    explanation: str
    recommendation: str
    exception_id: str | None = None
    scope: str = "unknown"
    category: str = "unknown"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


CheckFunction = Callable[[Rule, Mapping[str, Any]], tuple[bool, Any, Any]]


def _check_prefix(rule: Rule, element: Mapping[str, Any]) -> tuple[bool, Any, Any]:
    field = str(rule.check["field"])
    expected = str(rule.check["prefix"])
    actual = str(element.get(field, ""))
    return actual.startswith(expected), expected, actual


def _check_equals(rule: Rule, element: Mapping[str, Any]) -> tuple[bool, Any, Any]:
    field = str(rule.check["field"])
    expected = rule.check["value"]
    actual = element.get(field)
    return actual == expected, expected, actual


def _check_fields_equal(rule: Rule, element: Mapping[str, Any]) -> tuple[bool, Any, Any]:
    left = str(rule.check["left"])
    right = str(rule.check["right"])
    expected = element.get(left)
    actual = element.get(right)
    return actual == expected, expected, actual


CHECKS: dict[str, CheckFunction] = {
    "field_prefix": _check_prefix,
    "field_equals": _check_equals,
    "fields_equal": _check_fields_equal,
}


def load_rules(paths: Iterable[Path]) -> list[Rule]:
    rules: list[Rule] = []
    seen_ids: set[str] = set()
    for path in sorted(paths, key=lambda item: str(item)):
        data = json.loads(path.read_text(encoding="utf-8"))
        entries = data if isinstance(data, list) else [data]
        for entry in entries:
            rule = _parse_rule(entry, path)
            if rule.id in seen_ids:
                raise ValueError(f"Duplicate rule id {rule.id!r} in {path}")
            seen_ids.add(rule.id)
            rules.append(rule)
    return rules


def _parse_rule(data: Mapping[str, Any], source: Path) -> Rule:
    required = {
        "id", "title", "scope", "category", "severity", "status", "version",
        "description", "recommendation", "references", "check",
    }
    missing = sorted(required - data.keys())
    if missing:
        raise ValueError(f"Missing fields in {source}: {', '.join(missing)}")
    severity = str(data["severity"])
    if severity not in VALID_SEVERITIES:
        raise ValueError(f"Unknown severity {severity!r} in {source}")
    check = data["check"]
    if not isinstance(check, Mapping) or check.get("type") not in CHECKS:
        raise ValueError(f"Unknown or invalid check type in {source}")
    return Rule(
        id=str(data["id"]), title=str(data["title"]), scope=str(data["scope"]),
        category=str(data["category"]), severity=severity, status=str(data["status"]),
        version=str(data["version"]), description=str(data["description"]),
        recommendation=str(data["recommendation"]),
        references=tuple(str(item) for item in data["references"]), check=dict(check),
    )


def evaluate(
    rules: Iterable[Rule],
    element: Mapping[str, Any],
    exceptions: Iterable[Mapping[str, Any]] = (),
) -> list[Finding]:
    findings: list[Finding] = []
    element_name = str(element.get("element", "<unknown>"))
    for rule in rules:
        check = CHECKS[str(rule.check["type"])]
        passed, expected, actual = check(rule, element)
        if passed:
            result_status = "kicad_conform" if rule.id.startswith("KICAD-") else "z_conform"
            explanation = "Regel erfüllt."
            exception_id = None
        else:
            exception = _matching_exception(rule.id, element_name, exceptions)
            if exception:
                result_status = str(exception.get("status", "temporarily_accepted"))
                if result_status not in VALID_STATUSES:
                    raise ValueError(f"Invalid exception status {result_status!r}")
                explanation = str(exception["reason"])
                exception_id = str(exception["id"])
            else:
                result_status = "needs_rework"
                explanation = rule.description
                exception_id = None
        findings.append(Finding(
            element=element_name, rule_id=rule.id, title=rule.title,
            severity=rule.severity, status=result_status, expected=expected,
            actual=actual, explanation=explanation,
            recommendation=rule.recommendation, exception_id=exception_id,
            scope=rule.scope, category=rule.category,
        ))
    return findings


def _matching_exception(
    rule_id: str,
    element_name: str,
    exceptions: Iterable[Mapping[str, Any]],
) -> Mapping[str, Any] | None:
    for exception in exceptions:
        if exception.get("rule_id") == rule_id and fnmatch(
            element_name, str(exception.get("element", ""))
        ):
            return exception
    return None


def findings_to_json(findings: Iterable[Finding]) -> str:
    return json.dumps(
        [finding.to_dict() for finding in findings],
        ensure_ascii=False, indent=2, sort_keys=True,
    )


def should_fail(findings: Iterable[Finding], profile: Mapping[str, Any]) -> bool:
    fail_severities = set(profile.get("fail_severities", []))
    fail_statuses = set(profile.get("fail_statuses", ["needs_rework"]))
    return any(
        finding.severity in fail_severities and finding.status in fail_statuses
        for finding in findings
    )
