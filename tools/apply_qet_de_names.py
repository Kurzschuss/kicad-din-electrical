#!/usr/bin/env python3
"""Apply reviewed German visible-name overrides to a generated QET KiCad library.

This intentionally runs after the geometry converter. Source-derived names remain
untouched when QET already provides a German name. Only paths present in the
reviewed override files are changed, and every change is recorded in the
QET_Adjustments property.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Sequence

PROPERTY_RE = re.compile(r'^(\s*)\(property "([^"]+)" "((?:\\.|[^"])*)"(.*)$')


def unescape(value: str) -> str:
    return value.replace('\\n', '\n').replace('\\"', '"').replace('\\\\', '\\')


def escape(value: str) -> str:
    return value.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')


def load_overrides(config_dir: Path) -> dict[str, str]:
    overrides: dict[str, str] = {}
    for config_file in sorted(config_dir.rglob("*.json")):
        payload = json.loads(config_file.read_text(encoding="utf-8"))
        if payload.get("schema_version") != 1:
            raise ValueError(f"Unsupported schema in {config_file}")
        entries = payload.get("overrides")
        if not isinstance(entries, dict):
            raise ValueError(f"Missing overrides object in {config_file}")
        for source_path, german_name in entries.items():
            if not isinstance(source_path, str) or not isinstance(german_name, str):
                raise ValueError(f"Invalid override in {config_file}: {source_path!r}")
            german_name = " ".join(german_name.split())
            if not german_name:
                raise ValueError(f"Empty German name for {source_path} in {config_file}")
            if source_path in overrides:
                raise ValueError(f"Duplicate German override for {source_path}")
            overrides[source_path] = german_name
    return overrides


def property_value(block: list[str], property_name: str) -> str | None:
    for line in block:
        match = PROPERTY_RE.match(line)
        if match and match.group(2) == property_name:
            return unescape(match.group(3))
    return None


def replace_property(block: list[str], property_name: str, new_value: str) -> bool:
    for index, line in enumerate(block):
        match = PROPERTY_RE.match(line)
        if not match or match.group(2) != property_name:
            continue
        block[index] = (
            f'{match.group(1)}(property "{property_name}" '
            f'"{escape(new_value)}"{match.group(4)}'
        )
        return True
    return False


def add_adjustment(current: str | None, adjustment: str) -> str:
    parts = [] if not current or current == "none" else [p.strip() for p in current.split(";") if p.strip()]
    if adjustment not in parts:
        parts.append(adjustment)
    return "; ".join(sorted(parts))


def finalize_library(library_text: str, overrides: dict[str, str]) -> tuple[str, dict]:
    lines = library_text.splitlines()
    result: list[str] = []
    applied: list[str] = []
    unresolved_config_paths = set(overrides)

    def process(block: list[str]) -> list[str]:
        source_path = property_value(block, "QET_Source_Path")
        if not source_path or source_path not in overrides:
            return block

        german_name = overrides[source_path]
        old_value = property_value(block, "Value") or ""
        category = property_value(block, "QET_Category") or ""
        adjustments = property_value(block, "QET_Adjustments")
        keywords = property_value(block, "ki_keywords") or ""

        if not replace_property(block, "Value", german_name):
            raise ValueError(f"Missing Value property for {source_path}")
        if not replace_property(block, "Description", f"{german_name} | QET-Kategorie: {category}"):
            raise ValueError(f"Missing Description property for {source_path}")
        if not replace_property(block, "QET_Adjustments", add_adjustment(adjustments, "german_name_override")):
            raise ValueError(f"Missing QET_Adjustments property for {source_path}")

        keyword_parts = [german_name]
        if old_value and old_value.casefold() != german_name.casefold():
            keyword_parts.append(old_value)
        if keywords:
            keyword_parts.append(keywords)
        replace_property(block, "ki_keywords", " ".join(keyword_parts))

        applied.append(source_path)
        unresolved_config_paths.discard(source_path)
        return block

    block: list[str] | None = None
    for line in lines:
        if line.startswith('  (symbol "Z_Q_'):
            if block is not None:
                result.extend(process(block))
            block = [line]
        elif block is not None:
            block.append(line)
        else:
            result.append(line)
    if block is not None:
        result.extend(process(block))

    report = {
        "configured_overrides": len(overrides),
        "applied_overrides": len(applied),
        "applied_paths": sorted(applied),
        "unmatched_override_paths": sorted(unresolved_config_paths),
    }
    return "\n".join(result) + ("\n" if library_text.endswith("\n") else ""), report


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Apply reviewed German QET names to a generated KiCad library.")
    parser.add_argument("--library", type=Path, required=True)
    parser.add_argument("--config-dir", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args(argv)

    overrides = load_overrides(args.config_dir)
    finalized, report = finalize_library(args.library.read_text(encoding="utf-8"), overrides)
    args.library.write_text(finalized, encoding="utf-8", newline="\n")
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "applied_paths"}, ensure_ascii=False, indent=2))

    if args.strict and (report["applied_overrides"] != report["configured_overrides"] or report["unmatched_override_paths"]):
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
