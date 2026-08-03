"""Command-line entry point for the data-driven Z_ quality checks."""

from __future__ import annotations

import argparse
from collections import Counter
from html import escape
import json
import os
from pathlib import Path
from typing import Iterable

from tools.quality.kicad_footprint_adapter import extract_footprint_facts
from tools.quality.kicad_symbol_adapter import extract_symbol_facts
from tools.quality.rule_engine import Finding, evaluate, load_rules, should_fail

ROOT = Path(__file__).resolve().parents[2]
SYMBOL_RULES = (
    ROOT / "rules/z/symbols/naming.json",
    ROOT / "rules/z/symbols/geometry.json",
)
FOOTPRINT_RULES = (
    ROOT / "rules/z/footprints/core.json",
    ROOT / "rules/z/footprints/presentation.json",
)


def _load_profile(name: str) -> dict:
    path = ROOT / "rules/profiles" / f"{name}.json"
    if not path.is_file():
        available = ", ".join(sorted(item.stem for item in path.parent.glob("*.json")))
        raise ValueError(f"Unknown profile {name!r}. Available profiles: {available}")
    return json.loads(path.read_text(encoding="utf-8"))


def evaluate_symbols(paths: Iterable[Path]) -> list[Finding]:
    rules = load_rules(SYMBOL_RULES)
    findings: list[Finding] = []
    for path in paths:
        if not path.is_file():
            raise ValueError(f"Symbol file not found: {path}")
        findings.extend(evaluate(rules, extract_symbol_facts(path)))
    return findings


def evaluate_footprints(paths: Iterable[Path]) -> list[Finding]:
    rules = load_rules(FOOTPRINT_RULES)
    findings: list[Finding] = []
    for path in paths:
        if not path.is_file():
            raise ValueError(f"Footprint file not found: {path}")
        findings.extend(evaluate(rules, extract_footprint_facts(path)))
    return findings


def filter_findings(
    findings: Iterable[Finding],
    statuses: Iterable[str] = (),
    categories: Iterable[str] = (),
    scopes: Iterable[str] = (),
) -> list[Finding]:
    status_set, category_set, scope_set = set(statuses), set(categories), set(scopes)
    return [
        finding for finding in findings
        if (not status_set or finding.status in status_set)
        and (not category_set or finding.category in category_set)
        and (not scope_set or finding.scope in scope_set)
    ]


def render_console(findings: Iterable[Finding], profile_name: str) -> str:
    rows = list(findings)
    lines = [f"Z_ quality report (profile: {profile_name})", ""]
    for finding in rows:
        lines.extend([
            f"[{finding.status}] {finding.rule_id} – {finding.title}",
            f"  Element: {finding.element}",
            f"  Scope/category: {finding.scope}/{finding.category}",
            f"  Expected: {finding.expected!r}",
            f"  Actual: {finding.actual!r}",
            f"  Explanation: {finding.explanation}",
            f"  Recommendation: {finding.recommendation}",
        ])
        if finding.exception_id:
            lines.append(f"  Exception: {finding.exception_id}")
        lines.append("")
    counts = Counter(finding.status for finding in rows)
    lines.append("Summary: " + ", ".join(
        f"{status}={counts.get(status, 0)}" for status in sorted(counts)
    ))
    return "\n".join(lines) + "\n"


def render_markdown(findings: Iterable[Finding], profile_name: str) -> str:
    rows = list(findings)
    counts = Counter(finding.status for finding in rows)
    lines = [
        "## Z_ quality report", "", f"Profile: `{profile_name}`", "",
        "| Rule | Element | Scope | Category | Status | Expected | Actual |",
        "|---|---|---|---|---|---|---|",
    ]
    for finding in rows:
        lines.append(
            f"| `{finding.rule_id}` | `{finding.element}` | `{finding.scope}` | "
            f"`{finding.category}` | `{finding.status}` | `{finding.expected}` | "
            f"`{finding.actual}` |"
        )
    lines.extend(["", "### Summary", ""])
    for status in sorted(counts):
        lines.append(f"- `{status}`: {counts[status]}")
    return "\n".join(lines) + "\n"


def render_html(findings: Iterable[Finding], profile_name: str) -> str:
    rows = list(findings)
    counts = Counter(finding.status for finding in rows)
    summary = "".join(
        f'<li><code>{escape(status)}</code>: {count}</li>'
        for status, count in sorted(counts.items())
    )
    body_rows = "".join(
        "<tr>"
        f"<td><code>{escape(finding.rule_id)}</code></td>"
        f"<td><code>{escape(finding.element)}</code></td>"
        f"<td>{escape(finding.scope)}</td>"
        f"<td>{escape(finding.category)}</td>"
        f"<td><code>{escape(finding.status)}</code></td>"
        f"<td>{escape(str(finding.expected))}</td>"
        f"<td>{escape(str(finding.actual))}</td>"
        f"<td>{escape(finding.explanation)}</td>"
        f"<td>{escape(finding.recommendation)}</td>"
        "</tr>"
        for finding in rows
    )
    return f"""<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Z_ quality report</title>
<style>
body {{ font-family: system-ui, sans-serif; margin: 2rem; line-height: 1.4; }}
table {{ border-collapse: collapse; width: 100%; }}
th, td {{ border: 1px solid #bbb; padding: .45rem; text-align: left; vertical-align: top; }}
th {{ background: #eee; }}
code {{ white-space: nowrap; }}
</style>
</head>
<body>
<h1>Z_ quality report</h1>
<p>Profile: <code>{escape(profile_name)}</code></p>
<h2>Summary</h2><ul>{summary}</ul>
<table>
<thead><tr><th>Rule</th><th>Element</th><th>Scope</th><th>Category</th><th>Status</th><th>Expected</th><th>Actual</th><th>Explanation</th><th>Recommendation</th></tr></thead>
<tbody>{body_rows}</tbody>
</table>
</body>
</html>
"""


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run data-driven Z_ quality checks.")
    parser.add_argument("symbols", nargs="*", type=Path, help="KiCad .kicad_sym files")
    parser.add_argument("--footprint", action="append", default=[], type=Path,
                        help="KiCad .kicad_mod file; may be repeated")
    parser.add_argument("--profile", default="development", help="Profile name")
    parser.add_argument("--json-output", type=Path, help="Write machine-readable findings")
    parser.add_argument("--html-output", type=Path, help="Write standalone HTML report")
    parser.add_argument("--summary-output", type=Path,
                        help="Write GitHub-flavoured Markdown summary; defaults to GITHUB_STEP_SUMMARY")
    parser.add_argument("--status", action="append", default=[], help="Filter report by status")
    parser.add_argument("--category", action="append", default=[], help="Filter report by rule category")
    parser.add_argument("--scope", action="append", default=[], help="Filter report by element scope")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if not args.symbols and not args.footprint:
        raise SystemExit("quality check configuration error: provide a symbol or --footprint")
    try:
        profile = _load_profile(args.profile)
        all_findings = evaluate_symbols(args.symbols) + evaluate_footprints(args.footprint)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        raise SystemExit(f"quality check configuration error: {exc}") from exc

    findings = filter_findings(all_findings, args.status, args.category, args.scope)
    print(render_console(findings, args.profile), end="")
    if args.json_output:
        _write(args.json_output, json.dumps(
            [finding.to_dict() for finding in findings], ensure_ascii=False,
            indent=2, sort_keys=True,
        ) + "\n")
    if args.html_output:
        _write(args.html_output, render_html(findings, args.profile))
    summary_value = args.summary_output or os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_value:
        _write(Path(summary_value), render_markdown(findings, args.profile))
    # Filters affect presentation only. Release gating always evaluates all findings.
    return 1 if should_fail(all_findings, profile) else 0


if __name__ == "__main__":
    raise SystemExit(main())
