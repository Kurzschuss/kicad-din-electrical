# Arbeitsstand 2026-08-10 – Z_Cockpit Layout und nächster Ausbau

## Visuell festgelegter Stand

Die obere Darstellung der Z_Cockpit-Seiten wird am Bibliotheksbereich ausgerichtet.

Verbindliches Muster:

```text
Menü-/Seitentitel (kurze Erklärung zum Bereich)
```

Die Erklärung steht in kleinerer, zurückhaltender Schrift direkt in derselben Überschriftszeile. Eine zusätzliche zweite Erklärungszeile unmittelbar unter dem Seitentitel soll vermieden werden.

Die Änderung gilt für Seiten, die bisher direkt unter ihrer ersten Überschrift einen erklärenden Absatz hatten. `Einstellungen` und `Sicherheit` wurden ausdrücklich auf dieses Muster umgestellt. Start, Qualität, Hersteller, Diagnose und Dokumentation werden im erzeugten Cockpit ebenfalls auf dieses gemeinsame Kopfzeilenmuster normalisiert.

`Geräte` und `Bibliotheken` werden strukturell nicht umgebaut. Die bereits freigegebene Bibliotheksansicht bleibt Referenz für die kompakte Kopfgestaltung.

Zusätzlich wird auf der Sicherheitsseite der unnötige obere Abstand vor der Sicherheitstabelle entfernt.

## Nicht verändern

Ohne neue ausdrückliche Anforderung bleiben unverändert:

- freigegebene MCB-Geometrie;
- freigegebene RCD/FI-Geometrien 2P und 3+N/4P;
- Bibliotheksarbeitslogik;
- rechter Eigenschaften-/Vorschaubereich;
- separates Scrollverhalten der Geräte-ID-Listen.

## Nächste verbindliche Ausbaureihenfolge

Nach Abschluss dieser Layoutvereinheitlichung wird in folgender Reihenfolge weitergearbeitet:

1. **Benutzerverwaltung**
2. **Whitelist- und Berechtigungsverwaltung**
3. **Issue- und Fehlermeldungsworkflow**

Die vollständige fachliche Planung steht in:

```text
docs/projectos/Z_COCKPIT_AUSBAU_BENUTZER_WHITELIST_ISSUES.md
```

## Benutzerverwaltung

Die vorhandenen ProjectOS-Bausteine für Benutzer, Rollen, Berechtigungen, Benutzer-Lifecycle, Persistenz und Rechteherkunft werden ins Z_Cockpit integriert. Es wird keine zweite Benutzerdatenbank aufgebaut.

Zielbild:

- Benutzerliste;
- aktiv/deaktiviert;
- Rollen;
- effektive Rechte;
- Rechteherkunft;
- Lifecycle und Änderungsinformationen;
- Filter links und fester Detailbereich rechts;
- schreibende Änderungen ausschließlich über vorhandene autorisierte ProjectOS-Services.

## Whitelist-Verwaltung

Zwei verschiedene Whitelist-Arten müssen sichtbar getrennt bleiben:

- ProjectOS-Benutzer-Whitelist für einzelne Berechtigungen;
- Repository-Entwickler-Whitelist aus `config/authorized_developers.json` für freigegebene GitHub-Benutzer.

Blacklist/DENY bleibt vorrangig. Whitelist, Blacklist und Ausnahmerechte dürfen nicht zu einer unklaren gemeinsamen Liste zusammengezogen werden.

## Issue-/Fehlermeldung

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
