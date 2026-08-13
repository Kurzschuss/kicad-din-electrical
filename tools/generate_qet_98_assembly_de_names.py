#!/usr/bin/env python3
"""Generate reviewed German names for QET 98_graphics assembly-plan device views.

The QET source audit is authoritative. Only missing-German items below
`99_assembly_plan/01_thumbnails_mounting_plate` are handled. The generator fails
closed if the pinned QET collection adds an unhandled path or changes the
expected count.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from qet_98_assembly_common import normalize_spaces
import qet_98_assembly_legrand as legrand
import qet_98_assembly_other as other
import qet_98_assembly_schneider as schneider

SOURCE_COMMIT = "42692ea76d2fcc3c6cf1ca335951584cd0978922"
ASSEMBLY_PREFIX = "10_electric/98_graphics/99_assembly_plan/01_thumbnails_mounting_plate/"
EXPECTED_ASSEMBLY_OVERRIDES = 423


def assembly_name(item: dict) -> str:
    path = item["path"]
    if not path.startswith(ASSEMBLY_PREFIX):
        raise ValueError(f"outside assembly scope: {path}")
    vendor = path[len(ASSEMBLY_PREFIX):].split("/", 1)[0]
    if vendor == "legrand":
        return legrand.german_name(item)
    if vendor == "schneider_electric":
        return schneider.german_name(item)
    return other.german_name(item, vendor)


def generate(audit: dict) -> dict[str, str]:
    result: dict[str, str] = {}
    for item in audit.get("items", []):
        path = item["path"]
        if not path.startswith(ASSEMBLY_PREFIX):
            continue
        name = normalize_spaces(assembly_name(item))
        if not name:
            raise ValueError(f"empty generated name: {path}")
        result[path] = name

    if len(result) != EXPECTED_ASSEMBLY_OVERRIDES:
        raise ValueError(
            f"expected {EXPECTED_ASSEMBLY_OVERRIDES} assembly overrides, got {len(result)}"
        )
    return result


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate path-bound German names for QET 98 assembly graphics."
    )
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)

    audit = json.loads(args.audit.read_text(encoding="utf-8"))
    overrides = generate(audit)
    payload = {
        "schema_version": 1,
        "source_commit": SOURCE_COMMIT,
        "scope": ASSEMBLY_PREFIX.rstrip("/"),
        "overrides": dict(sorted(overrides.items())),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "generated_overrides": len(overrides),
                "scope": payload["scope"],
                "source_commit": SOURCE_COMMIT,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
