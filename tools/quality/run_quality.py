"""Command-line entry point for the data-driven Z_ quality checks."""

from __future__ import annotations

import argparse
from collections import Counter
import json
import os
from pathlib import Path
from typing import Iterable

from tools.quality.kicad_symbol_adapter import extract_symbol_facts
from tools.quality.rule_engine import Finding, evaluate, load_rules, should_fail

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RULES = (
    ROOT / "rules/z/symbols/naming.json",
    ROOT / "rules/z/symbols/geometry.json",
)


def _load_profile(name: str) -> dict:
    path = ROOT / "rules/profiles" / f"{name}.json"
    if not path.is_file():
        available = ", ".join(sorted(item.stem for item in path.parent.glob("*.json")))
        raise ValueError(f"Unknown profile {name!r}. Available profiles: {available}")
    return json.loads(path.read_text(encoding="utf-8"))


def evaluate_symbols(paths: Iterable[Path]) -> list[Finding]:
    rules = load_rules(DEFAULT_RULES)
    findings: list[Finding] = []
    for path in paths:
        if not path.is_file():
            raise ValueError(f"Symbol file not found: {path}")
        findings.extend(evaluate(rules, extract_symbol_facts(path)))
    return findings


def render_console(findings: Iterable[Finding], profile_name: str) -> str:
    rows = list(findings)
    lines = [f"Z_ quality report (profile: {profile_name})", ""]
    for finding in rows:
        lines.extend(
            [
                f"[{finding.status}] {finding.rule_id} – {finding.title}",
                f"  Element: {finding.element}",
                f"  Expected: {finding.expected!r}",
                f"  Actual: {finding.actual!r}",
                f"  Explanation: {finding.explanation}",
                f"  Recommendation: {finding.recommendation}",
            ]
        )
        if finding.exception_id:
            lines.append(f"  Exception: {finding.exception_id}")
        lines.append("")
    counts = Counter(finding.status for finding in rows)
    lines.append(
        "Summary: "
        + ", ".join(f"{status}={counts.get(status, 0)}" for status in sorted(counts))
    )
    return "\n".join(lines) + "\n"


def render_markdown(findings: Iterable[Finding], profile_name: str) -> str:
    rows = list(findings)
    counts = Counter(finding.status for finding in rows)
    lines = [
        "## Z_ quality report",
        "",
        f"Profile: `{profile_name}`",
        "",
        "| Rule | Element | Status | Expected | Actual |",
        "|---|---|---|---|---|",
    ]
    for finding in rows:
        lines.append(
            f"| `{finding.rule_id}` | `{finding.element}` | `{finding.status}` | "
            f"`{finding.expected}` | `{finding.actual}` |"
        )
    lines.extend(["", "### Summary", ""])
    for status in sorted(counts):
        lines.append(f"- `{status}`: {counts[status]}")
    return "\n".join(lines) + "\n"


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run data-driven Z_ quality checks.")
    parser.add_argument("symbols", nargs="+", type=Path, help="KiCad .kicad_sym files")
    parser.add_argument("--profile", default="development", help="Profile name")
    parser.add_argument("--json-output", type=Path, help="Write machine-readable findings")
    parser.add_argument(
        "--summary-output",
        type=Path,
        help="Write GitHub-flavoured Markdown summary; defaults to GITHUB_STEP_SUMMARY",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        profile = _load_profile(args.profile)
        findings = evaluate_symbols(args.symbols)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        raise SystemExit(f"quality check configuration error: {exc}") from exc

    print(render_console(findings, args.profile), end="")

    if args.json_output:
        _write(
            args.json_output,
            json.dumps(
                [finding.to_dict() for finding in findings],
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            )
            + "\n",
        )

    summary_value = args.summary_output or os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_value:
        summary_path = Path(summary_value)
        _write(summary_path, render_markdown(findings, args.profile))

    return 1 if should_fail(findings, profile) else 0


if __name__ == "__main__":
    raise SystemExit(main())
