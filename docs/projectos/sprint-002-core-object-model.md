# Sprint 002 – Core Object Model

**Status:** In Bearbeitung  
**Abgeschlossene Arbeitspakete:** AP-0011 bis AP-0016  
**Nächster Schritt:** Konsistenzreview und Abschluss von Sprint 002

## Ziel

Sprint 002 definiert das gemeinsame Objekt-, Anwendungs- und Persistenzmodell, das von allen späteren Domänen verwendet wird.

## AP-0011 – Kernobjektmodell

Jedes ProjectOS-Objekt besitzt gemeinsame Grundattribute:

- technische UUID,
- fachliche Kennung,
- Name und Beschreibung,
- Version,
- Lebenszyklusstatus,
- verantwortliche Domäne,
- Erstellungs- und Änderungsinformationen,
- Tags und Metadaten.

Beziehungen zwischen Objekten erfolgen über stabile Kennungen.

## AP-0012 – Domänenmodell und DDD-Grundlagen

ProjectOS unterscheidet verbindlich:

- Entitäten,
- Wertobjekte,
- Aggregate und Aggregatwurzeln,
- Domänenservices,
- Repositories,
- Domänenereignisse,
- Fabriken,
- Spezifikationen und Richtlinien.

Die Domänenschicht bleibt unabhängig von Datenbanken, Dateiformaten, Benutzeroberflächen, GitHub, KiCad und Frameworks.

## AP-0013 – Kernwertobjekte und Basisschnittstellen

Definiert unter anderem:

- `ObjectId`,
- `BusinessId`,
- `ObjectVersion`,
- `LifecycleStatus`,
- `DomainId`,
- `Timestamp`,
- `CorrelationId`,
- `AuditMetadata`,
- `Result<T>`,
- `ValidationMessage`,
- `ValidationResult`,
- `Page<T>`,
- `Repository<TAggregate, TId>`,
- `UnitOfWork`,
- `Clock`,
- Kennungsgeneratoren.

Erwartbare fachliche Fehler werden als strukturierte Ergebnisse zurückgegeben. Exceptions bleiben unerwarteten technischen Fehlern vorbehalten.

## AP-0014 – Domänenereignisse, Ereignisbus und Audit-Trail

ProjectOS trennt Domänenereignisse, Integrationsereignisse, technische Ereignisse, Audit-Einträge und Protokolleinträge.

Verbindliche Entscheidungen:

- Ereignisse sind unveränderlich,
- mindestens-einmal-Zustellung für Integrationsereignisse,
- idempotente Ereignisbehandler,
- Outbox-Muster,
- lokale Dead-Letter-Ablage,
- Audit-Trail getrennt von Logging,
- Offline-Verarbeitung,
- kein vollständiges Event Sourcing in der ersten Architekturversion.

## AP-0015 – Befehle, Abfragen und Prozesskoordination

ProjectOS trennt schreibende Befehle und lesende Abfragen.

Kernbausteine:

- `Command`, `CommandHandler`, `CommandBus`, `CommandResult`,
- `Query`, `QueryHandler`, `QueryBus`,
- spezialisierte Lesemodelle,
- Ausführungspipeline,
- `ExecutionContext`,
- `AuthorizationService`,
- Prozessmanager und Kompensationsbefehle.

Berechtigungsprüfungen berücksichtigen Rollen, Whitelist, Blacklist, Ausnahmerechte, Projektleitung, Stellvertretung, Vertrauensperson und Nachfolger.

## AP-0016 – Persistenzmodell, Offline-Datenspeicher und Migrationen

ProjectOS verwendet einen lokalen, eingebetteten und transaktionalen Datenspeicher als primäre Arbeitsquelle.

Verbindliche Entscheidungen:

- vollständiger Offline-Betrieb,
- Domäne unabhängig von der Speichertechnologie,
- Repository- und Mapper-Grenze,
- optimistische Revisionskontrolle,
- atomare Speicherung von Aggregat, Outbox, Audit, Prozesszustand und Befehlsidempotenz,
- ausschließlich anhängende Auditdaten,
- versionierte `RM-*`-Migrationen,
- Sicherung vor risikobehafteten Migrationen,
- reproduzierbare Lesemodelle,
- isolierte Simulationspersistenz.

Vollständige Spezifikation:

- [`AP-0016-persistenz-offline-speicher-migrationen.md`](AP-0016-persistenz-offline-speicher-migrationen.md)

## Zugehörige ADRs

- ADR-0001 – Einheitliches Kennungssystem
- ADR-0002 – Ereignisverarbeitung, Outbox und Audit-Trail
- ADR-0003 – Struktur der Anwendungsschicht und CQRS-Grundlagen
- ADR-0004 – Lokaler Datenspeicher, Persistenzgrenzen und Migrationen

## Nächste Schritte

1. Konsistenzreview für AP-0011 bis AP-0016.
2. Auswahl der ersten konkreten Implementierungstechnologien.
3. Abschluss von Sprint 002.
4. Beginn der fachlichen Domain Validation mit MCB und RCCB.
