# Z_RCD 4P – Typ F

## Zweck

Diese Ergänzung erweitert die herstellerneutrale 3+N-/4-polige RCD/FI-Gerätefamilie um mischfrequenzsensitive Vorlagen des Typs `F`, ohne die freigegebene Symbolgeometrie von `Z_RCD:RCD_4P` zu verändern.

Die bestehende 4P-Serie mit Typ A, B und B+ bleibt unverändert. Typ F wird bewusst als getrennte Serie geführt, damit keine Kurzschluss- oder Schaltvermögenswerte aus der älteren Matrix ungeprüft übernommen werden.

## Datenserie

Quelle im Repository:

```text
data/device_series/generic/rcd-4p-f-template-series.yaml
```

Die erzeugten Einzelgeräte liegen unter:

```text
data/devices/generated/generic.rcd-4p-f-template-series/
```

Die Serie erzeugt 9 herstellerneutrale Vorlagen aus:

- Bemessungsstrom: 25 A, 40 A, 63 A;
- Bemessungsdifferenzstrom: 30 mA, 300 mA, 500 mA;
- RCD-Typ: F.

Zusammen mit den vorhandenen 72 A/B/B+-Varianten stehen damit 81 datengetriebene 4P-RCD-Varianten zur Verfügung.

## Bewusst nicht pauschal gesetzt

Für die neue Typ-F-Serie werden folgende Werte nicht herstellerneutral festgeschrieben:

```text
rated_short_circuit_current_ka
making_breaking_capacity_ka
```

Diese Kenngrößen hängen vom konkreten Produkt, der Baureihe und teilweise von vorgeschalteten Schutzorganen ab. Sie müssen bei einem realen Gerät aus dem zugehörigen Herstellerdatenblatt übernommen und geprüft werden.

Die vorhandene A/B/B+-Serie behält ihre bereits freigegebenen Werte unverändert.

## Evidenzbasis

Aktuelle Herstellerprogramme belegen vierpolige Typ-F-RCCBs in der gewählten Planungsmatrix. Beispiele:

- Eaton `PFIM-25/4/003-G/F`: 4-polig, 25 A, 30 mA, Typ F;
- Eaton `PFIM-40/4/003-G/F`: 4-polig, 40 A, 30 mA, Typ F;
- Eaton `PFIM-63/4/003-G/F`: 4-polig, 63 A, 30 mA, Typ F;
- Doepke `DFS 4 025-4/0,30-F`: 4-polig, 25 A, 300 mA, Typ F;
- Doepke `DFS 4 025-4/0,50-F`: 4-polig, 25 A, 500 mA, Typ F;
- Doepke `DFS 4 040-4/0,30-F`: 4-polig, 40 A, 300 mA, Typ F;
- Doepke `DFS 4 040-4/0,50-F`: 4-polig, 40 A, 500 mA, Typ F;
- Eaton `PFIM-63/4/03-G/F`: 4-polig, 63 A, 300 mA, Typ F;
- Doepke `DFS 4 063-4/0,50-F`: 4-polig, 63 A, 500 mA, Typ F.

Primärquellen:

- https://www.eaton.com/us/en-us/skuPage.187455.html
- https://www.eaton.com/de/de-de/skuPage.187456.html
- https://www.eaton.com/de/de-de/skuPage.187358.html
- https://www.doepke.de/de/produkte/schuetzen/fehlerstromschutzschalter-rccb/fehlerstromtyp-f/basisausfuehrung/09126820
- https://www.doepke.de/de/produkte/schuetzen/fehlerstromschutzschalter-rccb/fehlerstromtyp-f/basisausfuehrung/09127820
- https://www.doepke.de/de/produkte/schuetzen/fehlerstromschutzschalter-rccb/fehlerstromtyp-f/basisausfuehrung/09136820
- https://www.doepke.de/de/produkte/schuetzen/fehlerstromschutzschalter-rccb/fehlerstromtyp-f/basisausfuehrung/09137820
- https://www.eaton.com/at/de-de/skuPage.187361.html
- https://www.doepke.de/en/products/protect/residual-current-circuit-breakers-rccbs/type-of-residual-current-f/basic-design/09147820

Die Quellen belegen, dass die Geräteklasse und die gewählten Planungsparameter real vorkommen. Die generischen Vorlagen ersetzen kein konkretes Herstellerdatenblatt.

## Symbol und Footprint

Alle Varianten verwenden weiterhin:

```text
Symbol: Z_RCD:RCD_4P
Polzahl: 4
Module: 4
Footprint Policy: optional
```

Die elektrische Symbolgeometrie bleibt unverändert. Vor einer konkreten mechanischen Konstruktion muss der Footprint gegen das Datenblatt des ausgewählten Geräts geprüft werden.
