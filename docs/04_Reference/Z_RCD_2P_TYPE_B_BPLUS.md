# Z_RCD 2P – Typ B und B+

## Zweck

Diese Ergänzung erweitert die herstellerneutrale 2-polige RCD/FI-Gerätefamilie um allstromsensitive Vorlagen der Typen `B` und `B+`, ohne die freigegebene Symbolgeometrie von `Z_RCD:RCD` zu verändern.

Die bestehende A/F-Serie bleibt unverändert. B/B+ werden bewusst als getrennte Serie geführt, damit keine elektrischen Kenngrößen aus der A/F-Serie ungeprüft übernommen werden.

## Datenserie

Quelle im Repository:

```text
data/device_series/generic/rcd-2p-b-bplus-template-series.yaml
```

Die erzeugten Einzelgeräte liegen unter:

```text
data/devices/generated/generic.rcd-2p-b-bplus-template-series/
```

Die Serie erzeugt 16 herstellerneutrale Vorlagen aus:

- Bemessungsstrom: 16 A, 25 A, 40 A, 63 A;
- Bemessungsdifferenzstrom: 30 mA, 300 mA;
- RCD-Typ: B, B+.

Zusammen mit den vorhandenen 64 A/F-Varianten stehen damit 80 datengetriebene 2P-RCD-Varianten zur Verfügung.

## Bewusst nicht pauschal gesetzt

Für die neue B/B+-Serie werden folgende Werte nicht herstellerneutral festgeschrieben:

```text
rated_short_circuit_current_ka
making_breaking_capacity_ka
```

Diese Kenngrößen können vom konkreten Produkt, der Baureihe und den angegebenen Bedingungen abhängen. Sie müssen bei einem realen Gerät aus dem zugehörigen Herstellerdatenblatt übernommen und geprüft werden.

Die vorhandene A/F-Serie behält ihre bereits freigegebenen Werte unverändert.

## Evidenzbasis

Die Auswahl der 2-poligen Typen B und B+ sowie der verwendeten Bemessungsströme und Differenzströme orientiert sich an aktuellen Herstellerprogrammen, unter anderem:

- Siemens SENTRON `5SV3324-4`: zweipoliger RCCB Typ B, 40 A, 30 mA;
- Doepke DFS 2 Typ B, z. B. `DFS 2 016-2/0,03-B NK` und `DFS 2 063-2/0,30-B NK`;
- Doepke DFS 2 Typ B+, z. B. `DFS 2 016-2/0,03-B+` und `DFS 2 063-2/0,30-B+`.

Primärquellen:

- https://mall.industry.siemens.com/mall/en/de/Catalog/Product/5SV3324-4
- https://www.doepke.de/de/produkte/schuetzen/fehlerstromschutzschalter-rccb/fehlerstromtyp-b/basisausfuehrung/09114595
- https://www.doepke.de/de/produkte/schuetzen/fehlerstromschutzschalter-rccb/fehlerstromtyp-b/basisausfuehrung/09146595
- https://www.doepke.de/de/produkte/schuetzen/fehlerstromschutzschalter-rccb/fehlerstromtyp-b-plus/basisausfuehrung/09114596
- https://www.doepke.de/de/produkte/schuetzen/fehlerstromschutzschalter-rccb/fehlerstromtyp-b-plus/basisausfuehrung/09146596

Diese Quellen dienen als Evidenz dafür, dass die Geräteklasse und die gewählten Planungsparameter real vorkommen. Die generischen Varianten sind keine Behauptung, dass jeder Hersteller jede Kombination unter identischen Zusatzkenngrößen anbietet.

## Symbol und Footprint

Alle Varianten verwenden weiterhin:

```text
Symbol: Z_RCD:RCD
Polzahl: 2
Module: 2
Footprint Policy: optional
```

Die elektrische Symbolgeometrie bleibt unverändert. Vor einer konkreten mechanischen Konstruktion muss der Footprint gegen das Datenblatt des ausgewählten Geräts geprüft werden.
