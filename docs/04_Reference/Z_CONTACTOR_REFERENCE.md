# Z_CONTACTOR – Leistungsschütz

## Zweck

`Z_CONTACTOR` stellt die herstellerneutrale elektrische Grundfunktion eines dreipoligen Leistungsschützes dar. Das Symbol bildet drei Hauptschließer und die Betätigungsspule ab; Herstellergehäuse, konkrete Spulenspannungen, Hilfskontaktbestückungen und mechanische Abmessungen gehören nicht in das neutrale Basissymbol.

## Kanonisches Symbol

- Bibliothek: `Z_CONTACTOR`
- Symbol: `CONTACTOR`
- qualifizierte ID: `Z_CONTACTOR:CONTACTOR`
- Referenzkennzeichen: `K`
- Hauptkontakte: 3 Schließer
- Hauptanschlüsse: `1/L1–2/T1`, `3/L2–4/T2`, `5/L3–6/T3`
- Spulenanschlüsse: `A1`, `A2`
- Footprint-Policy: `optional`

Die drei Hauptkontakte sind getrennt dargestellt und mechanisch gekoppelt. Die Spule ist als eigener Funktionsblock innerhalb desselben Symbols sichtbar. Hilfskontakte werden nicht in das Basissymbol hineingezogen; sie sind ein eigener späterer Bibliotheksbaustein.

## Herstellerneutrale Geräteserie

Quelle:

`data/device_series/generic/contactor-3p-ac3-template-series.yaml`

Die erste Planungsmatrix enthält die AC-3-Nennstromstufen:

- 9 A
- 12 A
- 18 A
- 25 A
- 32 A

Alle fünf Varianten besitzen:

- drei Pole;
- drei Hauptschließer und keine Hauptöffner;
- Nutzungskategorie `AC-3`;
- Symbol `Z_CONTACTOR:CONTACTOR`;
- `footprint_policy: optional`;
- `source_status: template`.

Die drei vorhandenen Hauptschließer werden mit `main_contacts_no: 3` beschrieben. Nicht vorhandene Hauptöffner werden bewusst **nicht** als numerischer Nullwert gespeichert; das Feld `main_contacts_nc` fehlt in dieser Basisserie vollständig. Damit bleiben technische Zahlenfelder positiv und eine spätere tatsächlich vorhandene NC-Bestückung kann eindeutig modelliert werden.

## Bewusst nicht pauschalisierte Werte

Die neutrale Serie enthält absichtlich **keine** allgemeine Spulenspannung, keine Spulenart AC/DC und keine Modul- oder Gehäusebreite. Diese Eigenschaften hängen von der konkreten Hersteller-/Bestellvariante ab und werden erst mit belegten Produktdaten ergänzt.

Auch fest eingebaute Hilfskontakte werden nicht als gemeinsame Eigenschaft der neutralen Basis behauptet. Herstellerfamilien unterscheiden sich hier je Baugröße und Bestellvariante.

## Technischer Referenzrahmen

Die neutrale Struktur wurde gegen aktuelle Herstellerfamilien plausibilisiert:

- Schneider Electric TeSys D: dreipolige Leistungsschütze; die Produktfamilie führt unter anderem 9, 12, 18, 25 und 32 A bei AC-3. Beispiel: `LC1D09BD`, 3-polig, 9 A bei 400 V AC-3.
- Siemens SIRIUS 3RT: dreipolige Leistungsschütze nach AC-3/AC-3e. Beispiel: `3RT2017-1AN21`, 12 A, 3-polig.
- ABB AF: dreipolige Schütze mit drei Hauptschließern. Beispiel: `AF12-30-10K-12`.
- Eaton Moeller DILM: dreipolige Leistungsschütze für Motoranwendungen. Beispiel: `DILM9-01(24VDC)` beziehungsweise Varianten der DILM-Baureihe.

Diese Herstellerangaben sind **Plausibilitäts- und Strukturbelege**. Sie werden nicht zu generischen Bestellnummern oder pauschalen Spulendaten umgedeutet. Herstellerbezogene Produktserien werden getrennt über die neue Hersteller-Stammdatenebene und den technischen Gerätekatalog aufgebaut.

## Normativer Bezug

Der neutrale Referenzwert `DIN EN 60947-4-1` kennzeichnet die Geräteklasse Schütze und Motorstarter. Konkrete Produktkonformität wird ausschließlich aus dem jeweiligen Herstellerdatenblatt übernommen.

## Qualitätsstatus

Das Paket darf den Reifegrad `Geprüft` nur erhalten, wenn Symbolquelle, Geräteserie, generierte Einzelgeräte, Vorschau, Referenzdokumentation und Regressionstests gemeinsam durch die Projektvalidatoren und die vollständige CI geprüft wurden.

Für `Praxisgetestet` fehlt anschließend weiterhin ein dokumentiertes Beispielprojekt.
