from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from tools.validate_device_catalog import REPO_ROOT


@dataclass(frozen=True)
class StatusItem:
    status_id: str
    label_de: str
    available: bool
    detail_de: str


def collect_project_status(repo_root: Path = REPO_ROOT) -> tuple[StatusItem, ...]:
    checks = (
        ("geraetekatalog", "Gerätekatalog", repo_root / "data" / "devices", "Technischer Gerätekatalog vorhanden"),
        ("symbole", "Symbolbibliothek", repo_root / "symbols" / "Z_MCB.kicad_sym", "Zentrale Symbolbibliothek vorhanden"),
        ("footprints", "Footprints", repo_root / "footprints" / "Z_DIN_Module_18mm.pretty", "DIN-Footprintbibliothek vorhanden"),
        ("dokumentation", "Dokumentation", repo_root / "docs" / "03_Developer" / "Z_COCKPIT.md", "Cockpit-Dokumentation vorhanden"),
        ("ruleset", "Repository-Schutz", repo_root / ".github" / "rulesets" / "main-branch-protection-v1.json", "Ruleset-Vorlage vorbereitet, noch nicht aktiviert"),
    )
    return tuple(StatusItem(status_id, label, path.exists(), detail) for status_id, label, path, detail in checks)
