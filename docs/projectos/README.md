# ProjectOS

ProjectOS ist die verbindliche Grundlage für die Weiterentwicklung von `kicad-din-electrical`.

## Status

- Architecture Freeze 1.0: beschlossen
- Sprint 001 – ProjectOS Foundation: abgeschlossen
- Sprint 002 – Core Object Model: abgeschlossen
- weitere ProjectOS-Implementierungsbausteine und Z_Cockpit-Kernseiten: umgesetzt
- Z_Cockpit-Benutzerverwaltung: umgesetzt
- Z_Cockpit-Whitelist-/Berechtigungsverwaltung: umgesetzt
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

## Benutzer und Berechtigungen

Rollen, Berechtigungen, Ausnahmerechte, Whitelist, Blacklist und Benutzer-Lifecycle besitzen technische ProjectOS-Grundlagen. Das Z_Cockpit bindet diese vorhandenen Modelle read-only an, ohne eine parallele Datenquelle einzuführen.

Die Benutzerseite zeigt Benutzer-ID, Anzeigename, Lifecycle-Status, Rollen, effektive Rechte und Rechteherkunft. Die Berechtigungsseite ergänzt die einzelnen Rechtezuweisungen mit Quelle, Wirkung, Scope, Risikoklasse, Gültigkeit, Widerrufsstatus und effektiver Entscheidung.

ProjectOS-Benutzer-Whitelist und Repository-Entwickler-Whitelist bleiben strikt getrennt. Die Repositoryquelle ist weiterhin:

```text
config/authorized_developers.json
```

Ohne ProjectOS-Projektbundle werden keine Benutzer oder ProjectOS-Rechte erfunden. Ein vorhandenes v4-Bundle kann explizit angebunden werden:

```text
python -m tools.generate_z_cockpit --project-bundle <projektdatei>
```

ProjectOS-Rechteänderungen müssen über die vorhandenen Change-/Command-/Autorisierungsservices laufen. Die statische Cockpit-Datei besitzt keine eigene Schreiblogik.

Technische Dokumentation:

- `docs/03_Developer/Z_COCKPIT_BENUTZERVERWALTUNG.md`;
- `docs/03_Developer/Z_COCKPIT_BERECHTIGUNGEN.md`.

## Nächster Z_Cockpit-Ausbau

Als nächster fachlicher Schritt ist jetzt der **Issue- und Fehlermeldungsworkflow** geplant.

Die vollständige Planung steht in [Z_Cockpit – Ausbau: Benutzer, Whitelist und Fehlermeldungen](Z_COCKPIT_AUSBAU_BENUTZER_WHITELIST_ISSUES.md).

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

Issue- und Fehlermeldungsworkflow integrieren. Dabei sollen relevante Diagnose- und Versionsdaten reproduzierbar vorbereitet werden, ohne Tokens, Schlüssel oder unnötige personenbezogene Daten automatisch weiterzugeben.
