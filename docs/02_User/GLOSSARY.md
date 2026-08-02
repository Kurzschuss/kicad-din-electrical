# Glossar

Dieses Glossar erklärt zentrale Begriffe des Projekts in einfacher Sprache.

## Bibliothek

Eine Sammlung zusammengehöriger KiCad-Elemente. Im Projekt gibt es getrennte Symbol- und Footprintbibliotheken.

## Symbol

Die grafische und elektrische Darstellung eines Bauteils im Schaltplan.

## Symbolbibliothek

Eine Datei mit der Endung `.kicad_sym`, die ein oder mehrere Symbole enthält.

Beispiel:

```text
Z_DIN_Control.kicad_sym
```

## Footprint

Die mechanische Darstellung eines Bauteils für die Leiterplatten- oder Aufbauplanung. Ein Footprint enthält beispielsweise Konturen, Pads, Bohrungen oder Einbaumaße.

## Footprintbibliothek

Ein Ordner mit der Endung `.pretty`, der eine oder mehrere `.kicad_mod`-Dateien enthält.

Beispiel:

```text
Z_DIN_Control.pretty/
```

## `.kicad_sym`

Dateiendung einer KiCad-Symbolbibliothek.

## `.pretty`

Ordnerendung einer KiCad-Footprintbibliothek. Eine `.pretty`-Bibliothek darf mehrere Footprints enthalten.

## `.kicad_mod`

Dateiendung eines einzelnen KiCad-Footprints.

## Bibliotheks-ID

Eine eindeutige Referenz aus Bibliotheksname und Elementname, getrennt durch einen Doppelpunkt.

Beispiel:

```text
Z_DIN_Module_18mm:Z_DIN_Module_18mm
```

## Qualifizierter Name

Ein vollständiger Name einschließlich Bibliothek, beispielsweise `Z_MCB:MCB`. Er verhindert Verwechslungen zwischen gleichnamigen Elementen aus verschiedenen Bibliotheken.

## Präfix `Z_`

Kennzeichnung aller projektinternen Bibliotheken. Dadurch sind sie in KiCad eindeutig erkennbar und alphabetisch gebündelt.

## Globale Bibliothek

Eine Bibliothek, die in allen KiCad-Projekten eines Computers zur Verfügung steht.

## Projektbezogene Bibliothek

Eine Bibliothek, die nur für ein bestimmtes KiCad-Projekt registriert ist.

## Bibliothekstabelle

KiCad-Konfiguration, in der Bibliotheksnamen und Dateipfade gespeichert werden. Symbol- und Footprintbibliotheken verwenden getrennte Tabellen.

## Repository

Der vollständige Projektordner mit Bibliotheken, Dokumentation, Tests und Versionsgeschichte.

## Git

Versionsverwaltung, die Änderungen an Dateien nachvollziehbar speichert.

## GitHub

Online-Plattform, auf der das Repository verwaltet, geprüft und gemeinsam weiterentwickelt wird.

## GitHub Desktop

Grafische Anwendung zum Klonen, Aktualisieren, Committen und Übertragen eines GitHub-Repositorys.

## Branch

Ein eigener Entwicklungszweig. Änderungen werden dort vorbereitet, ohne `main` sofort zu verändern.

## `main`

Der zentrale, freigegebene Entwicklungsstand des Repositorys.

## Commit

Gespeicherter Änderungsschritt mit Beschreibung und eindeutiger Kennung.

## Pull Request

Vorschlag, Änderungen aus einem Branch nach Prüfung in `main` zu übernehmen.

## CI

Abkürzung für Continuous Integration. Bei Änderungen führt GitHub automatisch die Tests des Projekts aus.

## Test

Automatische Prüfung einer festgelegten Projektregel, beispielsweise eines Dateinamens, Ordners oder internen Footprintnamens.

## `pytest`

Python-Testwerkzeug, mit dem die automatischen Projektprüfungen ausgeführt werden.

## `.venv`

Lokale virtuelle Python-Umgebung. Sie hält die für dieses Projekt installierten Pakete getrennt von anderen Python-Projekten.

## `run_tests.bat`

Windows-Testmenü des Repositorys. Es bietet mehrere Testarten, eine Hilfeseite und den Menüpunkt **0 – Programm verlassen**.

## `run_tests.sh`

Teststarter für Linux und macOS.

## Roadmap

Geplanter Entwicklungsweg des Projekts mit Phasen und langfristigen Zielen.

## Issue

Aufgabe, Fehlerbericht oder dokumentierter Vorschlag in GitHub.

## Footprint-Zuordnung

Verknüpfung eines Schaltplansymbols mit einem passenden Footprint.

## DIN-Schaltgerät

Gerät für elektrische Anlagen, das häufig auf Tragschienen oder in Verteilungen eingesetzt wird, beispielsweise Leitungsschutzschalter, Fehlerstrom-Schutzeinrichtungen oder Schütze.

## Reiheneinbaugerät

Gerät mit genormter Bauform zur Montage in elektrischen Verteilungen, typischerweise auf einer Tragschiene.
