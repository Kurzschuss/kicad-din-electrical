# AP-0021 – Technologieauswahl und ausführbares Projektgerüst

**Status:** Abgeschlossen  
**Version:** 1.0  
**Sprint:** 003 – Core Implementation

## Ziel

ProjectOS erhält erstmals ein direkt importierbares und durch pytest prüfbares Softwaregerüst.

## Technologieentscheidung

Die Kernimplementierung verwendet Python, da das bestehende Repository bereits Python und pytest für Werkzeuge und Tests einsetzt.

Siehe ADR-0008.

## Implementierte Dateien

```text
projectos/
├── __init__.py
└── runtime.py

tests/
└── test_projectos_runtime.py
```

## Implementierter Umfang

- importierbares Paket `projectos`,
- Paketversion `0.1.0`,
- unveränderlicher `RuntimeInfo`-Datentyp,
- Fabrikfunktion `create_runtime_info`,
- deutsche Standardsprache `de-DE`,
- explizite Kennzeichnung von Offline First und Simulation First,
- UTC-Zeitstempel,
- Validierung der Versionsangabe.

## Tests

Die Tests prüfen:

- Architekturstandardwerte,
- UTC-Zeitstempel,
- Versionsnormalisierung,
- Ablehnung leerer Versionen,
- Unveränderlichkeit des Runtime-Snapshots.

## Qualitätsregeln

- öffentliche Schnittstellen sind typisiert und dokumentiert,
- Standardbibliothek wird bevorzugt,
- keine Netzwerkabhängigkeit,
- keine zusätzliche Build-Toolchain,
- bestehender pytest-Ablauf bleibt verwendbar.

## Definition of Done

- Technologieentscheidung als ADR dokumentiert,
- ausführbares Python-Paket angelegt,
- erster Kernbaustein implementiert,
- automatisierte Tests ergänzt,
- bestehende Repository-Teststruktur verwendet.

## Nächster Schritt

AP-0022 – Identifier-Framework mit `ObjectId`, `BusinessId`, `CorrelationId` und zugehörigen Tests.
