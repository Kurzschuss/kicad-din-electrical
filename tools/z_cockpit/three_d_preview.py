from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from tools.generate_3d_previews import preview_source
from tools.validate_device_catalog import REPO_ROOT

from .footprint_preview import footprint_assignment


@dataclass(frozen=True)
class ThreeDPreviewAssignment:
    symbol_reference: str
    footprint_name: str | None
    model_reference: str | None
    model_file: Path | None
    model_available: bool
    preview_available: bool
    preview_relative_url: str | None
    preview_status: str


def three_d_preview_assignment(
    reference: str,
    repo_root: Path = REPO_ROOT,
) -> ThreeDPreviewAssignment:
    """Ermittelt echten 3D-Modellstatus und technische Vorschau eines Symbols."""
    footprint = footprint_assignment(reference, repo_root)
    if not footprint.footprint_file or not footprint.footprint_file.is_file():
        return ThreeDPreviewAssignment(
            symbol_reference=reference,
            footprint_name=footprint.footprint_name,
            model_reference=None,
            model_file=None,
            model_available=False,
            preview_available=False,
            preview_relative_url=None,
            preview_status="Nicht zugeordnet" if not footprint.mapped else "Fehlt",
        )

    source = preview_source(footprint.footprint_file, repo_root)
    preview_file = repo_root / "docs" / "site" / "3d-previews" / f"{source.footprint_name}.svg"
    preview_available = source.preview_available and preview_file.is_file()
    return ThreeDPreviewAssignment(
        symbol_reference=reference,
        footprint_name=footprint.footprint_name,
        model_reference=source.model_reference,
        model_file=source.model_file,
        model_available=source.model_available,
        preview_available=preview_available,
        preview_relative_url=(
            f"3d-previews/{source.footprint_name}.svg" if preview_available else None
        ),
        preview_status=source.status,
    )
