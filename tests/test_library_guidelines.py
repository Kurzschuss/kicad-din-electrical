import json
from pathlib import Path

from tools.generate_package_progress import CHECKED_REQUIRED_FIELDS


HANDBOOK = Path("docs/00_Project/LIBRARY_GUIDELINES.md")
ROADMAP = Path("docs/01_Roadmap/PROJECT_ROADMAP.md")
PROJECT_STATE = Path("project_state.yaml")


def test_quality_manual_contains_binding_package_contract():
    text = HANDBOOK.read_text(encoding="utf-8")
    required_sections = (
        "## 2. Grundsatz: Geräte werden als Pakete entwickelt",
        "## 4. Symbolstandard",
        "## 5. Verbindliche Footprint Policy",
        "## 6. Footprintstandard",
        "## 7. 3D-Modelle und 3D-Vorschauen",
        "## 8. Gerätekatalog",
        "## 11. Qualitätsstatus und Reifegrad sind getrennte Begriffe",
        "## 14. Freigabeverfahren für ein Bibliothekspaket",
        "## 15. Verbindliche Prüfkommandos",
        "## 18. Definition of Done",
    )
    for heading in required_sections:
        assert heading in text

    for token in (
        "Z_Footprint_Policy",
        "required",
        "optional",
        "none",
        "kicad_conform",
        "z_conform",
        "needs_rework",
        "temporarily_accepted",
        "Entwurf",
        "Geprüft",
        "Praxisgetestet",
    ):
        assert token in text


def test_checked_package_requirements_are_documented():
    text = HANDBOOK.read_text(encoding="utf-8")
    labels = {
        "symbol": "Symbol",
        "device_data": "Gerätedaten",
        "documentation": "Dokumentation",
        "tests": "automatisierte Tests",
    }
    assert set(CHECKED_REQUIRED_FIELDS) == set(labels)
    for field in CHECKED_REQUIRED_FIELDS:
        assert labels[field] in text
    assert "der Qualitätsstatus darf nicht `needs_rework` sein" in text
    assert "ein dokumentiertes Beispielprojekt ist vorhanden" in text


def test_roadmap_marks_quality_manual_complete():
    text = ROADMAP.read_text(encoding="utf-8")
    assert "- [x] Qualitätshandbuch `docs/00_Project/LIBRARY_GUIDELINES.md` vollständig ausarbeiten" in text


def test_project_state_records_quality_manual_as_done():
    state = json.loads(PROJECT_STATE.read_text(encoding="utf-8"))
    quality = next(item for item in state["milestones"] if item["id"] == "qualitaet")
    task = next(item for item in quality["tasks"] if item["id"] == "qualitaetshandbuch")
    assert task["state"] == "done"
