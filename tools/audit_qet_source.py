#!/usr/bin/env python3
"""Audit QElectroTech source metadata before translation/override work."""
from __future__ import annotations

import argparse
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Sequence

from qet_xml import parse_qet_file


def element_names(root: ET.Element) -> dict[str, str]:
    names: dict[str, str] = {}
    container = root.find("names")
    if container is None:
        return names
    for node in container.findall("name"):
        lang = (node.get("lang") or "").strip()
        value = (node.text or "").strip()
        if lang and value:
            names[lang] = value
    return names


def discover_files(qet_root: Path, scopes: Sequence[str]) -> list[Path]:
    files: list[Path] = []
    for scope in scopes:
        scope_root = qet_root / scope
        if not scope_root.is_dir():
            raise FileNotFoundError(f"QET scope not found: {scope_root}")
        files.extend(scope_root.rglob("*.elmt"))
    return sorted(set(files), key=lambda path: path.as_posix().casefold())


def audit(qet_root: Path, scopes: Sequence[str]) -> dict:
    files = discover_files(qet_root, scopes)
    missing_de: list[dict] = []
    parse_errors: list[dict] = []
    sanitized_xml_files: list[dict] = []

    for source_file in files:
        rel = source_file.relative_to(qet_root)
        source_path = str(Path("10_electric") / rel).replace("\\", "/")
        try:
            root, replaced = parse_qet_file(source_file)
            if replaced:
                sanitized_xml_files.append(
                    {
                        "path": source_path,
                        "invalid_codepoints": replaced,
                    }
                )
            names = element_names(root)
            description = root.find("description")
            terminals = [] if description is None else list(description.findall("terminal"))
            if not names.get("de"):
                missing_de.append(
                    {
                        "path": source_path,
                        "category": " / ".join(("10_electric",) + rel.parent.parts),
                        "filename": source_file.name,
                        "names": names,
                        "terminal_count": len(terminals),
                    }
                )
        except Exception as exc:
            parse_errors.append(
                {
                    "path": source_path,
                    "error": f"{type(exc).__name__}: {exc}",
                }
            )

    return {
        "scopes": list(scopes),
        "source_files": len(files),
        "missing_german_names": len(missing_de),
        "sanitized_xml_files": sanitized_xml_files,
        "parse_errors": parse_errors,
        "items": missing_de,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit QET source names without modifying them.")
    parser.add_argument("--qet-root", type=Path, required=True)
    parser.add_argument("--scope", action="append", dest="scopes")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)

    report = audit(args.qet_root, args.scopes or ["10_allpole"])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps({k: v for k, v in report.items() if k != "items"}, ensure_ascii=False, indent=2))
    return 2 if report["parse_errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
