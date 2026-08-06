# ADR-0004 – Lokaler Datenspeicher, Persistenzgrenzen und Migrationen

**Status:** Angenommen  
**Datum:** 2026-08-06  
**Bezug:** AP-0016

## Kontext

ProjectOS muss vollständig offline betrieben werden können. Gleichzeitig müssen Aggregate, Ereignis-Outbox, Auditdaten, Prozesszustände und Migrationen konsistent und nachvollziehbar gespeichert werden. Die Domänenschicht darf nicht von einer konkreten Speichertechnologie abhängig werden.

## Entscheidung

1. Der autoritative Arbeitsbestand eines ProjectOS-Projekts liegt in einem lokalen, eingebetteten und transaktionalen Datenspeicher.
2. Die Domäne greift ausschließlich über Repository- und Unit-of-Work-Schnittstellen auf persistente Daten zu.
3. Persistenzmodelle und Mapper liegen in der Infrastrukturschicht.
4. Schreibzugriffe verwenden optimistische Revisionskontrolle.
5. Aggregatänderungen, Outbox-Einträge, Audit-Einträge, Prozesszustände und Befehlsidempotenz werden innerhalb derselben lokalen Transaktion gespeichert.
6. Auditdaten sind ausschließlich anhängend.
7. Schemaänderungen erfolgen ausschließlich über unveränderliche, versionierte und geprüfte `RM-*`-Migrationen.
8. Vor risikobehafteten Migrationen wird eine konsistente Sicherung erstellt.
9. Lesemodelle sind reproduzierbar und nicht fachlich autoritativ.
10. Simulationen verwenden isolierte Speicherbereiche.

## Technologie

SQLite ist der bevorzugte Referenzkandidat für die erste Implementierung. Die endgültige Produktwahl wird in einer gesonderten Technologie-ADR festgelegt, ohne die Domänenschnittstellen zu verändern.

## Konsequenzen

### Positiv

- vollständiger Offline-Betrieb,
- keine Serverinstallation,
- reproduzierbare Transaktionen,
- sichere Outbox- und Audit-Verarbeitung,
- testbare und austauschbare Persistenzadapter,
- kontrollierte Schemaentwicklung.

### Negativ

- Mapper und Persistenzmodelle verursachen zusätzlichen Implementierungsaufwand,
- Migrationen und Sicherungsprüfungen müssen dauerhaft gepflegt werden,
- parallele Schreibzugriffe benötigen Sperr- und Konfliktbehandlung.

## Verworfene Alternativen

### Cloud-Datenbank als primärer Speicher

Verworfen, da sie dem Prinzip `Offline First` widerspricht.

### Direkte Speicherung von Domänenobjekten ohne Persistenzgrenze

Verworfen, da technische Details in die Domäne eindringen und spätere Migrationen erschweren würden.

### Unversionierte automatische Schemaänderungen

Verworfen, da sie nicht reproduzierbar, nicht auditierbar und nicht sicher rücksetzbar sind.
