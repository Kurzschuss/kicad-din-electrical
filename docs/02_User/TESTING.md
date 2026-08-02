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
3. Warte auf die Meldung `Alle Tests waren erfolgreich.`

Für eine ausführliche Ausgabe kann stattdessen `run_tests_verbose.bat` gestartet werden.

`run_all_checks.bat` führt zusätzlich eine Python-Syntaxprüfung aus.

## Einmalige Einrichtung

Öffne im Repositoryordner eine Eingabeaufforderung oder PowerShell.

### Empfohlene virtuelle Umgebung

Eine virtuelle Umgebung hält die Python-Pakete dieses Projekts getrennt von anderen Python-Installationen.

```cmd
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements-dev.txt
```

Der Ordner `.venv` ist optional. Die mitgelieferten Skripte verwenden ihn automatisch, wenn er vorhanden ist. Ohne `.venv` wird die normale Python-Installation verwendet.

### Ohne virtuelle Umgebung

```cmd
python -m pip install -r requirements-dev.txt
```

## Verfügbare Windows-Skripte

### Normale Testsuite

```cmd
run_tests.bat
```

Entspricht im Wesentlichen:

```cmd
python -m pytest -q
```

### Ausführliche Testsuite

```cmd
run_tests_verbose.bat
```

Entspricht:

```cmd
python -m pytest -vv
```

### Alle lokalen Prüfungen

```cmd
run_all_checks.bat
```

Dieses Skript führt nacheinander aus:

1. vollständige Testsuite
2. Python-Syntaxprüfung für `distributions/` und `tests/`

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

## Einzelne Tests ausführen

Nur eine Testdatei:

```bash
python -m pytest tests/test_symbol_matched_footprint_libraries.py
```

Nur einen bestimmten Test:

```bash
python -m pytest tests/test_symbol_matched_footprint_libraries.py::test_every_symbol_library_has_matching_pretty_directory
```

Beim ersten Fehler stoppen:

```bash
python -m pytest -x
```

Nur zuvor fehlgeschlagene Tests erneut ausführen:

```bash
python -m pytest --lf
```

## Häufige Fehler

### `Python wurde nicht gefunden`

Python ist nicht installiert oder nicht im Suchpfad eingetragen. Nach der Installation sollte ein neues Terminal geöffnet werden.

### `No module named pytest`

Installiere die Entwicklungsabhängigkeiten:

```cmd
python -m pip install -r requirements-dev.txt
```

### Die Batchdatei schließt sofort

Starte sie aus einer geöffneten Eingabeaufforderung, damit die Fehlermeldung sichtbar bleibt. Die bereitgestellten Batchdateien verwenden zusätzlich `pause`, damit das Fenster normalerweise geöffnet bleibt.

## GitHub Actions

Die zentrale CI führt ebenfalls die vollständige Testsuite aus:

```bash
python -m pytest -q
```

Ein erfolgreicher lokaler Lauf ist daher ein guter Hinweis darauf, dass auch der Pull-Request-Workflow erfolgreich sein wird.
