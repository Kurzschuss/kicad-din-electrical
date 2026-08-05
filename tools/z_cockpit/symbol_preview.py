from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from tools.validate_device_catalog import REPO_ROOT


@dataclass(frozen=True)
class SymbolPreview:
    reference: str
    library: str
    symbol: str
    relative_url: str
    file_path: Path
    available: bool


def parse_symbol_reference(reference: str) -> tuple[str, str]:
    """Zerlegt eine KiCad-Symbolreferenz im Format Bibliothek:Symbol."""
    if reference.count(":") != 1:
        raise ValueError(f"Ungültige Symbolreferenz: {reference}")
    library, symbol = (part.strip() for part in reference.split(":", 1))
    if not library or not symbol:
        raise ValueError(f"Ungültige Symbolreferenz: {reference}")
    if any(part in {".", ".."} or "/" in part or "\\" in part for part in (library, symbol)):
        raise ValueError(f"Unsichere Symbolreferenz: {reference}")
    return library, symbol


def symbol_preview(reference: str, repo_root: Path = REPO_ROOT) -> SymbolPreview:
    library, symbol = parse_symbol_reference(reference)
    relative_url = f"symbol-previews/{library}/{symbol}.svg"
    file_path = repo_root / "docs" / "site" / relative_url
    return SymbolPreview(
        reference=reference,
        library=library,
        symbol=symbol,
        relative_url=relative_url,
        file_path=file_path,
        available=file_path.is_file(),
    )
