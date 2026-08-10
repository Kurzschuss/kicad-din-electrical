# Arbeitsstand 2026-08-10 – Z_Cockpit Layout und Ausbau

## Visuell festgelegter Stand

Die obere Darstellung der Z_Cockpit-Seiten wird am Bibliotheksbereich ausgerichtet.

Verbindliches Muster:

```text
Menü-/Seitentitel (kurze Erklärung zum Bereich)
```

Die Erklärung steht in kleinerer, zurückhaltender Schrift direkt in derselben Überschriftszeile. Eine zusätzliche zweite Erklärungszeile unmittelbar unter dem Seitentitel soll vermieden werden.

`Einstellungen`, `Sicherheit` und die neue `Benutzerverwaltung` verwenden dieses Muster direkt. Start, Qualität, Hersteller, Diagnose und Dokumentation werden im erzeugten Cockpit ebenfalls auf dieses gemeinsame Kopfzeilenmuster normalisiert.

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
2. **Whitelist- und Berechtigungsverwaltung – als Nächstes**
3. **Issue- und Fehlermeldungsworkflow – danach**

Die vollständige fachliche Planung steht in:

```text
docs/projectos/Z_COCKPIT_AUSBAU_BENUTZER_WHITELIST_ISSUES.md
```

## Benutzerverwaltung – umgesetzt

Die vorhandenen ProjectOS-Bausteine für Benutzer, Rollen, Berechtigungen, Benutzer-Lifecycle und Rechteherkunft sind in eine eigene Z_Cockpit-Seite integriert. Es wurde keine zweite Benutzerdatenbank aufgebaut.

Umgesetzt sind:

- eigener Navigationspunkt `Benutzer`;
- Benutzerliste mit Anzeigename und technischer Benutzer-ID;
- Status `Aktiv` / `Deaktiviert` aus der bestehenden Lifecycle-Auswertung;
- Profilrollen und aktive Projektrollen;
- effektive Rechte und Rechteherkunft aus dem bestehenden Autorisierungs-Evaluator;
- Rechtequellen wie Rolle, direkte Zuweisung, Delegation, DENY, Ausnahme, Whitelist und Blacklist;
- Filter nach Name/ID, Status, Rolle und Berechtigungszustand;
- fester Detailbereich rechts;
- Lifecycle-Historie;
- klare read-only Trennung zu späteren schreibenden Aktionen.

Ohne ProjectOS-Projektdatei werden keine Benutzer erfunden. Für reale Projektdaten kann ein vorhandenes v4-Bundle explizit angebunden werden:

```text
python -m tools.generate_z_cockpit --project-bundle <projektdatei>
```

Schreibende Änderungen bleiben den bestehenden autorisierten ProjectOS-Change-/Command-Services vorbehalten.

Detaildokumentation:

```text
docs/03_Developer/Z_COCKPIT_BENUTZERVERWALTUNG.md
```

## Whitelist-Verwaltung – nächster Schritt

Zwei verschiedene Whitelist-Arten müssen sichtbar getrennt bleiben:

- ProjectOS-Benutzer-Whitelist für einzelne Berechtigungen;
- Repository-Entwickler-Whitelist aus `config/authorized_developers.json` für freigegebene GitHub-Benutzer.

Blacklist/DENY bleibt vorrangig. Whitelist, Blacklist und Ausnahmerechte dürfen nicht zu einer unklaren gemeinsamen Liste zusammengezogen werden.

Die Benutzerseite stellt Rechteherkunft bereits read-only dar. Die nächste Stufe ergänzt kontrollierte Whitelist-/Blacklist-/Ausnahmeverwaltung und die getrennte Repository-Entwickler-Whitelist.

## Issue-/Fehlermeldung – danach

Geplant ist ein strukturierter Workflow für Fehlerberichte aus dem Z_Cockpit. Relevante Diagnose- und Versionsdaten sollen automatisch vorbereitet werden, aber vor einer externen Weitergabe für den Benutzer sichtbar und kontrollierbar bleiben.

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
