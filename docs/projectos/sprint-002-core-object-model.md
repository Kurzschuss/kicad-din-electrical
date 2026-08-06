# Sprint 002 – Core Object Model

**Status:** In Bearbeitung  
**Abgeschlossene Arbeitspakete:** AP-0011 bis AP-0015  
**Nächster Schritt:** AP-0016 – Persistenzmodell, Offline-Datenspeicher und Migrationen

## Ziel

Sprint 002 definiert das gemeinsame Objekt- und Anwendungsmodell, das von allen späteren Domänen verwendet wird.

## AP-0011 – Kernobjektmodell

Jedes ProjectOS-Objekt besitzt gemeinsame Grundattribute:

- technische UUID
- fachliche Kennung
- Name und Beschreibung
- Version
- Lebenszyklusstatus
- verantwortliche Domäne
- Erstellungs- und Änderungsinformationen
- Tags und Metadaten

Lebenszyklus:

```text
Entwurf → Prüfung → Genehmigt → Freigegeben → Veraltet → Archiviert
```

Beziehungen zwischen Objekten erfolgen über stabile Kennungen.

## AP-0012 – Domänenmodell und DDD-Grundlagen

ProjectOS unterscheidet verbindlich:

- Entitäten
- Wertobjekte
- Aggregate und Aggregatwurzeln
- Domänenservices
- Repositories
- Domänenereignisse
- Fabriken
- Spezifikationen und Richtlinien

Die Domänenschicht bleibt unabhängig von Datenbanken, Dateiformaten, Benutzeroberflächen, GitHub, KiCad und Frameworks.

Vorgesehene Bounded Contexts:

- Core
- Projektverwaltung
- Komponentenverwaltung
- MCB
- RCCB
- Symbolverwaltung
- Footprint-Verwaltung
- Validierung
- Simulation
- Benutzerverwaltung
- Berechtigungsverwaltung
- Improvement-System
- Dokumentation
- Build und Release

## AP-0013 – Kernwertobjekte und Basisschnittstellen

Definiert unter anderem:

- `ObjectId`
- `BusinessId`
- `ObjectVersion`
- `LifecycleStatus`
- `DomainId`
- `Timestamp`
- `CorrelationId`
- `AuditMetadata`
- `Result<T>`
- `ValidationMessage`
- `ValidationResult`
- `Page<T>`
- `Repository<TAggregate, TId>`
- `UnitOfWork`
- `Clock`
- Kennungsgeneratoren

Erwartbare fachliche Fehler werden als strukturierte Ergebnisse zurückgegeben. Exceptions bleiben unerwarteten technischen Fehlern vorbehalten.

## AP-0014 – Domänenereignisse, Ereignisbus und Audit-Trail

ProjectOS trennt:

- Domänenereignisse
- Integrationsereignisse
- technische Ereignisse
- Audit-Einträge
- Protokolleinträge

Verbindliche Entscheidungen:

- Ereignisse sind unveränderlich
- mindestens-einmal-Zustellung für Integrationsereignisse
- idempotente Ereignisbehandler
- Outbox-Muster
- lokale Dead-Letter-Ablage
- Audit-Trail getrennt von Logging
- Offline-Verarbeitung
- kein vollständiges Event Sourcing in der ersten Architekturversion

## AP-0015 – Befehle, Abfragen und Prozesskoordination

ProjectOS trennt schreibende Befehle und lesende Abfragen.

Kernbausteine:

- `Command`
- `CommandHandler`
- `CommandBus`
- `CommandResult`
- `Query`
- `QueryHandler`
- `QueryBus`
- spezialisierte Lesemodelle
- Ausführungspipeline
- `ExecutionContext`
- `AuthorizationService`
- Prozessmanager
- Kompensationsbefehle

Verbindliche Ausführungspipeline:

```text
Vertrag prüfen
→ Kontext aufbauen
→ Authentifizierung
→ Autorisierung
→ Idempotenz
→ Transaktion
→ Domänenlogik
→ Persistenz
→ Outbox
→ Audit
→ Commit
→ Ereignisverarbeitung
→ Ergebnis
```

Berechtigungsprüfungen berücksichtigen Rollen, Whitelist, Blacklist, Ausnahmerechte, Projektleitung, Stellvertretung, Vertrauensperson und Nachfolger.

## Zugehörige ADRs

- ADR-0001 – Einheitliches Kennungssystem
- ADR-0002 – Ereignisverarbeitung, Outbox und Audit-Trail
- ADR-0003 – Struktur der Anwendungsschicht und CQRS-Grundlagen

## Nächste Arbeitspakete

- AP-0016 – Persistenzmodell, Offline-Datenspeicher und Migrationen
- anschließend Abschluss von Sprint 002
- danach fachliche Domain Validation mit MCB und RCCB
