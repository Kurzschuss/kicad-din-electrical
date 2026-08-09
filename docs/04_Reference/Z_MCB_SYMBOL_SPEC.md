# Z_MCB – Symbol- und Varianten-Spezifikation

## Zweck

`Z_MCB` ist das Referenzpaket für herstellerneutrale Leitungsschutzschalter. Diese Spezifikation ergänzt den bestehenden 1P-Goldstandard um die korrigierte DIN/IEC-Darstellung und eine eigenständige 3P-Variante.

Maßgeblich bleiben in dieser Reihenfolge:

1. KiCad-Konventionen und technisch erforderliche KiCad-Formate,
2. `docs/00_Project/SYMBOL_STYLE_GUIDE.md`,
3. `rules/z/symbols/*.json` und `docs/04_Reference/Z_SYMBOL_DIMENSIONS.md`.

## Symbol-IDs und Kompatibilität

| Variante | Qualifizierte Symbol-ID | Zweck |
|---|---|---|
| 1P | `Z_MCB:MCB` | bestehende technische ID bleibt unverändert |
| 3P | `Z_MCB:MCB_3P` | neue eigenständige Polvariante |

Nennstrom und Auslösecharakteristik erzeugen **keine kopierten Symbolkörper**. Sie werden als Gerätevarianten im Gerätekatalog modelliert. Dadurch bleibt die elektrische Geometrie eine gemeinsame, reproduzierbare Sicht auf die Gerätefamilie.

## Verbindliche Geometrie

Für beide Symbole gelten die vorhandenen Regeln:

- Anschlussraster: 100 mil (`ZSYM-003`)
- grafisches Unterraster: 50 mil
- Pinlänge: 100 mil (`ZSYM-004`)
- Linienbreite: 10 mil (`ZSYM-005`)
- Primärtext: 50 mil (`ZSYM-006`)
- Referenzkennzeichen: `Q`
- `Z_Footprint_Policy`: `optional`
- elektrische Pins: `passive`
- Stromflussdarstellung bei Installationsgeräten: oben nach unten

Die passive Pinklassifikation hält das generische Schutzschaltersymbol in unterschiedlichen Einspeise- und Lastkonfigurationen ERC-neutral.

## 1P – `Z_MCB:MCB`

Die bestehende Symbol-ID wird aus Kompatibilitätsgründen beibehalten. Anschluss `1` liegt oben, Anschluss `2` unten. Die Funktionsgrafik zeigt den geöffneten Schaltkontakt mit Auslösemechanik; die bisherige horizontale Rechteckdarstellung wird nicht weiter verwendet.

Zielbreite gemäß `Z_SYMBOL_DIMENSIONS.md`: **400 mil**.

## 3P – `Z_MCB:MCB_3P`

Die drei Pole werden in einem gemeinsamen Symbol dargestellt. Jeder Pol besitzt dieselbe Schutzschalter-Funktionsgrafik; die mechanische Kopplung der Pole ist grafisch kenntlich gemacht.

| Pol | oben | unten |
|---|---:|---:|
| L1 | `1` | `2` |
| L2 | `3` | `4` |
| L3 | `5` | `6` |

Zielbreite gemäß `Z_SYMBOL_DIMENSIONS.md`: **800 mil**.

## Gerätevarianten 3P

Datenquelle: `data/device_series/generic/mcb-3p-template-series.yaml`

Alle 42 Varianten referenzieren dasselbe Symbol `Z_MCB:MCB_3P`.

| Varianten-ID | Charakteristik | Nennstrom | Part Number | Deutsche Anzeige |
|---|---|---:|---|---|
| `b2` | B | 2 A | `MCB-3P-B2` | Leitungsschutzschalter B2, 3-polig |
| `b4` | B | 4 A | `MCB-3P-B4` | Leitungsschutzschalter B4, 3-polig |
| `b6` | B | 6 A | `MCB-3P-B6` | Leitungsschutzschalter B6, 3-polig |
| `b10` | B | 10 A | `MCB-3P-B10` | Leitungsschutzschalter B10, 3-polig |
| `b13` | B | 13 A | `MCB-3P-B13` | Leitungsschutzschalter B13, 3-polig |
| `b16` | B | 16 A | `MCB-3P-B16` | Leitungsschutzschalter B16, 3-polig |
| `b20` | B | 20 A | `MCB-3P-B20` | Leitungsschutzschalter B20, 3-polig |
| `b25` | B | 25 A | `MCB-3P-B25` | Leitungsschutzschalter B25, 3-polig |
| `b32` | B | 32 A | `MCB-3P-B32` | Leitungsschutzschalter B32, 3-polig |
| `b40` | B | 40 A | `MCB-3P-B40` | Leitungsschutzschalter B40, 3-polig |
| `b50` | B | 50 A | `MCB-3P-B50` | Leitungsschutzschalter B50, 3-polig |
| `b63` | B | 63 A | `MCB-3P-B63` | Leitungsschutzschalter B63, 3-polig |
| `b80` | B | 80 A | `MCB-3P-B80` | Leitungsschutzschalter B80, 3-polig |
| `b125` | B | 125 A | `MCB-3P-B125` | Leitungsschutzschalter B125, 3-polig |
| `c2` | C | 2 A | `MCB-3P-C2` | Leitungsschutzschalter C2, 3-polig |
| `c4` | C | 4 A | `MCB-3P-C4` | Leitungsschutzschalter C4, 3-polig |
| `c6` | C | 6 A | `MCB-3P-C6` | Leitungsschutzschalter C6, 3-polig |
| `c10` | C | 10 A | `MCB-3P-C10` | Leitungsschutzschalter C10, 3-polig |
| `c13` | C | 13 A | `MCB-3P-C13` | Leitungsschutzschalter C13, 3-polig |
| `c16` | C | 16 A | `MCB-3P-C16` | Leitungsschutzschalter C16, 3-polig |
| `c20` | C | 20 A | `MCB-3P-C20` | Leitungsschutzschalter C20, 3-polig |
| `c25` | C | 25 A | `MCB-3P-C25` | Leitungsschutzschalter C25, 3-polig |
| `c32` | C | 32 A | `MCB-3P-C32` | Leitungsschutzschalter C32, 3-polig |
| `c40` | C | 40 A | `MCB-3P-C40` | Leitungsschutzschalter C40, 3-polig |
| `c50` | C | 50 A | `MCB-3P-C50` | Leitungsschutzschalter C50, 3-polig |
| `c63` | C | 63 A | `MCB-3P-C63` | Leitungsschutzschalter C63, 3-polig |
| `c80` | C | 80 A | `MCB-3P-C80` | Leitungsschutzschalter C80, 3-polig |
| `c125` | C | 125 A | `MCB-3P-C125` | Leitungsschutzschalter C125, 3-polig |
| `d2` | D | 2 A | `MCB-3P-D2` | Leitungsschutzschalter D2, 3-polig |
| `d4` | D | 4 A | `MCB-3P-D4` | Leitungsschutzschalter D4, 3-polig |
| `d6` | D | 6 A | `MCB-3P-D6` | Leitungsschutzschalter D6, 3-polig |
| `d10` | D | 10 A | `MCB-3P-D10` | Leitungsschutzschalter D10, 3-polig |
| `d13` | D | 13 A | `MCB-3P-D13` | Leitungsschutzschalter D13, 3-polig |
| `d16` | D | 16 A | `MCB-3P-D16` | Leitungsschutzschalter D16, 3-polig |
| `d20` | D | 20 A | `MCB-3P-D20` | Leitungsschutzschalter D20, 3-polig |
| `d25` | D | 25 A | `MCB-3P-D25` | Leitungsschutzschalter D25, 3-polig |
| `d32` | D | 32 A | `MCB-3P-D32` | Leitungsschutzschalter D32, 3-polig |
| `d40` | D | 40 A | `MCB-3P-D40` | Leitungsschutzschalter D40, 3-polig |
| `d50` | D | 50 A | `MCB-3P-D50` | Leitungsschutzschalter D50, 3-polig |
| `d63` | D | 63 A | `MCB-3P-D63` | Leitungsschutzschalter D63, 3-polig |
| `d80` | D | 80 A | `MCB-3P-D80` | Leitungsschutzschalter D80, 3-polig |
| `d125` | D | 125 A | `MCB-3P-D125` | Leitungsschutzschalter D125, 3-polig |

Englische Anzeigenamen folgen dem Schema `Miniature Circuit Breaker <Kennlinie><Nennstrom>, 3-pole`; das technische Kürzel bleibt `MCB`.

## Qualitätsnachweis

Vor Freigabe müssen mindestens vollständige Pytest-Suite, `ZSYM-001` bis `ZSYM-006`, KiCad-Bibliotheksvalidator, Geräteserien-Generator, Gerätekatalogvalidierung sowie die generierten Referenzen und Symbolvorschauen erfolgreich sein. 1P- und 3P-Geometrie dürfen in den SVG-Vorschauen nicht vermischt werden.
