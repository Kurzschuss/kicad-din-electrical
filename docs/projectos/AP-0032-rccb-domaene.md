# AP-0032 – Erste RCCB-Domäne

**Status:** Abgeschlossen  
**Sprint:** 003 – Core Implementation  
**Paketversion:** 0.12.0

## Ziel

AP-0032 liefert den ersten ausführbaren Domain-Slice für Fehlerstrom-Schutzschalter (RCCB). Die Domäne nutzt die bereits implementierten ProjectOS-Bausteine für Kennungen, Repositories, strukturierte Meldungen und Validierung.

## Implementierte Objekte

- `RCCB`
- `RatedCurrent`
- `ResidualCurrent`
- `RCCBRatedVoltage`
- `RCCBPoleCount`
- `RCCBType`

Das RCCB-Aggregat ist unveränderlich und besitzt eine technische `ObjectId` sowie eine fachliche Kennung mit dem Präfix `RCCB-`.

## Startprofil

Das Profil `VAL-RCCB-DEFAULT-0001` enthält vier Regeln:

| Regel | Inhalt |
|---|---|
| `REQ-RCCB-0001` | Bemessungsstrom gegen die Startprofilwerte prüfen |
| `REQ-RCCB-0002` | Bemessungsdifferenzstrom gegen die Startprofilwerte prüfen |
| `REQ-RCCB-0003` | Spannung und Polzahl gemeinsam prüfen |
| `REQ-RCCB-0004` | Bei Typ AC eine projektspezifische Warnung ausgeben |

Unterstützte Startprofilwerte:

- Bemessungsstrom: 16, 25, 40, 63, 80 und 100 A
- Bemessungsdifferenzstrom: 10, 30, 100, 300 und 500 mA
- Bemessungsspannung: 230 und 400 V
- Polzahl: 2 oder 4
- Typen: AC, A, F und B

Für 400 V verlangt das Startprofil eine vierpolige Modellierung.

## Abgrenzung

Die Werte dienen ausschließlich als erster ProjectOS-Validierungssatz. Sie sind keine vollständige Normenprüfung und keine automatische Eignungsfreigabe für konkrete Anlagen, Netzformen, Hersteller oder Einsatzbedingungen.

Normen- und Herstellerwissen wird später als versionierte, dokumentierte und konfigurierbare Regelbasis ergänzt.

## Tests

Die Tests prüfen:

- ein gültiges RCCB-Aggregat,
- nicht unterstützte Bemessungsströme,
- nicht unterstützte Differenzströme,
- die Kombination 400 V und Polzahl,
- die Warnung für Typ AC,
- das vorgeschriebene Kennungspräfix,
- Unveränderlichkeit,
- ungültige Polzahlen.

## Dateien

```text
projectos/rccb.py
tests/test_projectos_rccb.py
docs/projectos/AP-0032-rccb-domaene.md
```

## Nächster Schritt

AP-0033 führt MCB und RCCB in einem ersten domänenübergreifenden Schutzgeräte-Validierungsszenario zusammen.
