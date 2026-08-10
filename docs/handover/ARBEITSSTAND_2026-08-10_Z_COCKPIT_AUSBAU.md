# Arbeitsstand 2026-08-10 – Z_Cockpit Layout und Ausbau

## Visuell festgelegter Stand

Die obere Darstellung der Z_Cockpit-Seiten wird am Bibliotheksbereich ausgerichtet.

Verbindliches Muster:

```text
Menü-/Seitentitel (kurze Erklärung zum Bereich)
```

Die Erklärung steht in kleinerer, zurückhaltender Schrift direkt in derselben Überschriftszeile. Eine zusätzliche zweite Erklärungszeile unmittelbar unter dem Seitentitel soll vermieden werden.

`Einstellungen`, `Sicherheit`, `Benutzer` und `Berechtigungen` verwenden dieses Muster direkt. Start, Qualität, Hersteller, Diagnose und Dokumentation werden im erzeugten Cockpit ebenfalls auf dieses gemeinsame Kopfzeilenmuster normalisiert.

`Geräte` und `Bibliotheken` werden strukturell nicht umgebaut. Die bereits freigegebene Bibliotheksansicht bleibt Referenz für die kompakte Kopfgestaltung.

## Nicht verändern

Ohne neue ausdrückliche Anforderung bleiben unverändert:

- freigegebene MCB-Geometrie;
- freigegebene RCD/FI-Geometrien 2P und 3+N/4P;
- Bibliotheksarbeitslogik;
- rechter Eigenschaften-/Vorschaubereich;
- separates Scrollverhalten der Geräte-ID-Listen.

## Ausbaureihenfolge und aktueller Stand

Die festgelegte Reihenfolge lautet:

1. **Benutzerverwaltung – umgesetzt**
2. **Whitelist- und Berechtigungsverwaltung – umgesetzt**
3. **Issue- und Fehlermeldungsworkflow – als Nächstes**

Die vollständige fachliche Planung steht in:

```text
docs/projectos/Z_COCKPIT_AUSBAU_BENUTZER_WHITELIST_ISSUES.md
```

## Benutzerverwaltung – umgesetzt

Die vorhandenen ProjectOS-Bausteine für Benutzer, Rollen, Berechtigungen, Benutzer-Lifecycle und Rechteherkunft sind in eine eigene Z_Cockpit-Seite integriert. Es wurde keine zweite Benutzerdatenbank aufgebaut.

Umgesetzt sind unter anderem Benutzerliste, technische ID, Aktiv/Deaktiviert, Rollen, effektive Rechte, Rechteherkunft, Filter, fester Detailbereich und Lifecycle-Historie.

Ohne ProjectOS-Projektdatei werden keine Benutzer erfunden. Für reale Projektdaten kann ein vorhandenes v4-Bundle explizit angebunden werden:

```text
python -m tools.generate_z_cockpit --project-bundle <projektdatei>
```

Detaildokumentation:

```text
docs/03_Developer/Z_COCKPIT_BENUTZERVERWALTUNG.md
```

## Whitelist- und Berechtigungsverwaltung – umgesetzt

Es gibt jetzt einen eigenen Navigationspunkt `Berechtigungen`.

### ProjectOS-Berechtigungen

Die Seite zeigt vorhandene `ProjectOSPermissionAssignment`-Daten mit:

- Benutzer und technischer Benutzer-ID;
- Berechtigung und Zuweisungs-ID;
- Quelle: Rolle, direkt, Delegation, DENY, Ausnahme, Whitelist oder Blacklist;
- Wirkung `allow` / `deny`;
- Scope und Risikoklasse;
- Gültigkeitszeitraum;
- Widerrufsstatus;
- effektiver Autorisierungsentscheidung und Rechteherkunft.

Ein wirksames DENY/Blacklist bleibt vorrangig. Die effektive Entscheidung kommt aus dem bestehenden `ProjectOSAuthorizationEvaluator`.

### Repository-Entwickler-Whitelist

Die Repository-Entwickler-Whitelist bleibt strikt getrennt und wird direkt aus folgender Quelle angezeigt:

```text
config/authorized_developers.json
```

Angezeigt werden Schema, Einträge und GitHub-Benutzernamen. Diese Liste wird weder in ProjectOS importiert noch als Browserkopie gepflegt.

### Schreibgrenze

Das statische Cockpit schreibt keine Rechte. ProjectOS-Änderungen müssen über `ProjectOSUserManagementChangeService` und die fail-closed `ProjectOSUserManagementCommandAuthorization` laufen. Repository-Whitelist-Änderungen erfolgen als versionierte Repository-Änderung mit anschließender Validator-/CI-Prüfung.

Detaildokumentation:

```text
docs/03_Developer/Z_COCKPIT_BERECHTIGUNGEN.md
```

## Issue-/Fehlermeldung – nächster Schritt

Als nächstes wird ein strukturierter Workflow für Fehlerberichte aus dem Z_Cockpit umgesetzt. Relevante Diagnose- und Versionsdaten sollen automatisch vorbereitet werden, aber vor einer externen Weitergabe sichtbar und kontrollierbar bleiben.

Mindestens vorgesehen:

- Fehlerkategorie;
- Beschreibung und Reproduktionsschritte;
- relevante `PRJ-*`-/Diagnosecodes;
- Projekt-/Cockpit-Version;
- Repository-Zustand;
- betroffene Geräte-/Symbol-/Footprintreferenzen;
- lokaler Bericht;
- GitHub-Issue-Vorbereitung;
- passende `.github/ISSUE_TEMPLATE/`-Vorlagen.

Keine Zugangstokens, Schlüssel oder unnötigen personenbezogenen Daten dürfen automatisch in einen Bericht gelangen.

## Separat offen

Unabhängig von dieser Reihenfolge bleiben offen:

- 3D-Vorschauen;
- direkte KiCad-Editoraufrufe;
- Persistenzanbindung der Laufzeitdiagnosen;
- GitHub-Ruleset-Aktivierung (`blocked`, separate Freigabe erforderlich).
