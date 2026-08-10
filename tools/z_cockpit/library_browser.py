from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping

from tools.generate_device_catalog_html import collect_devices
from tools.validate_device_catalog import REPO_ROOT

from .footprint_preview import footprint_assignment
from .symbol_preview import symbol_preview
from .three_d_preview import three_d_preview_assignment

_TOP_LEVEL_SYMBOL = re.compile(r'^  \(symbol "([^"]+)"')


@dataclass(frozen=True)
class LibrarySymbol:
    reference: str
    name: str
    device_ids: tuple[str, ...]
    device_count: int
    symbol_preview_available: bool
    footprint_name: str | None
    footprint_available: bool
    footprint_preview_available: bool
    three_d_model_available: bool
    three_d_preview_available: bool
    three_d_preview_status: str


@dataclass(frozen=True)
class SymbolLibrary:
    name: str
    file: Path
    symbols: tuple[LibrarySymbol, ...]
    symbol_count: int
    device_count: int
    footprint_count: int
    complete_preview_count: int
    three_d_model_count: int
    three_d_preview_count: int


def parse_library_symbols(path: Path) -> tuple[str, ...]:
    """Liest ausschließlich die obersten Symbole einer KiCad-Symbolbibliothek."""
    if not path.is_file():
        raise FileNotFoundError(path)
    names = [
        match.group(1)
        for line in path.read_text(encoding="utf-8").splitlines()
        if (match := _TOP_LEVEL_SYMBOL.match(line))
    ]
    if len(names) != len(set(names)):
        raise ValueError(f"Doppelte Symbole in {path.name}")
    return tuple(names)


def _device_index(devices: Iterable[Mapping[str, object]]) -> dict[str, tuple[str, ...]]:
    index: dict[str, list[str]] = {}
    for device in devices:
        reference = str(device.get("symbol") or "")
        device_id = str(device.get("id") or "")
        if not reference or not device_id:
            continue
        index.setdefault(reference, []).append(device_id)
    return {reference: tuple(sorted(ids)) for reference, ids in index.items()}


def collect_symbol_libraries(
    repo_root: Path = REPO_ROOT,
    devices: Iterable[Mapping[str, object]] | None = None,
) -> tuple[SymbolLibrary, ...]:
    """Verknüpft Bibliotheken, Symbole, Geräte, Footprints und Vorschauen."""
    source_devices = collect_devices()["devices"] if devices is None else devices
    device_index = _device_index(source_devices)
    libraries: list[SymbolLibrary] = []

    for library_file in sorted((repo_root / "symbols").glob("*.kicad_sym")):
        library_name = library_file.stem
        symbols: list[LibrarySymbol] = []
        for symbol_name in parse_library_symbols(library_file):
            reference = f"{library_name}:{symbol_name}"
            symbol_state = symbol_preview(reference, repo_root)
            footprint_state = footprint_assignment(reference, repo_root)
            three_d_state = three_d_preview_assignment(reference, repo_root)
            device_ids = device_index.get(reference, ())
            symbols.append(
                LibrarySymbol(
                    reference=reference,
                    name=symbol_name,
                    device_ids=device_ids,
                    device_count=len(device_ids),
                    symbol_preview_available=symbol_state.available,
                    footprint_name=footprint_state.footprint_name,
                    footprint_available=footprint_state.footprint_available,
                    footprint_preview_available=footprint_state.preview_available,
                    three_d_model_available=three_d_state.model_available,
                    three_d_preview_available=three_d_state.preview_available,
                    three_d_preview_status=three_d_state.preview_status,
                )
            )

        libraries.append(
            SymbolLibrary(
                name=library_name,
                file=library_file,
                symbols=tuple(symbols),
                symbol_count=len(symbols),
                device_count=sum(symbol.device_count for symbol in symbols),
                footprint_count=sum(symbol.footprint_available for symbol in symbols),
                complete_preview_count=sum(
                    symbol.symbol_preview_available and symbol.footprint_preview_available
                    for symbol in symbols
                ),
                three_d_model_count=sum(symbol.three_d_model_available for symbol in symbols),
                three_d_preview_count=sum(symbol.three_d_preview_available for symbol in symbols),
            )
        )

    return tuple(libraries)
