# Z_Cockpit erzeugen und testen

`Z_Cockpit` ist die zentrale, tabellenbasierte Projekt-, Bibliotheks- und Geräteübersicht der KiCad DIN Electrical Suite.

## Erzeugen

```text
python -m tools.generate_z_cockpit
```

Ausgabe:

```text
docs/site/z-cockpit.html
```

Die HTML-Datei ist ein lokal erzeugtes Arbeitsartefakt und wird nicht als zweite Datenquelle gepflegt.

Für echte ProjectOS-Benutzer- und Berechtigungsdaten kann ein ProjectOS-v4-Projektbundle angebunden werden:

```text
python -m tools.generate_z_cockpit --project-bundle <projektdatei>
```

Ohne Projektbundle werden weder Benutzer noch ProjectOS-Berechtigungen erfunden. Repositorydaten wie die Entwickler-Whitelist bleiben trotzdem sichtbar.

## Unter Windows öffnen

```text
tools\windows\open_z_cockpit.bat
```

Alternativ:

```powershell
.\.venv\Scripts\python.exe -m tools.generate_z_cockpit
```

## Zentrale Seitenregistrierung

Die Navigation wird aus `tools/z_cockpit/pages.py` erzeugt. Aktuell umgesetzt sind:

- Start;
- Geräte;
- Bibliotheken;
- Hersteller;
- Qualität;
- Diagnose;
- Benutzer;
- Berechtigungen;
- Sicherheit;
- Dokumentation;
- Einstellungen.

Neue Bereiche werden dort registriert und nicht als unabhängige Nebenoberflächen aufgebaut.

## Einheitliche Seitenköpfe

Visuelle Referenz ist die Bibliotheksansicht.

Verbindliches Muster:

```text
Seitentitel (kurze Erklärung zum Menüpunkt)
```

Die Erklärung steht kleiner in derselben Zeile. Eine zusätzliche Erklärungszeile direkt unter dem Titel wird vermieden. Filter-/Arbeitslisten stehen links beziehungsweise im Hauptbereich; ein fester Eigenschaftenbereich rechts wird verwendet, wenn er fachlich sinnvoll ist.

## Datenquellen

Das Cockpit führt keine zweite fachliche Datenhaltung ein.

Wichtige Quellen sind:

- Gerätekatalog unter `data/devices/`;
- KiCad-Symbol- und Footprintbibliotheken;
- `project_state.yaml`;
- ProjectOS-Projektvalidator und Projektanalyse;
- vorhandene Markdown-Dokumentation;
- optional `ProjectOSUserManagementState` aus einem ProjectOS-v4-Projektbundle;
- Repository-Entwickler-Whitelist unter `config/authorized_developers.json`.

## Geräte

Die Geräteansicht bietet Filter für Gerätefamilie, Hersteller, Polzahl, Charakteristik, Nennstrom und Status. Technische Geräte-ID, Symbol, Footprint und Vorschauen bleiben sichtbar.

## Bibliotheken

Die Bibliotheksansicht ist tabellenbasiert. Bibliotheksdetails werden direkt unter der ausgewählten Bibliothek geöffnet. Rechts bleibt der Symbolinspektor fest stehen; nur lange Geräte-ID-Listen scrollen separat.

## Hersteller

Die Herstellerseite aggregiert Hersteller, Serien, Gerätefamilien, Quellenstatus und technische Geräte-IDs read-only aus dem Gerätekatalog. `Generic` wird in der Oberfläche als `Herstellerneutral` dargestellt.

## Qualität

Die Qualitätsseite verbindet:

- ProjectOS-Projektkonsistenz aus `tools.project_validator`;
- Bibliotheksgesundheit aus der Quality Engine.

Der Projektvalidator liefert die stabilen Prüfungen `PRJ-001` bis `PRJ-010`.

## Diagnose

Die Diagnoseansicht bündelt repositoryweite Befunde aus Projektvalidator und Projektanalyse. Fehler und Warnungen können gefiltert werden; der rechte Bereich zeigt Prüfcode, Referenz, Details und vorhandene Reparaturempfehlung.

## Benutzer

Die Benutzerseite ist eine read-only Sicht auf den bestehenden `ProjectOSUserManagementState`.

Angezeigt werden:

- Benutzername und technische `user_id`;
- Lifecycle-Status `Aktiv` / `Deaktiviert`;
- Profil- und Projektrollen;
- effektive Rechte;
- Rechteherkunft;
- Risikoklassen und Widerrufe;
- Lifecycle-Ereignisse.

Technische Details:

```text
docs/03_Developer/Z_COCKPIT_BENUTZERVERWALTUNG.md
```

## Berechtigungen

Die Berechtigungsseite trennt zwei Sicherheitsquellen strikt:

### ProjectOS-Benutzerberechtigungen

Aus `ProjectOSUserManagementState` werden die vorhandenen Rechtezuweisungen mit folgenden Quellen ausgewertet:

- Rolle;
- direkte Zuweisung;
- Delegation;
- DENY;
- Ausnahme;
- Whitelist;
- Blacklist.

Sichtbar sind Benutzer, Berechtigung, Zuweisungs-ID, Quelle, Wirkung, Scope, Risikoklasse, Gültigkeit, Widerrufsstatus sowie die effektive Autorisierungsentscheidung.

Die effektive Entscheidung wird durch den bestehenden `ProjectOSAuthorizationEvaluator` bestimmt. Ein wirksames DENY/Blacklist bleibt vorrangig.

### Repository-Entwickler-Whitelist

Die getrennte Repositoryquelle bleibt:

```text
config/authorized_developers.json
```

Das Cockpit zeigt Schema, Anzahl und GitHub-Benutzernamen, importiert diese Liste aber nicht in ProjectOS.

### Schreibgrenze

Das statische Cockpit schreibt keine Berechtigungen. ProjectOS-Änderungen müssen über `ProjectOSUserManagementChangeService` und die fail-closed `ProjectOSUserManagementCommandAuthorization` laufen. Repository-Whitelist-Änderungen erfolgen als versionierte Repository-Änderung mit anschließender Validator-/CI-Prüfung.

Technische Details:

```text
docs/03_Developer/Z_COCKPIT_BERECHTIGUNGEN.md
```

## Sicherheit

Die Sicherheitsseite zeigt Repository-, Versions-, Originalitäts-, Entwickler-Whitelist-, CODEOWNERS- und Ruleset-Status. Ein vorhandener Ruleset-Entwurf bedeutet weiterhin nicht, dass der serverseitige Ruleset aktiviert ist.

## Dokumentation

Der Dokumentationsbrowser indexiert vorhandene Markdown-Dateien aus dem Repository. Die Markdown-Dateien selbst bleiben Single Source of Truth.

## Einstellungen

Projektwerte werden read-only aus Repositoryquellen angezeigt. Lokale Oberflächenoptionen wie Theme, Tabellendichte und letzte Seite werden ausschließlich im Browser unter `z-cockpit.settings.v1` gespeichert.

## Prüfung

Die Tests prüfen unter anderem:

- zentrale Seitenregistrierung und eindeutige Seiten-IDs;
- Gerätekatalog- und Bibliotheksintegration;
- Herstelleraggregation;
- Projektvalidator/Qualität;
- Diagnoseansicht;
- Benutzeraggregation, Rollen, Lifecycle und effektive Rechte;
- ProjectOS-Whitelist/Blacklist/Ausnahmen und Widerrufe;
- getrennte Repository-Entwickler-Whitelist;
- HTML-Escaping;
- Dokumentationsbrowser;
- lokale Einstellungen;
- einheitliche Seitenköpfe;
- Entwicklungsnavigator und Projektstatus.

GitHub Actions erzeugt das Cockpit bei der vollständigen ProjectOS-Prüfkette und führt zusätzlich den Projektvalidator aus.

## Aktueller Entwicklungsstand

Benutzerverwaltung sowie Whitelist-/Berechtigungsverwaltung sind umgesetzt. Im zentralen Projektmodell ist als nächster Z_Cockpit-Ausbau geplant:

```text
Issue- und Fehlermeldungsworkflow integrieren
```

Die fachliche Reihenfolge und Datenschutz-/Sicherheitsanforderungen dafür sind dokumentiert unter:

```text
docs/projectos/Z_COCKPIT_AUSBAU_BENUTZER_WHITELIST_ISSUES.md
```

Separat offen bleiben weiterhin:

- 3D-Vorschauen;
- direkte KiCad-Editoraufrufe;
- Persistenzanbindung der Laufzeit-Wissensgraphdiagnosen;
- serverseitige GitHub-Ruleset-Aktivierung nach separater Freigabe.
