"""Aufbau eines vollständigen lokalen KiCad-Snapshots aus Bibliothekstabellen.

Symbol- und Footprinttabellen bleiben unabhängig. Eine fehlende Tabelle bedeutet,
dass diese Artefaktart nicht eingelesen wird; sie ist nicht automatisch ein Fehler.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import PurePosixPath
from types import MappingProxyType
from typing import Mapping

from .kicad_library_tables import KiCadLibraryTable, KiCadLibraryTableType
from .kicad_library_validation import KiCadLibraryItemSnapshot
from .kicad_native_snapshot import KiCadNativeSnapshotBuilder, NativeKiCadSource


def _normalize_path(value: str) -> str:
    return value.strip().replace("\\", "/").rstrip("/")


@dataclass(frozen=True, slots=True)
class KiCadLocalFileSet:
    """Explizit bereitgestellte, ausschließlich lesbare KiCad-Dateiquellen."""

    files: Mapping[str, bytes]

    def __post_init__(self) -> None:
        normalized: dict[str, bytes] = {}
        for path, content in self.files.items():
            key = _normalize_path(path)
            if not key:
                raise ValueError("ERR-KICAD-0045: Ein KiCad-Dateipfad darf nicht leer sein.")
            if key in normalized:
                raise ValueError(f"ERR-KICAD-0046: Doppelte KiCad-Dateiquelle: {key}.")
            normalized[key] = bytes(content)
        object.__setattr__(self, "files", MappingProxyType(normalized))

    def read(self, path: str) -> bytes:
        normalized = _normalize_path(path)
        try:
            return self.files[normalized]
        except KeyError as exc:
            raise ValueError(f"ERR-KICAD-0047: KiCad-Datei nicht gefunden: {normalized}.") from exc

    def files_below(self, directory: str, *, suffix: str) -> tuple[tuple[str, bytes], ...]:
        root = _normalize_path(directory)
        prefix = f"{root}/"
        matches = tuple(
            sorted(
                (
                    (path, content)
                    for path, content in self.files.items()
                    if path.startswith(prefix)
                    and "/" not in path[len(prefix):]
                    and path.lower().endswith(suffix.lower())
                ),
                key=lambda item: item[0].casefold(),
            )
        )
        return matches


@dataclass(frozen=True, slots=True)
class KiCadCompleteSnapshotResult:
    items: tuple[KiCadLibraryItemSnapshot, ...]
    symbol_library_count: int
    footprint_library_count: int
    model_source_count: int


class KiCadCompleteSnapshotBuilder:
    """Verbindet KiCad-Tabellen, lokale Dateien und den nativen Snapshot-Parser."""

    def __init__(self, files: KiCadLocalFileSet) -> None:
        self._files = files
        self._native_builder = KiCadNativeSnapshotBuilder()

    def build(
        self,
        *,
        symbol_table: KiCadLibraryTable | None = None,
        footprint_table: KiCadLibraryTable | None = None,
        model_sources: tuple[NativeKiCadSource, ...] = (),
    ) -> KiCadCompleteSnapshotResult:
        if symbol_table is not None and symbol_table.table_type is not KiCadLibraryTableType.SYMBOL:
            raise ValueError("ERR-KICAD-0048: Als Symboltabelle wurde keine sym-lib-table übergeben.")
        if footprint_table is not None and footprint_table.table_type is not KiCadLibraryTableType.FOOTPRINT:
            raise ValueError("ERR-KICAD-0049: Als Footprinttabelle wurde keine fp-lib-table übergeben.")

        sources: list[NativeKiCadSource] = []
        symbol_count = 0
        footprint_count = 0

        if symbol_table is not None:
            for entry in symbol_table.entries:
                sources.append(NativeKiCadSource(
                    entry.name,
                    PurePosixPath(entry.resolved_path).name,
                    self._files.read(entry.resolved_path),
                ))
                symbol_count += 1

        if footprint_table is not None:
            for entry in footprint_table.entries:
                footprints = self._files.files_below(entry.resolved_path, suffix=".kicad_mod")
                if not footprints:
                    raise ValueError(
                        f"ERR-KICAD-0050: Footprintbibliothek enthält keine .kicad_mod-Dateien: {entry.name}."
                    )
                for path, content in footprints:
                    sources.append(NativeKiCadSource(
                        entry.name,
                        PurePosixPath(path).name,
                        content,
                    ))
                footprint_count += 1

        sources.extend(model_sources)
        result = self._native_builder.build(tuple(sources))
        return KiCadCompleteSnapshotResult(
            items=result.items,
            symbol_library_count=symbol_count,
            footprint_library_count=footprint_count,
            model_source_count=len(model_sources),
        )
