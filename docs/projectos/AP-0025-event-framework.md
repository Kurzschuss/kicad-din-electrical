# AP-0025 – Event-Framework

**Status:** Abgeschlossen  
**Version:** 1.0  
**Sprint:** 003 – Core Implementation  
**Abhängigkeiten:** AP-0014, AP-0022, AP-0023, AP-0024, ADR-0002

## Ziel

AP-0025 implementiert die erste ausführbare Ereignisgrundlage von ProjectOS.

## Implementierte Bausteine

- `DomainEvent`
- `DomainEventCollector`
- `LocalEventBus`

## DomainEvent

Ein Domänenereignis enthält:

- technische Ereigniskennung,
- stabilen Ereignistyp,
- UTC-Zeitpunkt,
- technische und fachliche Aggregatkennung,
- Aggregatrevision,
- optionale Korrelationskennung,
- unveränderliche Nutzdaten.

Technische Ereignistypen folgen dem Schema:

```text
<domaene>.<objekt>.<ereignis>
```

Beispiel:

```text
mcb.component.created
```

## Ereignissammlung

`DomainEventCollector` bewahrt die Erzeugungsreihenfolge und verhindert doppelte Ereigniskennungen. `clear()` gibt vor dem Leeren einen unveränderlichen Snapshot zurück.

## Lokaler Event-Bus

`LocalEventBus` verarbeitet Ereignisse synchron und vollständig offline. Handler werden in ihrer Registrierungsreihenfolge ausgeführt. Nicht registrierte Ereignistypen sind zulässig und ergeben null aufgerufene Handler.

## Bewusste Begrenzung

AP-0025 implementiert noch nicht:

- persistente Outbox,
- Wiederholungsstrategien,
- Dead-Letter-Ablage,
- asynchrone Verarbeitung,
- externe Integrationsereignisse.

Diese Funktionen bauen später auf dem hier definierten Vertrag auf.

## Tests

Die Tests prüfen:

- UTC-Normalisierung,
- Zeitzonenpflicht,
- Ereignistypvalidierung,
- unveränderliche Payloads,
- stabile Sammlungsreihenfolge,
- Schutz vor doppelten Ereignissen,
- deterministische Handlerreihenfolge,
- Verhalten ohne registrierte Handler.

## Repository-Dateien

```text
projectos/events.py
tests/test_projectos_events.py
docs/projectos/AP-0025-event-framework.md
```

## Ergebnis

AP-0025 ist abgeschlossen. Das ProjectOS-Paket trägt die Version `0.5.0`.
