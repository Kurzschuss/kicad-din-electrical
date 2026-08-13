# Tests lokal ausführen

Diese Anleitung richtet sich ausdrücklich auch an Einsteiger. Die Tests prüfen unter anderem Bibliotheksstruktur, Dateinamen, interne Symbol- und Footprint-Namen, Referenzen und dokumentierte Beispiele.

## Voraussetzungen

Benötigt werden:

- Python 3.10 oder neuer
- eine lokale Kopie dieses Repositorys

Git ist nur nötig, wenn das Repository geklont oder aktualisiert werden soll.

## Schnellster Weg unter Windows

1. Öffne den Ordner `kicad-din-electrical` im Windows-Explorer.
2. Doppelklicke auf `run_tests.bat`.
3. Wähle im Menü den gewünschten Testlauf aus.
4. Nach dem Test kehrt das Programm automatisch zum Hauptmenü zurück.
5. Mit **0 – Programm verlassen** wird das Testmenü beendet.

## Auswahlmöglichkeiten im Windows-Menü

### 1 – Schneller Testlauf

Führt alle Tests mit kompakter Ausgabe aus.

Entspricht:

```cmd
python -m pytest -q
```

### 2 – Ausführlicher Testlauf

Zeigt jeden einzelnen Test und sein Ergebnis an.

Entspricht:

```cmd
python -m pytest -vv
```

### 3 – Alle Prüfungen

Führt nacheinander aus:

1. vollständige Testsuite
2. Python-Syntaxprüfung für `distributions/` und `tests/`

### 4 – Beim ersten Fehler stoppen

Beendet den Testlauf sofort beim ersten Fehler. Das ist bei der Fehlersuche hilfreich.

Entspricht:

```cmd
python -m pytest -x
```

### 5 – Nur zuletzt fehlgeschlagene Tests

Wiederholt nur die Tests, die beim vorherigen Lauf fehlgeschlagen sind.

Entspricht:

```cmd
python -m pytest --lf
```

### 6 – Hilfe und Erklärungen

Zeigt direkt im Testmenü kurze Hinweise zu den Testarten und zur virtuellen Umgebung `.venv`.

### 0 – Programm verlassen

Beendet das Testmenü und schließt das Fenster.

## Einmalige Einrichtung

Öffne im Repositoryordner eine Eingabeaufforderung oder PowerShell.

### Empfohlene virtuelle Umgebung

Eine virtuelle Umgebung hält die Python-Pakete dieses Projekts getrennt von anderen Python-Installationen.

```cmd
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements-dev.txt
```

Der Ordner `.venv` ist optional. Das Testmenü verwendet ihn automatisch, wenn er vorhanden ist. Ohne `.venv` wird die normale Python-Installation verwendet.

### Ohne virtuelle Umgebung

```cmd
python -m pip install -r requirements-dev.txt
```

## Linux und macOS

Einmalige Einrichtung:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
```

Skript ausführbar machen:

```bash
chmod +x run_tests.sh
```

Tests starten:

```bash
./run_tests.sh
```

## Einzelne Tests manuell ausführen

Nur eine Testdatei:

```bash
python -m pytest tests/test_symbol_matched_footprint_libraries.py
```

Nur einen bestimmten Test:

```bash
python -m pytest tests/test_symbol_matched_footprint_libraries.py::test_every_symbol_library_has_matching_pretty_directory
```

## Häufige Fehler

### `Python wurde nicht gefunden`

Python ist nicht installiert oder nicht im Suchpfad eingetragen. Nach der Installation sollte ein neues Terminal geöffnet werden.

### `pytest ist nicht installiert`

Installiere die Entwicklungsabhängigkeiten:

```cmd
python -m pip install -r requirements-dev.txt
```

### Das Menü zeigt nach einem Test wieder die Auswahl

Das ist beabsichtigt. So können mehrere Testarten nacheinander ausgeführt werden, ohne die Batchdatei erneut zu starten. Mit **0 – Programm verlassen** wird das Menü beendet.

## GitHub Actions und vollständige Repository-Prüfung

Die zentrale CI heißt **ProjectOS complete test suite** und ist in
`.github/workflows/complete-test-suite.yml` definiert. Sie läuft bei Pull Requests gegen `main`, bei Pushes auf `main` sowie manuell über `workflow_dispatch`.

Die CI geht deutlich über `python -m pytest -q` hinaus. Der aktuelle Ablauf prüft nacheinander unter anderem:

1. Repository-Health-Check,
2. vollständige Pytest-Suite,
3. Python-Syntax für `distributions`, `tests` und `tools`,
4. Z_-Quality-Release-Profil,
5. KiCad-Bibliotheksvalidierung,
6. erzeugte Gerätevarianten,
7. Gerätekatalog,
8. erzeugte Symbol- und Footprintreferenzen,
9. Qualitätsbericht,
10. Symbolvorschauen,
11. 3D-Vorschauen,
12. HTML-Referenz,
13. Gerätekatalog-HTML,
14. ProjectOS-Projektvalidator,
15. Erzeugung des Z_Cockpit-HTML.

Für Änderungen an Bibliotheken, Generatoren oder Dokumentationsartefakten reicht ein reiner Pytest-Lauf deshalb nicht als vollständige CI-Parität aus. Vor einem Pull Request sollte mindestens `run_tests.bat` beziehungsweise `run_tests.sh` erfolgreich sein; bei Änderungen an erzeugten Dateien sollten zusätzlich die jeweils betroffenen Generatoren mit ihrer `--check`-Option ausgeführt werden.

Der Workflow selbst ist die verbindliche Quelle für die aktuell tatsächlich ausgeführten CI-Schritte. Wenn diese Anleitung und der Workflow voneinander abweichen, gilt `.github/workflows/complete-test-suite.yml`.
