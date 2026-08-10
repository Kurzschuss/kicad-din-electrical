from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PageSpec:
    """Beschreibt eine Seite in der zentralen Z_Cockpit-Navigation."""

    page_id: str
    label_de: str
    description_de: str
    implemented: bool = False


DEFAULT_PAGES: tuple[PageSpec, ...] = (
    PageSpec("start", "Start", "Projektstatus und wichtige Kennzahlen", True),
    PageSpec("geraete", "Geräte", "Gerätekatalog mit Filtern und Eigenschaften", True),
    PageSpec("bibliotheken", "Bibliotheken", "Symbole, Footprints und Modelle", True),
    PageSpec("hersteller", "Hersteller", "Hersteller, Serien und Katalogzuordnungen", True),
    PageSpec("qualitaet", "Qualität", "Tests, Regeln und Qualitätsberichte", True),
    PageSpec("diagnose", "Diagnose", "Fehler, Warnungen und Prüfdetails", True),
    PageSpec("sicherheit", "Sicherheit", "Repository-, Versions- und Freigabestatus", True),
    PageSpec("dokumentation", "Dokumentation", "Projekt- und Entwicklerdokumentation", True),
    PageSpec("einstellungen", "Einstellungen", "Sprache, Pfade und Entwickleroptionen"),
)


def page_by_id(page_id: str) -> PageSpec:
    for page in DEFAULT_PAGES:
        if page.page_id == page_id:
            return page
    raise KeyError(f"Unbekannte Z_Cockpit-Seite: {page_id}")
