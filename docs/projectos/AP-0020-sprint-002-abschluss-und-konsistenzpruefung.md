# AP-0020 – Sprint-002-Abschluss und Konsistenzprüfung

**Status:** Abgeschlossen  
**Version:** 1.0  
**Sprint:** 002 – Core Object Model  
**Prüfdatum:** 6. August 2026

## 1. Ziel

Dieses Arbeitspaket schließt Sprint 002 formal ab. Es prüft die Arbeitspakete AP-0011 bis AP-0019 und die ADRs ADR-0001 bis ADR-0007 auf Vollständigkeit, Überschneidungen und Widersprüche.

## 2. Geprüfter Umfang

- Kernobjektmodell und DDD-Grundlagen
- gemeinsame Wertobjekte und Basisschnittstellen
- Ereignismodell, Outbox und Audit-Trail
- Befehle, Abfragen und Prozesskoordination
- Persistenz, Offline-Datenspeicher und Migrationen
- Konfigurationssystem und Registries
- Plugin- und Erweiterungsmodell
- Bootstrapping und Runtime-Komposition

## 3. Ergebnis der Konsistenzprüfung

### Identität und Kennungen

Technische Identitäten, fachliche Kennungen, Korrelations-, Ereignis-, Befehls-, Abfrage-, Audit- und Migrationskennungen sind klar getrennt. ADR-0001 bleibt die autoritative Quelle für Kennungsschemata.

### Schichten und Verantwortlichkeiten

Domänen-, Anwendungs-, Infrastruktur- und Präsentationsschicht sind eindeutig getrennt. Domänenlogik bleibt unabhängig von Datenbanken, YAML, GitHub, KiCad und UI-Frameworks.

### Persistenz und Ereignisse

Aggregatänderungen, Outbox-Einträge, Auditdaten und Idempotenzinformationen werden innerhalb einer lokalen Transaktion gespeichert. Das Ereignismodell ergänzt den aktuellen Aggregatzustand; vollständiges Event Sourcing ist nicht beschlossen.

### Konfiguration und Registries

Konfiguration ist versioniert und schema-validiert. Registries sind zentrale, unveränderliche Runtime-Snapshots. Fachliche Invarianten dürfen nicht durch Konfiguration überschrieben werden.

### Plugins und Runtime

Plugins erweitern ausschließlich veröffentlichte Erweiterungspunkte. Der ProjectOS-Kern bleibt ohne Plugins funktionsfähig. Die Runtime wird deterministisch aufgebaut und erst nach erfolgreicher Startvalidierung freigegeben.

### Offline- und Simulationsfähigkeit

Alle Kernfunktionen sind ohne Netzwerkverbindung vorgesehen. Simulation verwendet dieselbe Domänen- und Anwendungslogik wie der Produktivbetrieb, jedoch isolierte Adapter, Speicher und Zeitquellen.

## 4. Festgestellte Abgrenzungen

Folgende Begriffe werden verbindlich getrennt:

- Objektversion: fachliche Version eines Objekts
- Revision: technische Nebenläufigkeitskontrolle
- Schema-Version: Version der gespeicherten Datenstruktur
- Vertragsversion: Version von Commands, Queries und Events
- Release-Version: Version des Gesamtprodukts

Außerdem gelten:

- Audit-Trail ist kein allgemeines Logging.
- Registry ist keine Persistenzdatenbank.
- Plugin ist keine Domäne.
- Lesemodell ist kein Aggregat.
- Simulation ist kein vereinfachter zweiter Fachkern.

## 5. Offene Implementierungsentscheidungen

Die folgenden Punkte sind bewusst noch nicht technisch festgelegt:

- konkrete Programmiersprache und Runtime
- konkrete eingebettete Datenbank
- konkretes Dependency-Injection-Framework
- konkrete YAML- und Schema-Bibliotheken
- kryptografische Verfahren für Plugin-Signaturen und Audit-Verkettung

Diese Entscheidungen müssen vor oder während Sprint 003 durch ADRs getroffen werden.

## 6. Qualitätsprüfung

| Prüfkriterium | Ergebnis |
|---|---|
| Architecture Freeze eingehalten | Bestanden |
| Single Source of Truth berücksichtigt | Bestanden |
| Domain Ownership eindeutig | Bestanden |
| Object First umgesetzt | Bestanden |
| Offline First berücksichtigt | Bestanden |
| Simulation First berücksichtigt | Bestanden |
| Documentation First umgesetzt | Bestanden |
| Configuration before Code berücksichtigt | Bestanden |
| Sicherheitsgrenzen beschrieben | Bestanden |
| Testanforderungen beschrieben | Bestanden |
| Migrationsfähigkeit beschrieben | Bestanden |

## 7. Definition of Done

Sprint 002 gilt als abgeschlossen, weil:

- AP-0011 bis AP-0020 dokumentiert sind,
- ADR-0001 bis ADR-0007 vorliegen,
- die Architekturbausteine untereinander konsistent sind,
- keine kritischen Widersprüche festgestellt wurden,
- offene technische Entscheidungen transparent dokumentiert sind,
- der Übergang in die Implementierungsphase definiert ist.

## 8. Abschlussentscheidung

**Sprint 002 – Core Object Model ist abgeschlossen.**

Der Architecture Freeze 1.0 bleibt unverändert gültig.

## 9. Nächster Sprint

**Sprint 003 – Core Implementation**

Vorgesehene erste Arbeitspakete:

1. AP-0021 – Technologieauswahl und ausführbares Projektgerüst
2. AP-0022 – Core Identity und Kennungsframework
3. AP-0023 – Result- und Fehlerframework
4. AP-0024 – Validierungsframework
5. AP-0025 – Ereignissystem und Outbox-Grundlage
6. AP-0026 – Persistenzadapter und Migration Runner
7. AP-0027 – Command-/Query-Pipeline
8. AP-0028 – Autorisierung und Audit
9. AP-0029 – Simulationsruntime
10. AP-0030 – Sprint-003-Integration und Qualitätsgate

Ab Sprint 003 müssen Arbeitspakete neben Dokumentation auch ausführbaren Code, automatisierte Tests und Build-Integration liefern.

## 10. Commit-Vorschlag

```text
docs(projectos): AP-0020 Sprint 002 abschließen
```
