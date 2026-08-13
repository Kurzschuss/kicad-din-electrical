# Entwicklerleitfaden

Dieser Leitfaden beschreibt den technischen Arbeitsablauf im Repository.

## Voraussetzungen

Empfohlen werden:

- Git und GitHub Desktop oder die Git-Kommandozeile,
- Python 3.10 oder neuer,
- eine aktuelle KiCad-Version,
- ein Texteditor oder eine Entwicklungsumgebung.

Die Python-Abhängigkeiten für Tests werden installiert mit:

```text
python -m pip install -r requirements-dev.txt
```

Optional kann eine lokale virtuelle Umgebung verwendet werden:

```text
python -m venv .venv
```

Unter Windows aktivieren:

```text
.venv\Scripts\activate
```

## Wichtige Verzeichnisse

```text
symbols/                          Symbolbibliotheken und Symboldokumentation
footprints/                       .pretty-Footprintbibliotheken
tests/                            zentrale Repositorytests
distributions/                    zusätzliche Prüfungen und Werkzeuge
tools/                            Hilfsprogramme
docs/                             Benutzer- und Entwicklerdokumentation
.github/workflows/                GitHub-Actions-Konfiguration
```

Alle `.kicad_sym`-Dateien müssen direkt unter `symbols/` liegen. Verschachtelte Symbolbibliotheksordner sind nicht zulässig und werden durch Tests verhindert.

## Lokaler Arbeitsablauf

1. `main` aktualisieren.
2. Einen neuen Branch erstellen.
3. Eine klar begrenzte Änderung durchführen.
4. Automatisch erzeugte Referenz aktualisieren.
5. Tests lokal ausführen.
6. Änderungen kontrollieren und committen.
7. Branch pushen und Pull Request öffnen.

## Bibliotheksreferenz

Die Bibliotheksindizes werden aus der tatsächlichen Repositorystruktur erzeugt:

```text
python tools/generate_library_reference.py
```

Nur prüfen:

```text
python tools/generate_library_reference.py --check
```

GitHub Actions führt diese Aktualitätsprüfung ebenfalls aus. Eine Änderung an Bibliotheksdateien ohne aktualisierte Indizes lässt CI fehlschlagen.

Weitere Einzelheiten stehen in:

```text
docs/03_Developer/REFERENCE_GENERATOR.md
```

## Tests

Schneller vollständiger Lauf:

```text
python -m pytest -q
```

Ausführlicher Lauf:

```text
python -m pytest -vv
```

Beim ersten Fehler stoppen:

```text
python -m pytest -x
```

Nur zuletzt fehlgeschlagene Tests wiederholen:

```text
python -m pytest --lf
```

Unter Windows fasst `run_tests.bat` diese Befehle in einem Menü zusammen. Eine Übersicht über lokale Tests und die vollständige CI steht in `docs/02_User/TESTING.md`.

## Neue Strukturregel ergänzen

Eine neue Regel sollte möglichst durch einen Test beschrieben werden. Der Test soll:

- einen eindeutigen Namen besitzen,
- eine verständliche Fehlermeldung ausgeben,
- nur eine fachliche Regel prüfen,
- unabhängig von der Dateireihenfolge arbeiten,
- unter Windows und Linux funktionieren.

Beispielhafte Prüfbereiche:

- erlaubte Dateipfade,
- Namenskonventionen,
- Zuordnung von Symbol- und Footprintbibliotheken,
- interne KiCad-IDs,
- Dokumentationsbeispiele,
- Aktualität erzeugter Dateien.

## CI-Ablauf

Der zentrale Workflow lautet:

```text
.github/workflows/complete-test-suite.yml
```

Er läuft bei Pull Requests gegen `main`, bei Pushes auf `main` und kann über `workflow_dispatch` manuell gestartet werden.

Der Workflow führt derzeit unter anderem aus:

1. Repository-Health-Check,
2. vollständige Pytest-Suite,
3. Python-Syntaxprüfung für `distributions`, `tests` und `tools`,
4. Z_-Quality-Release-Profil,
5. KiCad-Bibliotheksvalidierung,
6. Prüfung erzeugter Gerätevarianten,
7. Gerätekatalogvalidierung,
8. Prüfung der erzeugten Bibliotheksreferenz,
9. Prüfung des Qualitätsberichts,
10. Symbol- und 3D-Preview-Prüfungen,
11. HTML-Referenz und Gerätekatalog-HTML,
12. ProjectOS-Projektvalidator,
13. Erzeugung des Z_Cockpit-HTML.

Der Workflow selbst ist die verbindliche Quelle für den aktuellen CI-Stand. Dokumentationslisten sollen den Ablauf erläutern, aber keine davon ist maßgeblicher als `.github/workflows/complete-test-suite.yml`.

Ein grüner CI-Lauf bestätigt die automatischen Regeln, ersetzt aber nicht die fachliche und visuelle Kontrolle in KiCad.

## KiCad-Dateien bearbeiten

Nach einer Änderung in KiCad vor dem Commit kontrollieren:

- Liegt die `.kicad_sym`-Datei direkt unter `symbols/`?
- Wurde nur die beabsichtigte Bibliothek verändert?
- Stimmen Dateiname und interner Name überein?
- Sind Symbol- und Footprintzuordnungen korrekt?
- Wurden keine lokalen absoluten Pfade gespeichert?
- Öffnet sich die Datei ohne Reparaturmeldung?
- Ist die Darstellung bei üblichen Zoomstufen lesbar?

## Kleine Pull Requests bevorzugen

Bibliotheksinhalte, Regeländerungen, Dokumentation und CI möglichst nicht unnötig in einem großen Pull Request vermischen. Kleine Änderungen sind leichter zu prüfen, zurückzusetzen und später nachzuvollziehen.

## Technische Entscheidungen dokumentieren

Dauerhafte Architektur- und Strukturentscheidungen werden in folgendem Dokument ergänzt:

```text
docs/01_Roadmap/DECISIONS.md
```

Neue Ideen und noch nicht beschlossene Erweiterungen gehören nach:

```text
docs/01_Roadmap/IDEAS.md
```
