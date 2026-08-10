# Z_Cockpit – Ausbau: Benutzer, Whitelist und Fehlermeldungen

Stand: 10. August 2026

Dieses Dokument legt die drei fachlichen Ausbaustufen nach Abschluss der ursprünglichen Z_Cockpit-Kernseiten fest. Die Reihenfolge bleibt verbindlich, solange keine neue Freigabe etwas anderes festlegt:

1. **Benutzerverwaltung – umgesetzt**
2. **Whitelist- und Berechtigungsverwaltung – umgesetzt**
3. **Issue- und Fehlermeldungsworkflow – als Nächstes geplant**

Die Arbeiten bauen auf den bereits vorhandenen ProjectOS-Domänen- und Persistenzbausteinen auf. Es wird keine parallele Benutzer-, Rechte- oder Fehlerdatenbank im Z_Cockpit eingeführt.

## 1. Benutzerverwaltung – umgesetzt

Das Z_Cockpit besitzt den Bereich `Benutzer`. Er zeigt vorhandene ProjectOS-Benutzer, technische Benutzer-IDs, Lifecycle-Status, Rollen, effektive Rechte und Rechteherkunft read-only an.

Technische Grundlage sind insbesondere:

- `distributions/projectos_user_management_persistence.py`;
- `distributions/projectos_authorization.py`;
- `distributions/projectos_user_lifecycle.py`;
- `distributions/projectos_user_project_roles.py`;
- `distributions/projectos_project_bundle_v4.py`.

Ohne angebundene ProjectOS-Projektdatei werden keine Benutzer erfunden. Für echte Projektdaten kann der Generator mit einem ProjectOS-v4-Bundle aufgerufen werden:

```text
python -m tools.generate_z_cockpit --project-bundle <projektdatei>
```

Details: `docs/03_Developer/Z_COCKPIT_BENUTZERVERWALTUNG.md`.

## 2. Whitelist- und Berechtigungsverwaltung – umgesetzt

### Ergebnis

Das Z_Cockpit besitzt den eigenen Bereich `Berechtigungen`. Er trennt zwei fachlich verschiedene Sicherheitsquellen strikt voneinander:

1. ProjectOS-Benutzerberechtigungen aus `ProjectOSUserManagementState`;
2. Repository-Entwickler-Whitelist aus `config/authorized_developers.json`.

Benutzer- und Berechtigungsseite verwenden bei `--project-bundle` denselben ProjectOS-Datenpfad. Ohne Projektbundle werden keine Beispielberechtigungen erzeugt. Die Repository-Entwickler-Whitelist bleibt als eigenständige Repository-Quelle sichtbar.

### A. ProjectOS-Benutzerberechtigungen

Die Berechtigungsseite wertet die vorhandenen `ProjectOSPermissionAssignment`-Objekte aus. Sichtbar sind:

- Benutzer und technische Benutzer-ID;
- Berechtigung und Zuweisungs-ID;
- Quelle der Zuweisung;
- Wirkung `allow` oder `deny`;
- Scope und Risikoklasse;
- Gültig-ab/Gültig-bis;
- Quellenreferenz;
- Zuweisungsstatus `Aktiv`, `Geplant`, `Abgelaufen` oder `Widerrufen`;
- effektive Autorisierungsentscheidung;
- effektive Rechteherkunft.

Die vorhandenen ProjectOS-Quellen bleiben unverändert:

- Rolle;
- direkte Zuweisung;
- Delegation;
- DENY;
- Ausnahme;
- Whitelist;
- Blacklist.

Die effektive Entscheidung wird nicht im Cockpit neu erfunden, sondern durch den bestehenden `ProjectOSAuthorizationEvaluator` bestimmt.

### Sicherheitsregel

Ein wirksames DENY beziehungsweise eine Blacklist-Zuweisung bleibt vorrangig. Eine Whitelist kann einen ausdrücklich gesperrten Zugriff nicht unbemerkt überschreiben.

### B. Repository-Entwickler-Whitelist

Die Repository-Entwickler-Whitelist bleibt eine getrennte Sicherheitsquelle:

```text
config/authorized_developers.json
```

Die Berechtigungsseite zeigt:

- Vorhandensein;
- Schema-Version;
- Anzahl der freigegebenen GitHub-Benutzer;
- eingetragene Benutzernamen;
- feste Repository-Quelle.

Sie wird nicht in das ProjectOS-Berechtigungsmodell importiert und nicht mit der ProjectOS-Benutzer-Whitelist zusammengeführt.

### Bedienung

Die Seite folgt dem freigegebenen Cockpit-Muster:

- kompakter Seitenkopf mit Erklärung in Klammern;
- Filter und Arbeitsliste links;
- fester Eigenschaftenbereich rechts;
- Freitextsuche;
- Filter nach Benutzer, Quelle, Wirkung und Status;
- technische IDs sichtbar;
- Auswahl per Maus sowie Enter/Leertaste.

### Kontrollierte Änderungswege

Das statische HTML schreibt keine Berechtigungen.

ProjectOS-Änderungen müssen über die vorhandenen, autorisierten Fachservices laufen, insbesondere:

- `ProjectOSUserManagementChangeService.command_assign_permission(...)`;
- `ProjectOSUserManagementChangeService.command_revoke_permission(...)`;
- `ProjectOSUserManagementCommandAuthorization` als fail-closed Autorisierungsprüfung;
- vorhandene Command-/Audit-/Persistenzpfade.

Änderungen an `config/authorized_developers.json` erfolgen als versionierte Repository-Änderung und müssen anschließend Validatoren und CI bestehen. Es wird keine lokale Browser-Whitelist als zweite Quelle geführt.

Damit ist Phase 2 fachlich abgeschlossen. Die Detaildokumentation liegt unter:

```text
docs/03_Developer/Z_COCKPIT_BERECHTIGUNGEN.md
```

## 3. Issue- und Fehlermeldungsworkflow – als Nächstes geplant

### Ziel

Aus dem Z_Cockpit soll ein reproduzierbarer, strukturierter Fehlerbericht erzeugt werden können. Der Benutzer soll technische Zustandsdaten nicht manuell zusammensuchen müssen.

### Geplante Fehlerkategorien

Mindestens:

- allgemeiner Programmfehler;
- Z_Cockpit-Oberfläche;
- Gerätedaten;
- Symbol;
- Footprint;
- Vorschau/3D;
- Projektvalidator/Qualität;
- Benutzer-/Berechtigungsverwaltung;
- Sicherheit;
- Dokumentation.

### Automatisch erfassbare Diagnoseinformationen

Soweit lokal vorhanden und für die Meldung relevant:

- ProjectOS-/Projektversion;
- Z_Cockpit-Version;
- Projektvalidator-Gesamtstatus;
- relevante `PRJ-*`-Prüfcodes;
- Diagnosebefunde;
- Repository-Zustand;
- Versions-/Originalitätsprüfung;
- betroffene technische Geräte-ID;
- Symbol- oder Footprintreferenz;
- aktive Seite/Funktion;
- gegebenenfalls Benutzerverwaltungs- oder Berechtigungsfehlercode.

### Datenschutz- und Sicherheitsgrenze

Vor dem Erzeugen oder Absenden eines Fehlerberichts muss sichtbar sein, welche Informationen enthalten sind.

Nicht automatisch übertragen werden dürfen:

- Passwörter oder Tokens;
- private Schlüssel;
- Zugangsdaten;
- nicht erforderliche personenbezogene Daten;
- ungeprüfte lokale Dateiinhalte;
- vollständige Benutzer-/Rechtedatenbestände, wenn für den Fehler nicht erforderlich.

Sensible oder potenziell personenbezogene Angaben müssen vor einer externen Übertragung überprüfbar und entfernbar sein.

### Ausgabewege

Die Architektur soll mindestens zwei Wege unterstützen:

1. **lokal erzeugbarer Bericht** zum Kopieren/Speichern;
2. **GitHub-Issue-Vorbereitung** mit strukturierter Vorlage.

Eine direkte GitHub-Erstellung darf erst angebunden werden, wenn Authentisierung, Berechtigungsprüfung, Fehlerbehandlung und Nutzerbestätigung sauber definiert sind. Das statische HTML darf keine Zugangstokens enthalten.

### GitHub-Vorlagen

Im Zuge dieses Arbeitspakets sollen passende Issue-Templates beziehungsweise Issue-Forms unter `.github/ISSUE_TEMPLATE/` angelegt werden. Mindestens ein allgemeiner Bug-Report und bei Bedarf spezialisierte Formulare für Bibliotheks-/Gerätefehler sind vorgesehen.

## Einheitliche Z_Cockpit-Bedienlogik

Neue Seiten orientieren sich an den bereits freigegebenen Arbeitsseiten:

- kompakter Seitenkopf;
- Erklärung in Klammern direkt in der Überschriftszeile;
- Filter und Arbeitsliste links;
- fester Detail-/Eigenschaftenbereich rechts, wenn fachlich sinnvoll;
- nur der eigentliche Listenbereich scrollt;
- technische IDs bleiben sichtbar und kopierbar;
- read-only und schreibende Funktionen werden klar getrennt.

## Abnahmestand

### Phase 1 – Benutzerverwaltung: erfüllt

Benutzer, Status, Rollen und effektive Rechte werden aus der vorhandenen ProjectOS-Datenquelle nachvollziehbar dargestellt.

### Phase 2 – Whitelist-/Berechtigungsverwaltung: erfüllt

ProjectOS-Whitelist/Blacklist/Ausnahmen und Repository-Entwickler-Whitelist werden klar getrennt dargestellt. Die bestehenden autorisierten Änderungswege sind dokumentiert und das statische Cockpit führt keine eigene Schreiblogik ein.

### Phase 3 – Issue-/Fehlermeldung: offen

Abnahme, wenn ein strukturierter lokaler Fehlerbericht erzeugt werden kann, relevante Diagnosedaten automatisch aufgenommen werden und der Benutzer vor externer Weitergabe die enthaltenen Daten kontrollieren kann.

## Separat offen

Unabhängig von diesen drei Arbeitspaketen bleiben weiterhin offen:

- 3D-Vorschauen;
- direkte KiCad-Editoraufrufe;
- Persistenzanbindung der Laufzeit-Wissensgraphdiagnosen;
- serverseitige Aktivierung des vorbereiteten GitHub-Rulesets.

Der GitHub-Ruleset-Punkt bleibt bis zu einer separaten gemeinsamen Freigabe `blocked`.
