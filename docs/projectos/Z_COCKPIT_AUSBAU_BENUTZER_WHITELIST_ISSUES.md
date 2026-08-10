# Z_Cockpit – Ausbau: Benutzer, Whitelist und Fehlermeldungen

Stand: 10. August 2026

Dieses Dokument legt die drei fachlichen Ausbaustufen nach Abschluss der ursprünglichen Z_Cockpit-Kernseiten fest. Die Reihenfolge bleibt verbindlich, solange keine neue Freigabe etwas anderes festlegt:

1. **Benutzerverwaltung – umgesetzt**
2. **Whitelist- und Berechtigungsverwaltung – als Nächstes geplant**
3. **Issue- und Fehlermeldungsworkflow – danach geplant**

Die Arbeiten bauen auf den bereits vorhandenen ProjectOS-Domänen- und Persistenzbausteinen auf. Es wird keine parallele Benutzer-, Rechte- oder Fehlerdatenbank im Z_Cockpit eingeführt.

## 1. Benutzerverwaltung – umgesetzt

### Ziel und Ergebnis

Das Z_Cockpit besitzt einen eigenen Bereich für die ProjectOS-Benutzerverwaltung. Vorhandene Benutzer-, Rollen-, Rechte- und Lifecycle-Modelle werden read-only sichtbar und nachvollziehbar ausgewertet. Schreibende Funktionen bleiben bewusst einer späteren, autorisierten Service-Anbindung vorbehalten.

### Technische Grundlage

Verwendet werden die bereits vorhandenen ProjectOS-Bausteine, insbesondere:

- `distributions/projectos_user_management_persistence.py` als fachlicher Persistenzvertrag;
- `distributions/projectos_authorization.py` für Berechtigungsentscheidungen und Rechteherkunft;
- `distributions/projectos_user_lifecycle.py` für Deaktivierung und Reaktivierung;
- `distributions/projectos_user_project_roles.py` für aktive Projektrollen;
- `distributions/projectos_project_bundle_v4.py` zum expliziten Laden vorhandener ProjectOS-Projektbundles;
- vorhandene Change-/Command-/Audit-Bausteine als verbindliche Grundlage für spätere schreibende Aktionen.

Diese vorhandenen Bausteine bleiben Single Source of Truth.

### Umgesetzte Cockpit-Funktionen

Die Benutzerverwaltungsansicht enthält:

- Benutzerliste mit technischer Benutzer-ID und Anzeigename;
- Status `Aktiv` / `Deaktiviert` aus dem vorhandenen Lifecycle-Evaluator;
- Profilrollen und aktive ProjectOS-Projektrollen;
- effektive Rechte auf Basis des vorhandenen Autorisierungs-Evaluators;
- Herkunft eines wirksamen Rechts, zum Beispiel Rolle, direkte Zuweisung, Delegation, Whitelist, Ausnahme oder DENY;
- Benutzer-Lifecycle einschließlich vorhandener Deaktivierungs-/Reaktivierungsereignisse;
- festen Detailbereich rechts nach dem Bedienmuster der anderen Cockpit-Arbeitsseiten;
- Filter nach Name/ID, Benutzerstatus, Rolle und Berechtigungszustand;
- klare read-only Kennzeichnung.

Ohne angebundene ProjectOS-Projektdatei werden keine Benutzer erfunden. Der statische Standardlauf zeigt einen expliziten Leerzustand.

Für echte Projektdaten kann der Generator mit einem ProjectOS-v4-Bundle aufgerufen werden:

```text
python -m tools.generate_z_cockpit --project-bundle <projektdatei>
```

Die technische Detaildokumentation liegt unter:

```text
docs/03_Developer/Z_COCKPIT_BENUTZERVERWALTUNG.md
```

### Schreibende Aktionen

Schreibende Benutzerverwaltungsaktionen dürfen nicht als unabhängige HTML-Logik implementiert werden. Sie müssen über die vorhandenen ProjectOS-Services und deren Autorisierungsregeln laufen.

Für jede spätere schreibende Aktion gelten mindestens:

- Berechtigungsprüfung vor der Änderung;
- keine Umgehung vorhandener Rollen-/DENY-/Freigaberegeln;
- bestehende Persistenz verwenden;
- nachvollziehbare Änderungshistorie;
- Fehler klar anzeigen;
- keine stillen automatischen Rechteerweiterungen.

Damit ist Phase 1 fachlich abgeschlossen; die schreibende Rechtepflege gehört zur folgenden Phase 2.

## 2. Whitelist- und Berechtigungsverwaltung – als Nächstes geplant

### Zwei verschiedene Whitelists strikt trennen

Im Projekt gibt es zwei unterschiedliche Konzepte, die in der Oberfläche nicht vermischt werden dürfen.

#### A. ProjectOS-Benutzer-Whitelist

Diese Whitelist ist Teil des ProjectOS-Autorisierungsmodells. Sie erteilt einem Benutzer ausdrücklich einzelne Berechtigungen, wenn diese nicht bereits über eine Rolle erteilt werden und kein vorrangiges DENY entgegensteht.

Dazugehörige Daten liegen im bestehenden Benutzer-/Berechtigungsmodell, unter anderem in `projectos_user_whitelist` der SQLite-Persistenz beziehungsweise in den neueren ProjectOS-Berechtigungszuweisungen mit `source_type="whitelist"`.

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

## 3. Issue- und Fehlermeldungsworkflow – danach geplant

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

### Phase 1 – Benutzerverwaltung: erfüllt

Abnahmebedingung war, Benutzer, Status, Rollen und effektive Rechte aus der vorhandenen ProjectOS-Datenquelle nachvollziehbar darzustellen und die Architektur für kontrollierte Änderungen festzulegen. Dies ist mit der neuen Benutzerseite, dem optionalen ProjectOS-v4-Bundle-Lader und der read-only Servicegrenze erfüllt.

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
