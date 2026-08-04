# Diagnose-Workflow

Dieses Dokument beschreibt den aktuellen lokalen Diagnoseablauf des Projekts.

## Ziel

Fehlgeschlagene Prüfungen sollen reproduzierbar dokumentiert werden, ohne Daten ungefragt an GitHub zu übertragen.

## Ablauf

```text
Prüfung starten
    ↓
Konsolenausgabe live anzeigen
    ↓
Ausgabe in Logdatei speichern
    ↓
bei Fehler: FEHLERBERICHT.md erzeugen
    ↓
lokalen Aktionsdialog anzeigen
    ↓
Bericht öffnen / Ordner anzeigen / Issue-Vorschau erzeugen
```

## Zentrale Werkzeuge

```text
tools/run_with_error_report.py
tools/create_error_report.py
tools/create_github_issue_preview.py
tools/windows/run_with_error_report.bat
tools/windows/open_error_report.bat
```

## Erzeugte Dateien

Je nach ausgeführter Prüfung entstehen unter `build/`:

```text
LETZTER_TESTLAUF.log
ALLE_PRUEFUNGEN_PYTEST.log
ALLE_PRUEFUNGEN_SYNTAX.log
ALLE_PRUEFUNGEN_QUALITAET.log
FEHLERBERICHT.md
GITHUB_ISSUE_TITEL.txt
GITHUB_ISSUE_VORSCHAU.md
```

## Fehlerdialog

Nach einer fehlgeschlagenen Prüfung stehen lokal diese Aktionen zur Verfügung:

```text
[1] Fehlerbericht öffnen
[2] Fehlerordner im Explorer öffnen
[3] GitHub-Issue-Vorschau erzeugen und öffnen
[0] Zurück
```

## Datenschutz

Vor der Erzeugung der GitHub-Issue-Vorschau werden derzeit automatisch maskiert:

- Benutzernamen in Windows-Pfaden unter `C:\Users\...`
- Werte typischer Zugangsdaten wie `TOKEN`, `API_KEY`, `SECRET`, `PASSWORD` und `PASSWD`

Die Vorschau muss trotzdem vor einer Veröffentlichung vollständig gelesen und geprüft werden.

## Sicherheitsgrenze

Der aktuelle Workflow:

- erstellt ausschließlich lokale Dateien,
- öffnet kein GitHub-Issue,
- überträgt keine Diagnosedaten ins Internet,
- enthält keinen automatischen Veröffentlichungsbefehl.

Eine spätere Issue-Erstellung muss als eigener, ausdrücklich bestätigter Schritt umgesetzt werden.

## Einbindung in das Testmenü

Die Diagnose ist für Einzelprüfungen und für den kombinierten Lauf „Alle Prüfungen“ aktiv. Beim ersten fehlgeschlagenen Schritt wird der Lauf beendet und ein Bericht für genau diesen Schritt erzeugt.

## Aktueller Status

```text
Automatische Protokollierung        erledigt
Markdown-Fehlerbericht              erledigt
Lokaler Aktionsdialog               erledigt
Datenschutzbereinigte Issue-Vorschau erledigt
Automatische GitHub-Veröffentlichung nicht vorhanden
```

## Nächste mögliche Ausbaustufen

- Fehler-Fingerprint zur Erkennung von Dubletten
- Fehlerhistorie mit eindeutiger Fehler-ID
- Vergleich mit bestehenden GitHub-Issues
- ausdrücklich bestätigte Issue-Erstellung
- Anzeige im Z_Cockpit
