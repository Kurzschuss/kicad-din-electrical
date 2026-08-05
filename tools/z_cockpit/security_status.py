from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from tools.validate_device_catalog import REPO_ROOT


@dataclass(frozen=True)
class SecurityItem:
    security_id: str
    label_de: str
    state: str
    detail_de: str


def collect_security_status(repo_root: Path = REPO_ROOT) -> tuple[SecurityItem, ...]:
    def present(security_id: str, label: str, path: Path, detail: str) -> SecurityItem:
        if path.exists():
            return SecurityItem(security_id, label, "vorhanden", detail)
        return SecurityItem(security_id, label, "fehlt", f"Fehlt: {path.relative_to(repo_root)}")

    return (
        present(
            "versionspruefung",
            "Versionsprüfung",
            repo_root / "tools" / "check_repository_version.py",
            "Prüfung gegen den aktuellen Stand des offiziellen Repositorys vorhanden",
        ),
        present(
            "entwickler_whitelist",
            "Entwickler-Whitelist",
            repo_root / "config" / "authorized_developers.json",
            "Freigegebene GitHub-Benutzer werden aus einer versionierten Datei gelesen",
        ),
        present(
            "codeowners",
            "CODEOWNERS",
            repo_root / ".github" / "CODEOWNERS",
            "Sicherheitsrelevante Dateien sind einem Code Owner zugeordnet",
        ),
        SecurityItem(
            "repository_zustand",
            "Repository-Zustand",
            "laufzeitpruefung",
            "Originalität, lokaler Änderungsstand und offizielles Remote werden beim Fehlerbericht geprüft",
        ),
        SecurityItem(
            "ruleset",
            "GitHub-Ruleset",
            "vorbereitet" if (repo_root / ".github" / "rulesets" / "main-branch-protection-v1.json").is_file() else "fehlt",
            "Ruleset-Vorlage vorbereitet, serverseitige Aktivierung noch nicht bestätigt",
        ),
    )
