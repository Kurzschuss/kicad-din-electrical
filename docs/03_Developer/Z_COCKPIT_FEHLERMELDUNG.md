# Z_Cockpit – Issue- und Fehlermeldungsworkflow

Stand: 10. August 2026

## Ziel

Der Bereich `Fehler melden` erzeugt einen reproduzierbaren Markdown-Fehlerbericht aus Benutzerangaben und bereits vorhandenen ProjectOS-/Repository-Prüfdaten. Das statische Z_Cockpit sendet niemals selbst ein Issue ab und enthält keine GitHub-Zugangstokens.

Die Berichtsvorschau ist die verbindliche Übergabegrenze: Nur der dort sichtbare Text wird kopiert oder als lokale Markdown-Datei gespeichert.

## Datenquellen

Verwendet werden ausschließlich vorhandene Quellen:

- Projektname, Zielrelease und Projektstatus aus `project_state.yaml`;
- ProjectOS-Version aus `projectos.__version__`;
- Diagnosebefunde aus `tools.z_cockpit.diagnostics_page.collect_diagnostics()`;
- Sicherheitsstatus aus `tools.z_cockpit.security_status.collect_security_status()`;
- optional das Ergebnis der expliziten Repositoryprüfung aus `build/VERSIONSPRUEFUNG.json`.

`build/VERSIONSPRUEFUNG.json` wird durch folgenden vorhandenen Prüfer erzeugt:

```text
python -m tools.check_repository_version
```

Der Windows-Starter `tools/windows/open_z_cockpit.bat` führt diese Prüfung vor der Cockpit-Erzeugung automatisch aus. Ein nicht freigegebener oder nicht prüfbarer Repositoryzustand verhindert nicht den lokalen Bericht, sperrt aber die Schaltfläche `GitHub-Issue vorbereiten`.

## Inhalt des Berichts

Der Benutzer kann erfassen:

- Fehlerkategorie;
- Kurztitel;
- technische Referenz, zum Beispiel Geräte-ID, Symbol, Footprint oder `PRJ-*`-Code;
- Beschreibung;
- Reproduktionsschritte;
- erwartetes Verhalten;
- tatsächliches Verhalten.

Zusätzlich können einzeln abgewählt werden:

- Projekt-/ProjectOS-Version;
- Diagnosezusammenfassung und relevante Prüf-/Analysecodes;
- Repository-Sicherheitsstatus;
- Repositoryprüfergebnis.

Diagnosebefunde werden auf maximal 25 Einträge im eingebetteten Kontext begrenzt. Sind mehr Befunde vorhanden, nennt der Bericht die Zahl der nicht eingebetteten Befunde.

## Datenschutzgrenze

Nicht automatisch in den Fehlerbericht übernommen werden:

- Benutzerkonten oder vollständige Benutzerverwaltungsdaten;
- Rollen-/Berechtigungsbestände;
- authentifizierter GitHub-Benutzer aus der Repositoryprüfung;
- Passwörter;
- Tokens;
- private Schlüssel;
- Zugangsdaten;
- ungeprüfte lokale Dateiinhalte.

Der Benutzer kann die Markdown-Vorschau vor jeder Weitergabe vollständig lesen und bearbeiten. Vor der GitHub-Vorbereitung ist eine ausdrückliche Bestätigung erforderlich, dass sensible oder unnötige Angaben entfernt wurden.

## Repository- und GitHub-Gate

Die GitHub-Vorbereitung ist nur aktiv, wenn alle folgenden Bedingungen erfüllt sind:

1. `tools.check_repository_version` hat einen zulässigen Zustand geliefert (`current=true`);
2. ein Kurztitel ist vorhanden;
3. eine Beschreibung ist vorhanden;
4. die sichtbare Datenschutz-/Inhaltsprüfung wurde bestätigt.

Der Repositoryprüfer erlaubt damit nur die unveränderte aktuelle offizielle Version oder einen bereits über den bestehenden Entwicklermodus freigegebenen Entwicklerzustand. Ein nicht offizielles Repository, ein veralteter Stand, eine nicht freigegebene lokale Änderung oder eine nicht sicher bestimmbare Version bleibt für die Cockpit-GitHub-Vorbereitung gesperrt.

## GitHub-Ablauf

`GitHub-Issue vorbereiten` führt zwei lokale Benutzeraktionen aus:

1. den aktuell sichtbaren Bericht in die Zwischenablage kopieren;
2. das GitHub-Issue-Formular des offiziellen Repositorys in einem neuen Browserfenster öffnen.

Das Issue wird **nicht** automatisch angelegt oder abgesendet. Die abschließende Prüfung und das Absenden erfolgen ausdrücklich im GitHub-Formular durch den Benutzer.

Die dazugehörige Issue Form liegt unter:

```text
.github/ISSUE_TEMPLATE/bug_report.yml
```

Sie enthält dieselben Hauptfelder und verlangt erneut die Bestätigung von Datenschutz/Sicherheit und Repositorystatus.

## Lokaler Ausgabeweg

Der Bericht kann unabhängig von GitHub jederzeit:

- in die Zwischenablage kopiert;
- als `z-cockpit-fehlerbericht.md` lokal gespeichert werden.

Damit bleibt der Fehlerbericht auch offline beziehungsweise bei gesperrter Repositoryprüfung nutzbar.

## Architekturgrenze

Die Seite `tools/z_cockpit/issue_report_page.py` ist read-only gegenüber Repository- und ProjectOS-Daten. Sie schreibt weder Projektdateien noch Benutzer-/Berechtigungszustände.

Die Repositoryprüfung wird nicht innerhalb der Seitenaggregation gestartet. Die Seite liest lediglich ein vorhandenes Prüfergebnis. Dadurch bleiben Netzwerkzugriff, Versionsprüfung und Berichtsdarstellung sauber getrennt und die CI-Erzeugung des Cockpits reproduzierbar.

## Tests

`tests/test_issue_report_page.py` sichert unter anderem ab:

- Registrierung der Seite `fehlerbericht`;
- Vorschau und Datenschutzbestätigung;
- GitHub-Gate anhand des Repositoryprüfergebnisses;
- Ausschluss des authentifizierten GitHub-Benutzers aus dem Berichtskontext;
- Nutzung injizierbarer Projekt-, Diagnose- und Sicherheitsdaten;
- Vorhandensein der GitHub Issue Form und ihrer Datenschutzbestätigung.
