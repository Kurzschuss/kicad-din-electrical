# AP-0031 – Erste MCB-Domäne

**Status:** Abgeschlossen  
**Sprint:** 003 – Core Implementation  
**Paketversion:** 0.11.0

## Ziel

Ein erster vollständiger fachlicher Domain-Slice für Leitungsschutzschalter (MCB) wird auf dem ProjectOS-Kernframework aufgebaut.

## Implementiert

- unveränderliches `MCB`-Aggregat,
- `NominalCurrent`, `RatedVoltage`, `BreakingCapacity` und `PoleCount`,
- Auslösecharakteristiken B, C und D,
- MCB-spezifische fachliche Kennungen,
- versioniertes Validierungsprofil `VAL-MCB-DEFAULT-0001`,
- vier deterministisch ausgeführte Regeln,
- strukturierte Fehler und Warnungen,
- Unit-Tests.

## Startprofil

Das erste ProjectOS-Profil akzeptiert bewusst nur einen kleinen, konfigurationsnahen Wertebereich:

- Nennströme: 2, 4, 6, 10, 13, 16, 20, 25, 32, 40, 50 und 63 A,
- Bemessungsspannungen: 230 und 400 V,
- Schaltvermögen: 4.500, 6.000 und 10.000 A,
- Polzahlen: 1 bis 4.

Diese Werte sind ein technisches Startprofil und keine vollständige Normen- oder Herstellerfreigabe. Die spätere Domain Validation erweitert und versioniert dieses Profil.

## Regeln

- `REQ-MCB-0001`: Nennstrom im Startprofil,
- `REQ-MCB-0002`: Bemessungsspannung im Startprofil,
- `REQ-MCB-0003`: Schaltvermögen im Startprofil,
- `REQ-MCB-0004`: Hinweis bei einpoligen Geräten über 40 A.

## Fehlerkennungen

- `ERR-MCB-0001`: Nennstrom nicht freigegeben,
- `ERR-MCB-0002`: Spannung nicht freigegeben,
- `ERR-MCB-0003`: Schaltvermögen nicht freigegeben,
- `WARN-MCB-0001`: projektspezifische Prüfung empfohlen.

## Dateien

```text
projectos/mcb.py
tests/test_projectos_mcb.py
```

## Nächster Schritt

AP-0032 – RCCB-Domäne mit eigenen Wertobjekten und Validierungsregeln.
