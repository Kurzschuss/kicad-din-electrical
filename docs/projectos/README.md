# ProjectOS

ProjectOS ist die verbindliche Grundlage für die Weiterentwicklung von `kicad-din-electrical`.

## Status

- Architecture Freeze 1.0: beschlossen
- Sprint 001 – ProjectOS Foundation: abgeschlossen
- Sprint 002 – Core Object Model: abgeschlossen
- weitere ProjectOS-Implementierungsbausteine und Z_Cockpit-Kernseiten: umgesetzt
- Z_Cockpit-Benutzerverwaltung: umgesetzt
- Dokumentationsstand aktualisiert am 10. August 2026

## Verbindliche Architekturprinzipien

- Single Source of Truth
- Domain Ownership
- Object First
- Offline First
- Simulation First
- Documentation First
- Configuration before Code
- Drei Perspektiven: Entwickler, Engineering, Projektleiter

## Benutzerverwaltung

Rollen, Berechtigungen, Ausnahmerechte, Whitelist, Blacklist und Benutzer-Lifecycle besitzen technische ProjectOS-Grundlagen. Die Z_Cockpit-Benutzerverwaltung bindet diese vorhandenen Modelle jetzt read-only an, ohne eine parallele Datenquelle einzuführen.

Die Benutzerseite zeigt Benutzer-ID, Anzeigename, Lifecycle-Status, Rollen, effektive Rechte und Rechteherkunft. Ohne ProjectOS-Projektbundle werden keine Benutzer erfunden. Ein vorhandenes v4-Bundle kann explizit über `python -m tools.generate_z_cockpit --project-bundle <projektdatei>` angebunden werden.

Die verbleibende Reihenfolge lautet:

1. Whitelist- und Berechtigungsverwaltung;
2. Issue- und Fehlermeldungsworkflow.

Die vollständige Planung steht in [Z_Cockpit – Ausbau: Benutzer, Whitelist und Fehlermeldungen](Z_COCKPIT_AUSBAU_BENUTZER_WHITELIST_ISSUES.md). Die technische Benutzerseiten-Dokumentation liegt unter `docs/03_Developer/Z_COCKPIT_BENUTZERVERWALTUNG.md`.

## Improvement-System

Das Improvement-System umfasst Dublettenerkennung, Gewichtung, Priorisierung und GitHub-Anbindung.

## Erste fachliche Domänen

Die Domain Validation beginnt mit:

- MCB
- RCCB

## Arbeitsweise

Dieser Bereich dient als Entwicklungsprotokoll. Neue Änderungen sollen direkt repositoryfähig dokumentiert werden. Architekturänderungen erfolgen nur über ADRs oder dokumentierte Repository-Migrationen.

## Dokumente

- [Sprint 001 – ProjectOS Foundation](sprint-001-projectos-foundation.md)
- [Sprint 002 – Core Object Model](sprint-002-core-object-model.md)
- [AP-0016 – Persistenzmodell, Offline-Datenspeicher und Migrationen](AP-0016-persistenz-offline-speicher-migrationen.md)
- [Z_Cockpit – Benutzer, Whitelist und Fehlermeldungen](Z_COCKPIT_AUSBAU_BENUTZER_WHITELIST_ISSUES.md)
- [Maschinenlesbarer Arbeitsstand](arbeitsstand.yaml)
- [Architekturentscheidungen](../adr/)

## Nächster Schritt

Whitelist- und Berechtigungsverwaltung integrieren. Dabei bleiben ProjectOS-Benutzer-Whitelist und Repository-Entwickler-Whitelist strikt getrennt. Danach folgt der Issue-/Fehlermeldungsworkflow.
