# AP-0030 – Simulation-Framework

**Status:** Abgeschlossen  
**Sprint:** 003 – Core Implementation  
**Paketversion:** 0.10.0

## Ziel

AP-0030 stellt die ersten ausführbaren Bausteine für das Architekturprinzip **Simulation First** bereit. Fachliche Abläufe sollen mit kontrollierter Zeit, isoliertem Kontext und vollständig nachvollziehbarer Spur reproduzierbar ausgeführt werden können.

## Implementierte Bausteine

### `SimulationClock`

- liefert eine kontrollierte UTC-Zeit,
- kann deterministisch vorwärtsgesetzt werden,
- erlaubt keine naive Zeit ohne Zeitzone,
- verhindert rückwärts laufende Zeit.

### `SimulationContext`

Der unveränderliche Kontext enthält:

- Simulationskennung,
- Szenariokennung,
- Korrelationskennung,
- Startzeit,
- schreibgeschützte Metadaten.

### `SimulationTraceEntry`

Ein Spureneintrag enthält:

- fortlaufende Sequenz,
- UTC-Zeitpunkt,
- normalisierte Kategorie,
- Referenz,
- schreibgeschützte Zusatzdaten.

### `SimulationTrace`

Die Spur ist ausschließlich ergänzbar und:

- vergibt Sequenzen deterministisch,
- erhält die Erzeugungsreihenfolge,
- kann Befehle, Ergebnisse und beliebige Schritte aufzeichnen,
- kann `DomainEvent`-Objekte direkt übernehmen,
- liefert unveränderliche Snapshots.

## Verbindliche Regeln

1. Simulationszeit besitzt immer einen Zeitzonenbezug und wird intern als UTC geführt.
2. Die Simulationsuhr darf nicht rückwärts laufen.
3. Simulationskontext und Spureneinträge sind unveränderlich.
4. Eine Spur ist ausschließlich ergänzbar.
5. Sequenzen beginnen bei 1 und steigen lückenlos.
6. Ereignisse verwenden denselben fachlichen Ereignisvertrag wie der Produktivbetrieb.
7. Externe produktive Nebenwirkungen sind nicht Bestandteil dieses Frameworks.

## Tests

Die Tests prüfen:

- deterministische Zeitsteuerung,
- Abweisung naiver und rückwärts gerichteter Zeiten,
- unveränderliche Kontexte und Spureneinträge,
- fortlaufende Sequenzen,
- schreibgeschützte Metadaten,
- Aufzeichnung von Domänenereignissen.

## Nicht Bestandteil

Noch nicht implementiert sind:

- isolierte persistente Simulations-Repositories,
- Szenario-Runner,
- automatische Soll-Ist-Vergleiche,
- simulierte externe Adapter,
- vollständige Command-/Query-Ausführung innerhalb eines Simulationscontainers.

Diese Funktionen bauen auf dem jetzt stabilisierten Zeit-, Kontext- und Trace-Modell auf.

## Repository-Dateien

```text
projectos/simulation.py
tests/test_projectos_simulation.py
docs/projectos/AP-0030-simulation-framework.md
```

## Ergebnis

AP-0030 ist abgeschlossen. ProjectOS besitzt damit eine deterministische und nachvollziehbare Basis für spätere fachliche Simulationen von MCB, RCCB und domänenübergreifenden Anwendungsfällen.
