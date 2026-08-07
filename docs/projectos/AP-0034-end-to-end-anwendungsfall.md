# AP-0034 – Ausführbarer End-to-End-Anwendungsfall

**Status:** Abgeschlossen  
**Sprint:** 003 – Core Implementation  
**Paketversion:** 0.14.0

## Ziel

AP-0034 verbindet die bislang getrennt implementierten ProjectOS-Bausteine in einem ausführbaren Schutzgeräte-Anwendungsfall.

Der Command `protection.pair.register` durchläuft:

1. Command Bus,
2. Vertragsprüfung,
3. Autorisierung,
4. MCB-Validierung,
5. RCCB-Validierung,
6. domänenübergreifende Koordinationsvalidierung,
7. Speicherung beider Aggregate,
8. Kompensation bei einer teilweise fehlgeschlagenen Speicherung,
9. Audit-Trail,
10. strukturierte Ergebnisrückgabe.

## Simulation

Im Simulationsmodus werden dieselben fachlichen Validierungen ausgeführt. Es erfolgen jedoch:

- keine Repository-Schreibvorgänge,
- keine Audit-Einträge,
- keine produktiven Nebenwirkungen.

Stattdessen wird ein nachvollziehbarer Eintrag in der `SimulationTrace` erzeugt.

## Berechtigung

Der Anwendungsfall benötigt:

```text
PERM-PROT-REGISTER
```

Eine fehlende Berechtigung führt zu `ERR-AUTH-0001`, bevor Validierung oder Speicherung ausgeführt werden.

## Fehlergrenzen

- Ungültige Command-Daten: `ERR-APP-0034` bis `ERR-APP-0040`
- Fehlende Berechtigung: `ERR-AUTH-0001`
- Domänen- und Koordinationsfehler: bestehende `ERR-MCB-*`, `ERR-RCCB-*` und `ERR-PROT-*`
- Repository-Konflikte: bestehende `ERR-REP-*`

## Dateien

```text
projectos/workflows.py
tests/test_projectos_workflows.py
```

## Testfälle

Die Tests prüfen:

- erfolgreichen produktiven Durchlauf über den Command Bus,
- Speicherung von MCB und RCCB,
- Erstellung und Integrität des Audit-Eintrags,
- Abbruch ohne Nebenwirkungen bei fehlender Berechtigung,
- Abbruch ohne Nebenwirkungen bei ungültiger Schutzgerätekombination,
- Simulationsbetrieb ohne Persistenz und Audit,
- Aufzeichnung der Simulationsspur.

## Abgrenzung

Die In-Memory-Repositories bilden weiterhin eine Referenzimplementierung. Atomare Datenbanktransaktionen, persistente Outbox und produktive Recovery-Mechanismen folgen in späteren Arbeitspaketen.
