#!/usr/bin/env python3
"""Merge generated QET KiCad symbol libraries into one master library.

All inputs must use the converter's KiCad symbol-library format.  Top-level
symbol names and QET source paths are checked globally.  If two independently
generated collection libraries reuse the same internal symbol name, the later
symbol is renamed deterministically with its QET collection root while its
visible Value and metadata remain unchanged.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Sequence

HEADER_RE = re.compile(r'^\(kicad_symbol_lib \(version (\d+)\) \(generator ([^)]+)\)$')
TOP_SYMBOL_RE = re.compile(r'^  \(symbol "([^"]+)"')
SOURCE_PATH_RE = re.compile(r'^    \(property "QET_Source_Path" "([^"]+)"')


def parse_library(path: Path) -> tuple[str, list[list[str]]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines:
        raise ValueError(f"Empty KiCad symbol library: {path}")
    header = lines[0]
    if not HEADER_RE.match(header):
        raise ValueError(f"Unsupported KiCad symbol-library header in {path}: {header!r}")
    if lines[-1] != ")":
        raise ValueError(f"Missing final library close in {path}")

    blocks: list[list[str]] = []
    current: list[str] | None = None
    for line in lines[1:-1]:
        if TOP_SYMBOL_RE.match(line):
            if current is not None:
                blocks.append(current)
            current = [line]
        elif current is None:
            if line.strip():
                raise ValueError(f"Unexpected top-level content in {path}: {line!r}")
        else:
            current.append(line)
    if current is not None:
        blocks.append(current)
    return header, blocks


def top_symbol_name(block: list[str]) -> str:
    match = TOP_SYMBOL_RE.match(block[0])
    if not match:
        raise ValueError(f"Malformed top-level symbol block: {block[0]!r}")
    return match.group(1)


def source_path(block: list[str]) -> str:
    for line in block:
        match = SOURCE_PATH_RE.match(line)
        if match:
            return match.group(1)
    raise ValueError(f"Missing QET_Source_Path in symbol {top_symbol_name(block)}")


def rename_symbol_block(block: list[str], old_name: str, new_name: str) -> list[str]:
    # Converter-generated nested unit names are derived from the top-level name.
    # Restrict the replacement to quoted symbol-name prefixes, never properties.
    marker = f'(symbol "{old_name}'
    replacement = f'(symbol "{new_name}'
    return [line.replace(marker, replacement, 1) if marker in line else line for line in block]


def merge_libraries(paths: Sequence[Path]) -> tuple[str, dict]:
    if not paths:
        raise ValueError("At least one input library is required")

    parsed = [(path, *parse_library(path)) for path in paths]
    headers = {header for _, header, _ in parsed}
    if len(headers) != 1:
        raise ValueError(f"Input library headers differ: {sorted(headers)}")
    header = next(iter(headers))

    merged: list[list[str]] = []
    used_names: dict[str, str] = {}
    used_paths: set[str] = set()
    renames: list[dict[str, str]] = []
    collection_counts: Counter[str] = Counter()
    input_counts: dict[str, int] = {}

    for path, _, blocks in parsed:
        input_counts[path.name] = len(blocks)
        for block in blocks:
            name = top_symbol_name(block)
            qet_path = source_path(block)
            if qet_path in used_paths:
                raise ValueError(f"Duplicate QET source path across input libraries: {qet_path}")
            used_paths.add(qet_path)
            collection = qet_path.split("/", 1)[0]
            collection_counts[collection] += 1

            final_name = name
            if final_name in used_names:
                base = f"Z_Q_{collection}__{name.removeprefix('Z_Q_')}"
                final_name = base
                index = 2
                while final_name in used_names:
                    final_name = f"{base}__{index}"
                    index += 1
                block = rename_symbol_block(block, name, final_name)
                renames.append(
                    {
                        "source_path": qet_path,
                        "old_name": name,
                        "new_name": final_name,
                        "collides_with_source_path": used_names[name],
                    }
                )
            used_names[final_name] = qet_path
            merged.append(block)

    lines = [header]
    for block in merged:
        lines.extend(block)
    lines.append(")")
    text = "\n".join(lines) + "\n"

    report = {
        "input_libraries": input_counts,
        "merged_symbols": len(merged),
        "unique_source_paths": len(used_paths),
        "collection_counts": dict(sorted(collection_counts.items())),
        "duplicate_internal_names_resolved": len(renames),
        "renames": renames,
    }
    return text, report


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Merge generated QET KiCad symbol libraries")
    parser.add_argument("--input", type=Path, action="append", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args(argv)

    merged, report = merge_libraries(args.input)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(merged, encoding="utf-8", newline="\n")
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "renames"}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
