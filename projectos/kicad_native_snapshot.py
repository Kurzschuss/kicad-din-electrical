"""Lesender Import nativer KiCad-Bibliotheksdateien in den lokalen Snapshot.

Der Import verändert keine KiCad-Dateien. Unterstützt werden moderne S-Expression-
Symbolbibliotheken, einzelne Footprint-Dateien und 3D-Modelldateien.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import PurePosixPath
import re

from .kicad_assets import KiCadAssetType
from .kicad_library_validation import KiCadLibraryItemSnapshot


_SYMBOL_SUFFIX = ".kicad_sym"
_FOOTPRINT_SUFFIX = ".kicad_mod"
_MODEL_SUFFIXES = {".step", ".stp", ".wrl"}
_TOKEN_PATTERN = re.compile(r'\s*(?:(\()|(\))|"((?:\\.|[^"\\])*)"|([^\s()]+))')


@dataclass(frozen=True, slots=True)
class NativeKiCadSource:
    library: str
    relative_path: str
    content: bytes

    def __post_init__(self) -> None:
        library = self.library.strip()
        path_text = self.relative_path.strip().replace("\\", "/")
        path = PurePosixPath(path_text)
        if not library:
            raise ValueError("ERR-KICAD-0023: Der Bibliotheksname darf nicht leer sein.")
        if not path_text or path.is_absolute() or ".." in path.parts:
            raise ValueError("ERR-KICAD-0024: Der KiCad-Quellpfad muss relativ und sicher sein.")
        object.__setattr__(self, "library", library)
        object.__setattr__(self, "relative_path", path_text)


@dataclass(frozen=True, slots=True)
class KiCadSnapshotBuildResult:
    items: tuple[KiCadLibraryItemSnapshot, ...]
    source_count: int


class KiCadNativeSnapshotBuilder:
    """Erzeugt einen deterministischen Snapshot aus nativen KiCad-Quellen."""

    def build(self, sources: tuple[NativeKiCadSource, ...]) -> KiCadSnapshotBuildResult:
        items: list[KiCadLibraryItemSnapshot] = []
        for source in sources:
            suffix = PurePosixPath(source.relative_path).suffix.lower()
            if suffix == _SYMBOL_SUFFIX:
                items.extend(self._read_symbol_library(source))
            elif suffix == _FOOTPRINT_SUFFIX:
                items.append(self._read_footprint(source))
            elif suffix in _MODEL_SUFFIXES:
                items.append(self._read_model(source))
            else:
                raise ValueError(
                    f"ERR-KICAD-0025: Nicht unterstütztes KiCad-Dateiformat: {suffix or '<ohne>'}."
                )

        unique: dict[tuple[KiCadAssetType, str], KiCadLibraryItemSnapshot] = {}
        for item in items:
            key = (item.asset_type, item.qualified_name.casefold())
            if key in unique:
                raise ValueError(
                    f"ERR-KICAD-0026: Doppelter Bibliothekseintrag: {item.qualified_name}."
                )
            unique[key] = item
        ordered = tuple(sorted(unique.values(), key=lambda item: (item.asset_type.value, item.qualified_name.casefold())))
        return KiCadSnapshotBuildResult(ordered, len(sources))

    def _read_symbol_library(self, source: NativeKiCadSource) -> tuple[KiCadLibraryItemSnapshot, ...]:
        root = _parse_sexpression(_decode_text(source))
        if _head(root) != "kicad_symbol_lib":
            raise ValueError("ERR-KICAD-0027: Die Datei ist keine native KiCad-Symbolbibliothek.")
        result: list[KiCadLibraryItemSnapshot] = []
        for child in root[1:]:
            if not isinstance(child, list) or _head(child) != "symbol" or len(child) < 2:
                continue
            name = str(child[1]).strip()
            pins = tuple(dict.fromkeys(_collect_pin_numbers(child)))
            result.append(KiCadLibraryItemSnapshot(
                KiCadAssetType.SYMBOL,
                f"{source.library}:{name}",
                pins,
                _checksum(source.content),
            ))
        if not result:
            raise ValueError("ERR-KICAD-0028: Die Symbolbibliothek enthält keine Symbole.")
        return tuple(result)

    def _read_footprint(self, source: NativeKiCadSource) -> KiCadLibraryItemSnapshot:
        root = _parse_sexpression(_decode_text(source))
        if _head(root) not in {"footprint", "module"}:
            raise ValueError("ERR-KICAD-0029: Die Datei ist kein natives KiCad-Footprint.")
        name = str(root[1]).strip() if len(root) > 1 else PurePosixPath(source.relative_path).stem
        return KiCadLibraryItemSnapshot(
            KiCadAssetType.FOOTPRINT,
            f"{source.library}:{name}",
            checksum_sha256=_checksum(source.content),
        )

    def _read_model(self, source: NativeKiCadSource) -> KiCadLibraryItemSnapshot:
        name = PurePosixPath(source.relative_path).stem
        return KiCadLibraryItemSnapshot(
            KiCadAssetType.MODEL_3D,
            f"{source.library}:{name}",
            checksum_sha256=_checksum(source.content),
        )


def _decode_text(source: NativeKiCadSource) -> str:
    try:
        return source.content.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("ERR-KICAD-0030: Die KiCad-Textdatei ist nicht UTF-8-kodiert.") from exc


def _checksum(content: bytes) -> str:
    return sha256(content).hexdigest()


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
    stack: list[list[object]] = []
    root: list[object] | None = None
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


def _collect_pin_numbers(node: list[object]) -> list[str]:
    numbers: list[str] = []
    if _head(node) == "pin":
        for child in node[1:]:
            if isinstance(child, list) and _head(child) == "number" and len(child) > 1:
                number = str(child[1]).strip()
                if number:
                    numbers.append(number)
    for child in node[1:]:
        if isinstance(child, list):
            numbers.extend(_collect_pin_numbers(child))
    return numbers
