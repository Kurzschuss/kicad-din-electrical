# Z_Cockpit – Ausbau: Benutzer, Whitelist und Fehlermeldungen

Stand: 10. August 2026

Der nach Abschluss der ursprünglichen Z_Cockpit-Kernseiten festgelegte Ausbau ist vollständig umgesetzt:

1. **Benutzerverwaltung – umgesetzt**
2. **Whitelist- und Berechtigungsverwaltung – umgesetzt**
3. **Issue- und Fehlermeldungsworkflow – umgesetzt**

Alle drei Stufen bauen auf vorhandenen ProjectOS-/Repository-Quellen auf. Es wurde keine parallele Benutzer-, Rechte- oder Fehlerdatenbank im Z_Cockpit eingeführt.

## 1. Benutzerverwaltung – umgesetzt

Der Bereich `Benutzer` zeigt vorhandene ProjectOS-Benutzer, technische Benutzer-IDs, Lifecycle-Status, Rollen, effektive Rechte und Rechteherkunft read-only an.

Technische Grundlage sind insbesondere:

- `distributions/projectos_user_management_persistence.py`;
- `distributions/projectos_authorization.py`;
- `distributions/projectos_user_lifecycle.py`;
- `distributions/projectos_user_project_roles.py`;
- `distributions/projectos_project_bundle_v4.py`.

Ohne angebundene ProjectOS-Projektdatei werden keine Benutzer erfunden. Reale Projektdaten können explizit angebunden werden:

```text
python -m tools.generate_z_cockpit --project-bundle <projektdatei>
```

Details: `docs/03_Developer/Z_COCKPIT_BENUTZERVERWALTUNG.md`.

## 2. Whitelist- und Berechtigungsverwaltung – umgesetzt

Der Bereich `Berechtigungen` trennt zwei fachlich unterschiedliche Sicherheitsquellen:

1. ProjectOS-Benutzerberechtigungen aus `ProjectOSUserManagementState`;
2. Repository-Entwickler-Whitelist aus `config/authorized_developers.json`.

### ProjectOS-Berechtigungen

Sichtbar sind unter anderem:

- Benutzer und technische Benutzer-ID;
- Berechtigung und Zuweisungs-ID;
- Quelle: Rolle, direkte Zuweisung, Delegation, DENY, Ausnahme, Whitelist oder Blacklist;
- Wirkung `allow` / `deny`;
- Scope und Risikoklasse;
- Gültigkeitszeitraum;
- Widerrufsstatus;
- effektive Autorisierungsentscheidung und Rechteherkunft.

Die effektive Entscheidung wird durch den bestehenden `ProjectOSAuthorizationEvaluator` bestimmt. Ein wirksames DENY beziehungsweise eine Blacklist-Zuweisung bleibt vorrangig.

### Repository-Entwickler-Whitelist

Die Repository-Entwickler-Whitelist bleibt eine getrennte, versionierte Quelle:

```text
config/authorized_developers.json
```

Sie wird nicht in das ProjectOS-Berechtigungsmodell importiert und nicht als Browserkopie gepflegt.

### Schreibgrenze

Das statische HTML schreibt keine Berechtigungen. ProjectOS-Änderungen müssen über die vorhandenen autorisierten Fachservices laufen, insbesondere `ProjectOSUserManagementChangeService` und die fail-closed `ProjectOSUserManagementCommandAuthorization`. Änderungen der Repository-Entwickler-Whitelist erfolgen als normale versionierte Repository-Änderung mit anschließender Validator-/CI-Prüfung.

Details: `docs/03_Developer/Z_COCKPIT_BERECHTIGUNGEN.md`.

## 3. Issue- und Fehlermeldungsworkflow – umgesetzt

### Ziel und Ergebnis

Der Bereich `Fehler melden` erzeugt einen reproduzierbaren Markdown-Fehlerbericht. Benutzerangaben werden mit bereits vorhandenen technischen Prüfständen kombiniert, ohne sensible Benutzer- oder Zugangsdaten automatisch zu übernehmen.

### Fehlerkategorien

Umgesetzt sind:

- allgemeiner Programmfehler;
- Z_Cockpit-Oberfläche;
- Gerätedaten;
- Symbol;
- Footprint;
- Vorschau / 3D;
- Projektvalidator / Qualität;
- Benutzer / Berechtigungen;
- Sicherheit;
- Dokumentation.

### Berichtsdaten

Der Benutzer erfasst:

- Kurztitel;
- Kategorie;
- optionale technische Referenz;
- Beschreibung;
- Reproduktionsschritte;
- erwartetes Verhalten;
- tatsächliches Verhalten.

Optional und einzeln abwählbar werden ergänzt:

- Projektname, Zielrelease, ProjectOS- und Z_Cockpit-Version;
- Diagnosezusammenfassung und relevante `PRJ-*`-/Analysebefunde;
- Repository-Sicherheitsstatus;
- Ergebnis der expliziten Repositoryprüfung.

Die Diagnoseeinbettung ist auf 25 Befunde begrenzt; weitere Befunde werden nur als Anzahl genannt.

### Repositoryprüfung

Für die GitHub-Vorbereitung wird der vorhandene Prüfer verwendet:

```text
python -m tools.check_repository_version
```

Das Ergebnis liegt unter:

```text
build/VERSIONSPRUEFUNG.json
```

Die Fehlerbericht-Seite liest diese Datei nur. Sie startet selbst keinen Netzwerkzugriff. Der Windows-Starter `tools/windows/open_z_cockpit.bat` führt die Repositoryprüfung vor der Cockpit-Erzeugung automatisch aus.

Die GitHub-Vorbereitung bleibt gesperrt, wenn die Repositoryprüfung keinen zulässigen Zustand bestätigt. Der lokale Bericht bleibt davon unabhängig verfügbar.

### Datenschutz- und Sicherheitsgrenze

Nicht automatisch übernommen werden:

- Benutzerkonten oder vollständige Benutzerverwaltungsdaten;
- Rollen-/Berechtigungsbestände;
- authentifizierter GitHub-Benutzer aus der Repositoryprüfung;
- Passwörter;
- Tokens;
- private Schlüssel;
- Zugangsdaten;
- ungeprüfte lokale Dateiinhalte.

Die sichtbare Markdown-Vorschau ist die verbindliche Übergabegrenze. Vor der GitHub-Vorbereitung muss der Benutzer ausdrücklich bestätigen, dass der Bericht geprüft und sensible oder unnötige Angaben entfernt wurden.

### Ausgabewege

Umgesetzt sind zwei Wege:

1. **lokaler Bericht** – kopierbar und als `z-cockpit-fehlerbericht.md` speicherbar;
2. **GitHub-Issue-Vorbereitung** – Bericht kopieren und offizielles GitHub-Issue-Formular öffnen.

Das Z_Cockpit legt kein GitHub-Issue automatisch an und sendet nichts automatisch ab.

### GitHub Issue Form

Die strukturierte Vorlage liegt unter:

```text
.github/ISSUE_TEMPLATE/bug_report.yml
```

Sie enthält dieselben Hauptfelder sowie verpflichtende Datenschutz-/Sicherheitsbestätigungen.

Technische Detaildokumentation:

```text
docs/03_Developer/Z_COCKPIT_FEHLERMELDUNG.md
```

## Einheitliche Z_Cockpit-Bedienlogik

Alle drei Ausbaupunkte folgen dem bestehenden Cockpit-Muster:

- kompakter Seitenkopf;
- Erklärung in Klammern direkt in der Überschriftszeile;
- Arbeitsbereich links und fester Detail-/Vorschaubereich rechts, wenn fachlich sinnvoll;
- nur fachlich notwendige Bereiche scrollen;
- technische IDs bleiben sichtbar;
- read-only Datenaggregation und schreibende Aktionen bleiben klar getrennt.

## Abnahmestand

### Phase 1 – Benutzerverwaltung: erfüllt

Benutzer, Status, Rollen und effektive Rechte werden aus der vorhandenen ProjectOS-Datenquelle nachvollziehbar dargestellt.

### Phase 2 – Whitelist-/Berechtigungsverwaltung: erfüllt

ProjectOS-Whitelist/Blacklist/Ausnahmen und Repository-Entwickler-Whitelist werden klar getrennt dargestellt. Bestehende autorisierte Änderungswege bleiben verbindlich.

### Phase 3 – Issue-/Fehlermeldung: erfüllt

Ein strukturierter lokaler Fehlerbericht kann erzeugt werden, relevante Diagnosedaten können automatisch aufgenommen werden und der Benutzer kontrolliert die endgültige Berichtsvorschau vor jeder externen Weitergabe.

## Zentraler Projektstatus

Die Aufgaben `benutzerverwaltung`, `whitelist_verwaltung` und `issue_fehlermeldung` stehen in `project_state.yaml` auf `done`.

Damit ist aktuell keine normale `planned`- oder `in_progress`-Aufgabe im zentralen Projektmodell vorhanden.

## Separat offen

Unabhängig vom abgeschlossenen Dreierpaket bleiben weiterhin offen:

- 3D-Vorschauen;
- direkte KiCad-Editoraufrufe;
- Persistenzanbindung der Laufzeit-Wissensgraphdiagnosen;
- serverseitige Aktivierung des vorbereiteten GitHub-Rulesets.

Der GitHub-Ruleset-Punkt bleibt bis zu einer separaten gemeinsamen Freigabe `blocked`.
