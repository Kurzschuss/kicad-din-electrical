#!/usr/bin/env python3
from __future__ import annotations

import pathlib
import re


def subgroup(item: dict, vendor: str) -> str:
    parts = pathlib.PurePosixPath(item["path"]).parts
    index = parts.index(vendor)
    return "/".join(parts[index + 1:-1])


def source_name(item: dict) -> str:
    names = item.get("names") or {}
    return names.get("fr") or names.get("en") or next(iter(names.values()))


def filename_stem(item: dict) -> str:
    return pathlib.PurePosixPath(item["path"]).stem


def article_code(item: dict) -> str | None:
    match = re.match(r"([0-9]{5,6}[A-Za-z]?)", filename_stem(item))
    return match.group(1) if match else None


def suffix_after_dash(text: str) -> str:
    return text.split(" - ", 1)[1] if " - " in text else text


def normalize_spaces(text: str) -> str:
    return " ".join(text.split())
