#!/usr/bin/env python3
"""Accept reviewed-by-rule language-neutral manufacturer identifiers as visible names.

This is intentionally conservative. It only accepts a name when a majority of
non-Chinese QET translations agree on the same spelling and every alphabetic
chunk looks like an acronym/model token (uppercase or <=3 characters). Common
English functional words are explicitly blocked so they remain translation work.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Sequence

from apply_qet_de_names import property_value, replace_property

_BLOCKED_FUNCTION_WORDS = {
    "on", "off", "out", "in", "input", "output", "part", "send", "receive", "recv",
    "power", "safety", "module", "modules", "switch", "relay", "sensor", "motor",
    "drive", "controller", "layout", "detail", "details", "left", "right", "front",
    "back", "top", "bottom", "open", "closed", "male", "female",
}


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip()).casefold()


def language_neutral_candidate(item: dict) -> str | None:
    names = item.get("names") or {}
    values = [value for lang, value in names.items() if lang != "zh" and str(value).strip()]
    if not values:
        return None

    counts = Counter(normalize(value) for value in values)
    normalized, count = counts.most_common(1)[0]
    if count < 2 or count < max(2, len(values) * 0.5):
        return None

    english = names.get("en")
    if english and normalize(english) == normalized:
        candidate = english.strip()
    else:
        candidate = next(value.strip() for value in values if normalize(value) == normalized)

    chunks = re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ]+", candidate)
    if not chunks:
        return None
    if any(chunk.casefold() in _BLOCKED_FUNCTION_WORDS for chunk in chunks):
        return None
    if not all(chunk.isupper() or len(chunk) <= 3 for chunk in chunks):
        return None
    return candidate


def _clean_adjustments(current: str | None) -> str:
    parts = [] if not current or current == "none" else [p.strip() for p in current.split(";") if p.strip()]
    parts = [p for p in parts if not p.startswith("german_name_fallback:")]
    if "language_neutral_name_accepted" not in parts:
        parts.append("language_neutral_name_accepted")
    return "; ".join(sorted(parts))


def finalize_library(library_text: str, audit: dict) -> tuple[str, dict]:
    accepted_by_path: dict[str, str] = {}
    for item in audit.get("items", []):
        candidate = language_neutral_candidate(item)
        if candidate:
            accepted_by_path[item["path"]] = candidate

    lines = library_text.splitlines()
    result: list[str] = []
    applied: list[str] = []
    block: list[str] | None = None

    def process(symbol: list[str]) -> list[str]:
        path = property_value(symbol, "QET_Source_Path")
        if not path or path not in accepted_by_path:
            return symbol
        candidate = accepted_by_path[path]
        category = property_value(symbol, "QET_Category") or ""
        old_value = property_value(symbol, "Value") or ""
        adjustments = property_value(symbol, "QET_Adjustments")
        keywords = property_value(symbol, "ki_keywords") or ""

        if not replace_property(symbol, "Value", candidate):
            raise ValueError(f"Missing Value property for {path}")
        if not replace_property(symbol, "Description", f"{candidate} | QET-Kategorie: {category}"):
            raise ValueError(f"Missing Description property for {path}")
        if not replace_property(symbol, "QET_Adjustments", _clean_adjustments(adjustments)):
            raise ValueError(f"Missing QET_Adjustments property for {path}")

        keyword_parts = [candidate]
        if old_value and normalize(old_value) != normalize(candidate):
            keyword_parts.append(old_value)
        if keywords:
            keyword_parts.append(keywords)
        replace_property(symbol, "ki_keywords", " ".join(keyword_parts))
        applied.append(path)
        return symbol

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

    missing_paths = {item["path"] for item in audit.get("items", [])}
    accepted_paths = set(applied)
    report = {
        "audited_missing_german_names": len(missing_paths),
        "language_neutral_candidates": len(accepted_by_path),
        "language_neutral_applied": len(applied),
        "applied_paths": sorted(applied),
        "remaining_translation_paths": sorted(missing_paths - accepted_paths),
        "remaining_translation_count": len(missing_paths - accepted_paths),
    }
    return "\n".join(result) + ("\n" if library_text.endswith("\n") else ""), report


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Accept conservative language-neutral QET model names.")
    parser.add_argument("--library", type=Path, required=True)
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args(argv)

    audit = json.loads(args.audit.read_text(encoding="utf-8"))
    finalized, report = finalize_library(args.library.read_text(encoding="utf-8"), audit)
    args.library.write_text(finalized, encoding="utf-8", newline="\n")
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if not k.endswith("_paths")}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
