"""Lesendes Einlesen nativer KiCad-Bibliothekstabellen.

Unterstützt werden `sym-lib-table` und `fp-lib-table`. Die Einträge bleiben
KiCad-nah; ProjectOS löst lediglich ausdrücklich bereitgestellte Variablen auf
und prüft die resultierenden Dateipfade gegen erlaubte Wurzelverzeichnisse.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import PurePosixPath
import re
from types import MappingProxyType
from typing import Mapping


_TOKEN_PATTERN = re.compile(r'\s*(?:(\()|(\))|"((?:\\.|[^"\\])*)"|([^\s()]+))')
_VARIABLE_PATTERN = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}")
_WINDOWS_DRIVE_PATTERN = re.compile(r"^[A-Za-z]:/")


class KiCadLibraryTableType(StrEnum):
    SYMBOL = "SYMBOL"
    FOOTPRINT = "FOOTPRINT"

    @property
    def root_name(self) -> str:
        return "sym_lib_table" if self is KiCadLibraryTableType.SYMBOL else "fp_lib_table"


@dataclass(frozen=True, slots=True)
class KiCadVariableContext:
    variables: Mapping[str, str]
    allowed_roots: tuple[str, ...]

    def __post_init__(self) -> None:
        normalized_variables: dict[str, str] = {}
        for name, value in self.variables.items():
            key = name.strip()
            resolved = _normalize_path(value)
            if not key:
                raise ValueError("ERR-KICAD-0032: Ein Variablenname darf nicht leer sein.")
            if not resolved:
                raise ValueError(f"ERR-KICAD-0033: Die KiCad-Variable {key} besitzt keinen Pfad.")
            normalized_variables[key] = resolved

        roots = tuple(dict.fromkeys(_normalize_path(root) for root in self.allowed_roots if root.strip()))
        if not roots:
            raise ValueError("ERR-KICAD-0034: Mindestens ein erlaubtes KiCad-Wurzelverzeichnis ist erforderlich.")
        object.__setattr__(self, "variables", MappingProxyType(normalized_variables))
        object.__setattr__(self, "allowed_roots", roots)


@dataclass(frozen=True, slots=True)
class KiCadLibraryTableEntry:
    table_type: KiCadLibraryTableType
    name: str
    plugin_type: str
    uri: str
    resolved_path: str
    options: str = ""
    description: str = ""

    def __post_init__(self) -> None:
        name = self.name.strip()
        plugin_type = self.plugin_type.strip()
        uri = self.uri.strip()
        resolved_path = _normalize_path(self.resolved_path)
        if not name:
            raise ValueError("ERR-KICAD-0035: Ein Bibliothekstabelleneintrag benötigt einen Namen.")
        if not plugin_type:
            raise ValueError("ERR-KICAD-0036: Ein Bibliothekstabelleneintrag benötigt einen Plugin-Typ.")
        if not uri:
            raise ValueError("ERR-KICAD-0037: Ein Bibliothekstabelleneintrag benötigt eine URI.")
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "plugin_type", plugin_type)
        object.__setattr__(self, "uri", uri)
        object.__setattr__(self, "resolved_path", resolved_path)
        object.__setattr__(self, "options", self.options.strip())
        object.__setattr__(self, "description", self.description.strip())


@dataclass(frozen=True, slots=True)
class KiCadLibraryTable:
    table_type: KiCadLibraryTableType
    entries: tuple[KiCadLibraryTableEntry, ...]

    def get(self, name: str) -> KiCadLibraryTableEntry | None:
        key = name.strip().casefold()
        return next((entry for entry in self.entries if entry.name.casefold() == key), None)


class KiCadLibraryTableParser:
    """Parst eine native KiCad-Bibliothekstabelle ohne sie zu verändern."""

    def parse(
        self,
        *,
        table_type: KiCadLibraryTableType,
        content: str,
        context: KiCadVariableContext,
    ) -> KiCadLibraryTable:
        root = _parse_sexpression(content)
        if _head(root) != table_type.root_name:
            raise ValueError(
                f"ERR-KICAD-0038: Die Datei ist keine passende KiCad-{table_type.value}-Bibliothekstabelle."
            )

        entries: list[KiCadLibraryTableEntry] = []
        names: set[str] = set()
        for node in root[1:]:
            if not isinstance(node, list) or _head(node) != "lib":
                continue
            fields = _read_fields(node)
            name = fields.get("name", "")
            name_key = name.casefold()
            if name_key in names:
                raise ValueError(f"ERR-KICAD-0039: Doppelter Bibliotheksname: {name}.")
            uri = fields.get("uri", "")
            resolved_path = _resolve_uri(uri, context)
            entries.append(KiCadLibraryTableEntry(
                table_type=table_type,
                name=name,
                plugin_type=fields.get("type", ""),
                uri=uri,
                resolved_path=resolved_path,
                options=fields.get("options", ""),
                description=fields.get("descr", ""),
            ))
            names.add(name_key)

        return KiCadLibraryTable(table_type, tuple(entries))


def _resolve_uri(uri: str, context: KiCadVariableContext) -> str:
    text = uri.strip().replace("\\", "/")
    if not text:
        raise ValueError("ERR-KICAD-0037: Ein Bibliothekstabelleneintrag benötigt eine URI.")
    if "://" in text and not text.startswith("file://"):
        raise ValueError("ERR-KICAD-0040: Nur lokale KiCad-Bibliotheks-URIs werden unterstützt.")
    if text.startswith("file://"):
        text = text[7:]

    unknown: set[str] = set()

    def replace_variable(match: re.Match[str]) -> str:
        name = match.group(1)
        value = context.variables.get(name)
        if value is None:
            unknown.add(name)
            return match.group(0)
        return value

    expanded = _VARIABLE_PATTERN.sub(replace_variable, text)
    if unknown:
        names = ", ".join(sorted(unknown))
        raise ValueError(f"ERR-KICAD-0041: Unbekannte KiCad-Variable: {names}.")
    if "${" in expanded:
        raise ValueError("ERR-KICAD-0041: Die KiCad-URI enthält eine nicht auflösbare Variable.")

    resolved = _collapse_path(_normalize_path(expanded))
    if not _is_absolute(resolved):
        project_root = context.variables.get("KIPRJMOD")
        if project_root is None:
            raise ValueError("ERR-KICAD-0042: Relative Bibliothekspfade benötigen KIPRJMOD.")
        resolved = _collapse_path(f"{project_root}/{resolved}")

    if not any(_is_within(resolved, root) for root in context.allowed_roots):
        raise ValueError("ERR-KICAD-0043: Der aufgelöste Bibliothekspfad liegt außerhalb erlaubter Wurzeln.")
    return resolved


def _normalize_path(value: str) -> str:
    return value.strip().replace("\\", "/").rstrip("/")


def _collapse_path(value: str) -> str:
    prefix = "/" if value.startswith("/") else ""
    drive = value[:2] if _WINDOWS_DRIVE_PATTERN.match(value) else ""
    rest = value[2:] if drive else value
    parts: list[str] = []
    for part in PurePosixPath(rest).parts:
        if part in {"", "/", "."}:
            continue
        if part == "..":
            if not parts:
                raise ValueError("ERR-KICAD-0044: Der Bibliothekspfad verlässt seine Wurzel.")
            parts.pop()
        else:
            parts.append(part)
    base = "/".join(parts)
    if drive:
        return f"{drive}/{base}" if base else f"{drive}/"
    return f"{prefix}{base}" if prefix else base


def _is_absolute(path: str) -> bool:
    return path.startswith("/") or bool(_WINDOWS_DRIVE_PATTERN.match(path))


def _is_within(path: str, root: str) -> bool:
    normalized_path = _collapse_path(path).casefold()
    normalized_root = _collapse_path(root).rstrip("/").casefold()
    return normalized_path == normalized_root or normalized_path.startswith(f"{normalized_root}/")


def _read_fields(node: list[object]) -> dict[str, str]:
    fields: dict[str, str] = {}
    for child in node[1:]:
        if isinstance(child, list) and len(child) > 1:
            fields[str(child[0])] = str(child[1])
    return fields


def _parse_sexpression(text: str) -> list[object]:
    tokens: list[str] = []
    position = 0
    while position < len(text):
        match = _TOKEN_PATTERN.match(text, position)
        if match is None:
            raise ValueError("ERR-KICAD-0031: Ungültige KiCad-S-Expression.")
        position = match.end()
        if match.group(1):
            tokens.append("(")
        elif match.group(2):
            tokens.append(")")
        elif match.group(3) is not None:
            tokens.append(bytes(match.group(3), "utf-8").decode("unicode_escape"))
        elif match.group(4):
            tokens.append(match.group(4))

    root: list[object] | None = None
    stack: list[list[object]] = []
    for token in tokens:
        if token == "(":
            node: list[object] = []
            if stack:
                stack[-1].append(node)
            stack.append(node)
            if root is None:
                root = node
        elif token == ")":
            if not stack:
                raise ValueError("ERR-KICAD-0031: Ungültige KiCad-S-Expression.")
            stack.pop()
        else:
            if not stack:
                raise ValueError("ERR-KICAD-0031: Ungültige KiCad-S-Expression.")
            stack[-1].append(token)
    if root is None or stack:
        raise ValueError("ERR-KICAD-0031: Ungültige KiCad-S-Expression.")
    return root


def _head(node: list[object]) -> str | None:
    return str(node[0]) if node else None
