# Arbeitsstand 2026-08-10 – Z_Cockpit Layout und Ausbau

## Visuell festgelegter Stand

Die obere Darstellung der Z_Cockpit-Seiten wird am Bibliotheksbereich ausgerichtet.

Verbindliches Muster:

```text
Menü-/Seitentitel (kurze Erklärung zum Bereich)
```

Die Erklärung steht in kleinerer, zurückhaltender Schrift direkt in derselben Überschriftszeile. Eine zusätzliche zweite Erklärungszeile unmittelbar unter dem Seitentitel soll vermieden werden.

`Einstellungen`, `Sicherheit`, `Benutzer`, `Berechtigungen` und `Fehler melden` verwenden dieses Muster direkt. Start, Qualität, Hersteller, Diagnose und Dokumentation werden im erzeugten Cockpit ebenfalls auf dieses gemeinsame Kopfzeilenmuster normalisiert.

`Geräte` und `Bibliotheken` werden strukturell nicht umgebaut. Die bereits freigegebene Bibliotheksansicht bleibt Referenz für die kompakte Kopfgestaltung.

## Nicht verändern

Ohne neue ausdrückliche Anforderung bleiben unverändert:

- freigegebene MCB-Geometrie;
- freigegebene RCD/FI-Geometrien 2P und 3+N/4P;
- Bibliotheksarbeitslogik;
- rechter Eigenschaften-/Vorschaubereich;
- separates Scrollverhalten der Geräte-ID-Listen.

## Dreistufiger Z_Cockpit-Ausbau – abgeschlossen

Die festgelegte Reihenfolge ist vollständig umgesetzt:

1. **Benutzerverwaltung – umgesetzt**
2. **Whitelist- und Berechtigungsverwaltung – umgesetzt**
3. **Issue- und Fehlermeldungsworkflow – umgesetzt**

Die fachliche Gesamtdokumentation steht in:

```text
docs/projectos/Z_COCKPIT_AUSBAU_BENUTZER_WHITELIST_ISSUES.md
```

## Benutzerverwaltung

Die vorhandenen ProjectOS-Bausteine für Benutzer, Rollen, Berechtigungen, Benutzer-Lifecycle und Rechteherkunft sind in eine eigene Z_Cockpit-Seite integriert. Ohne ProjectOS-Projektdatei werden keine Benutzer erfunden. Für reale Projektdaten kann ein vorhandenes v4-Bundle explizit angebunden werden:

```text
python -m tools.generate_z_cockpit --project-bundle <projektdatei>
```

Detaildokumentation:

```text
docs/03_Developer/Z_COCKPIT_BENUTZERVERWALTUNG.md
```

## Whitelist- und Berechtigungsverwaltung

Der Navigationspunkt `Berechtigungen` zeigt ProjectOS-Berechtigungszuweisungen inklusive Quelle, Wirkung, Scope, Risikoklasse, Gültigkeit, Widerrufsstatus und effektiver Entscheidung. DENY/Blacklist bleibt vorrangig und wird über den vorhandenen `ProjectOSAuthorizationEvaluator` ausgewertet.

Die Repository-Entwickler-Whitelist aus `config/authorized_developers.json` bleibt davon strikt getrennt. Das statische Cockpit schreibt keine Rechte oder Entwicklerfreigaben.

Detaildokumentation:

```text
docs/03_Developer/Z_COCKPIT_BERECHTIGUNGEN.md
```

## Issue- und Fehlermeldungsworkflow

Der Navigationspunkt `Fehler melden` erzeugt einen strukturierten lokalen Markdown-Bericht mit:

- Fehlerkategorie;
- Kurztitel und technischer Referenz;
- Beschreibung und Reproduktionsschritten;
- erwartetem und tatsächlichem Verhalten;
- optionaler Projekt-/ProjectOS-Version;
- optionaler Diagnosezusammenfassung mit `PRJ-*`-/Analysebefunden;
- optionalem Sicherheitsstatus;
- optionalem Ergebnis der Repositoryprüfung.

Die sichtbare Berichtsvorschau ist die Übergabegrenze. Benutzer-/Berechtigungsbestände, authentifizierter GitHub-Benutzer, Tokens, Passwörter, Schlüssel und ungeprüfte Dateiinhalte werden nicht automatisch in den Bericht übernommen.

Der lokale Bericht kann kopiert oder als Markdown-Datei gespeichert werden. Die GitHub-Vorbereitung wird nur freigegeben, wenn `tools.check_repository_version` einen zulässigen Repositoryzustand bestätigt, Kurztitel und Beschreibung vorhanden sind und der Benutzer die Vorschau ausdrücklich geprüft hat.

`GitHub-Issue vorbereiten` kopiert den Bericht und öffnet das offizielle GitHub-Issue-Formular; das Issue wird nicht automatisch abgesendet.

Der Windows-Starter führt die Repositoryprüfung vor dem Erzeugen des Cockpits automatisch aus. Ein gesperrter Prüfzustand blockiert nur die GitHub-Vorbereitung, nicht den lokalen Bericht.

Technische Dateien:

```text
tools/z_cockpit/issue_report_page.py
.github/ISSUE_TEMPLATE/bug_report.yml
docs/03_Developer/Z_COCKPIT_FEHLERMELDUNG.md
```

## Projektmodell

`benutzerverwaltung`, `whitelist_verwaltung` und `issue_fehlermeldung` stehen in `project_state.yaml` auf `done`.

Damit ist aktuell keine normale `planned`- oder `in_progress`-Aufgabe im zentralen Projektmodell offen. Der Entwicklungsnavigator zeigt entsprechend `Keine ausführbare Aufgabe offen.`

## Separat offen

Unabhängig von diesem abgeschlossenen Dreierpaket bleiben weiterhin separat offen:

- 3D-Vorschauen;
- direkte KiCad-Editoraufrufe;
- Persistenzanbindung der Laufzeitdiagnosen;
- GitHub-Ruleset-Aktivierung (`blocked`, separate gemeinsame Freigabe erforderlich).
