# ProjectOS

ProjectOS ist die verbindliche Grundlage für die Weiterentwicklung von `kicad-din-electrical`.

## Status

- Architecture Freeze 1.0: beschlossen
- Sprint 001 – ProjectOS Foundation: abgeschlossen
- Sprint 002 – Core Object Model: abgeschlossen
- weitere ProjectOS-Implementierungsbausteine und Z_Cockpit-Kernseiten: umgesetzt
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

Rollen, Berechtigungen, Ausnahmerechte, Whitelist, Blacklist und Benutzer-Lifecycle besitzen bereits technische ProjectOS-Grundlagen. Der nächste Z_Cockpit-Ausbau integriert diese vorhandenen Bausteine in eine zentrale Benutzerverwaltung, ohne eine parallele Datenquelle einzuführen.

Die geplante Reihenfolge lautet:

1. Benutzerverwaltung;
2. Whitelist- und Berechtigungsverwaltung;
3. Issue- und Fehlermeldungsworkflow.

Die vollständige Planung steht in [Z_Cockpit – nächster Ausbau: Benutzer, Whitelist und Fehlermeldungen](Z_COCKPIT_AUSBAU_BENUTZER_WHITELIST_ISSUES.md).

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

Benutzerverwaltung im Z_Cockpit auf Basis der vorhandenen ProjectOS-Benutzer-, Persistenz- und Autorisierungsbausteine integrieren. Danach folgen Whitelist-/Berechtigungsverwaltung und Issue-/Fehlermeldungsworkflow.
