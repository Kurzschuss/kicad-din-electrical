# ADR-0002 – Ereignisverarbeitung, Outbox und Audit-Trail

**Status:** Angenommen

## Kontext

ProjectOS muss fachliche Änderungen offlinefähig, zuverlässig und nachvollziehbar zwischen Domänen und externen Adaptern verarbeiten.

## Entscheidung

- Domänen-, Integrations- und technische Ereignisse werden getrennt.
- Ereignisse sind unveränderlich.
- Integrationsereignisse verwenden mindestens-einmal-Zustellung.
- Ereignisbehandler müssen idempotent sein.
- Aggregatänderungen und Integrationsereignisse werden über das Outbox-Muster atomar gespeichert.
- Nicht verarbeitbare Ereignisse gelangen in eine Dead-Letter-Ablage.
- Audit-Trail und technische Protokollierung bleiben getrennte Systeme.
- Audit-Einträge werden ausschließlich angehängt und nicht regulär geändert.
- ProjectOS wird in der ersten Architekturversion nicht als vollständiges Event-Sourcing-System umgesetzt.
- Der gesamte Ereignisbetrieb muss offline möglich sein.

## Konsequenzen

- Ereignisverträge benötigen stabile Typen und Versionen.
- Empfänger speichern verarbeitete Ereigniskennungen.
- Wiederholungen und Kompensation müssen getestet werden.
- Kritische Änderungen erzeugen separate Audit-Einträge.
