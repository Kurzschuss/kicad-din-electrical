# Z_Cockpit – nächster Ausbau: Benutzer, Whitelist und Fehlermeldungen

Stand: 10. August 2026

Dieses Dokument legt die nächsten drei fachlichen Ausbaustufen nach Abschluss der aktuellen Z_Cockpit-Kernseiten fest. Die Reihenfolge ist verbindlich, solange keine neue Freigabe etwas anderes festlegt:

1. **Benutzerverwaltung**
2. **Whitelist- und Berechtigungsverwaltung**
3. **Issue- und Fehlermeldungsworkflow**

Die Arbeiten bauen auf den bereits vorhandenen ProjectOS-Domänen- und Persistenzbausteinen auf. Es wird keine parallele Benutzer-, Rechte- oder Fehlerdatenbank im Z_Cockpit eingeführt.

## 1. Benutzerverwaltung

### Ziel

Das Z_Cockpit erhält einen eigenen Bereich für die ProjectOS-Benutzerverwaltung. Vorhandene Benutzer-, Rollen-, Rechte- und Lifecycle-Modelle werden sichtbar und später kontrolliert bearbeitbar gemacht.

### Bereits vorhandene technische Grundlage

Im Repository existieren bereits unter anderem:

- `projectos/authorization.py` für Rollen, Whitelist, Blacklist, Ausnahmerechte und nachvollziehbare Autorisierungsentscheidungen;
- `projectos/identity_persistence.py` für persistente Benutzerkonten, Rollen, Rollenrechte, Whitelist, Blacklist und Ausnahmerechte in SQLite;
- `distributions/z_cockpit_authorization.py` für read-only Rechteherkunft und Rechtesimulation;
- `distributions/z_cockpit_user_management_persistence.py` für Persistenz- und Migrationsstatus der Benutzerverwaltung;
- weitere ProjectOS-Bausteine für Benutzer-Lifecycle, Änderungsverfolgung, Undo/Redo, Freigaben und Konsistenzprüfungen.

Diese vorhandenen Bausteine bleiben Single Source of Truth.

### Geplante Cockpit-Funktionen

Die erste Benutzerverwaltungsansicht soll mindestens enthalten:

- Benutzerliste mit technischer Benutzer-ID und Anzeigename;
- Status `aktiv` / `deaktiviert`;
- Rollen und Rollenzuweisungen;
- effektive Rechte;
- Herkunft eines Rechts, zum Beispiel Rolle, direkte Zuweisung, Whitelist, Ausnahme oder DENY;
- Benutzer-Lifecycle einschließlich Deaktivierung und Reaktivierung;
- fester Detailbereich rechts nach dem Bedienmuster von Geräte-, Hersteller- und Diagnoseansicht;
- Filter nach Benutzerstatus, Rolle und Berechtigungszustand;
- nachvollziehbare Änderungs- und Freigabeinformationen, soweit die vorhandenen ProjectOS-Daten diese bereitstellen.

### Schreibende Aktionen

Schreibende Benutzerverwaltungsaktionen dürfen nicht als unabhängige HTML-Logik implementiert werden. Sie müssen über die vorhandenen ProjectOS-Services und deren Autorisierungsregeln laufen.

Für jede schreibende Aktion gelten mindestens:

- Berechtigungsprüfung vor der Änderung;
- keine Umgehung vorhandener Rollen-/DENY-/Freigaberegeln;
- bestehende Persistenz verwenden;
- nachvollziehbare Änderungshistorie;
- Fehler klar anzeigen;
- keine stillen automatischen Rechteerweiterungen.

## 2. Whitelist- und Berechtigungsverwaltung

### Zwei verschiedene Whitelists strikt trennen

Im Projekt gibt es zwei unterschiedliche Konzepte, die in der Oberfläche nicht vermischt werden dürfen.

#### A. ProjectOS-Benutzer-Whitelist

Diese Whitelist ist Teil des ProjectOS-Autorisierungsmodells. Sie erteilt einem Benutzer ausdrücklich einzelne Berechtigungen, wenn diese nicht bereits über eine Rolle erteilt werden und kein vorrangiges DENY entgegensteht.

Dazugehörige Daten liegen im bestehenden Benutzer-/Berechtigungsmodell, unter anderem in `projectos_user_whitelist` der SQLite-Persistenz.

Geplante Oberfläche:

- Benutzer auswählen;
- aktuelle Whitelist-Rechte sehen;
- Blacklist/DENY separat sehen;
- neue Whitelist-Berechtigung kontrolliert hinzufügen;
- vorhandene Whitelist-Berechtigung kontrolliert entfernen;
- effektive Entscheidung vor und nach einer geplanten Änderung simulieren;
- Ausnahmerechte mit Gültigkeitszeitraum separat darstellen;
- Herkunft und Priorität der Entscheidung sichtbar halten.

#### B. Repository-Entwickler-Whitelist

Die Repository-Entwickler-Whitelist ist **nicht** dasselbe wie die ProjectOS-Benutzer-Whitelist.

Ihre aktuelle Quelle ist:

```text
config/authorized_developers.json
```

Sie enthält freigegebene GitHub-Benutzer für repositorybezogene Schutzmechanismen. Die Sicherheitsseite prüft bereits, ob diese Datei vorhanden ist.

Geplante Verwaltungsfunktion:

- aktuell freigegebene GitHub-Benutzer anzeigen;
- Quelle und Schema anzeigen;
- Änderungen nur über einen kontrollierten Repository-Änderungsweg vorbereiten;
- keine lokale Browserliste als zweite Quelle führen;
- Änderungsvorschau vor dem Schreiben;
- Repository-Validator/CI nach Änderung ausführen;
- CODEOWNERS und Ruleset als getrennte Schutzmechanismen darstellen.

### Sicherheitsregel

Blacklist/DENY bleibt vorrangig. Eine Whitelist darf keinen ausdrücklich gesperrten Zugriff unbemerkt überschreiben.

## 3. Issue- und Fehlermeldungsworkflow

### Ziel

Aus dem Z_Cockpit soll ein reproduzierbarer, strukturierter Fehlerbericht erzeugt werden können. Der Benutzer soll nicht manuell technische Zustandsdaten zusammensuchen müssen.

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

## Reihenfolge und Abnahmepunkte

### Phase 1 – Benutzerverwaltung

Abnahme, wenn Benutzer, Status, Rollen und effektive Rechte aus der vorhandenen ProjectOS-Datenquelle nachvollziehbar dargestellt werden und die Architektur für kontrollierte Änderungen festgelegt ist.

### Phase 2 – Whitelist-/Berechtigungsverwaltung

Abnahme, wenn ProjectOS-Whitelist/Blacklist/Ausnahmen und Repository-Entwickler-Whitelist klar getrennt dargestellt und ihre vorgesehenen Änderungswege abgesichert sind.

### Phase 3 – Issue-/Fehlermeldung

Abnahme, wenn ein strukturierter lokaler Fehlerbericht erzeugt werden kann, relevante Diagnosedaten automatisch aufgenommen werden und der Benutzer vor externer Weitergabe die enthaltenen Daten kontrollieren kann.

## Nicht Teil dieser drei Arbeitspakete

Separat offen bleiben weiterhin:

- 3D-Vorschauen;
- direkte KiCad-Editoraufrufe;
- Persistenzanbindung der Laufzeit-Wissensgraphdiagnosen;
- serverseitige Aktivierung des vorbereiteten GitHub-Rulesets.

Der GitHub-Ruleset-Punkt bleibt bis zu einer separaten gemeinsamen Freigabe `blocked`.
