# AP-0116 – MCB 1P Goldstandard und Pinvertrag

## Ziel

Für den einpoligen Leitungsschutzschalter wird vor jeder weiteren Symboländerung ein verbindlicher fachlicher, grafischer und elektrischer Vertrag festgelegt. Der MCB 1P wird damit zur Referenz für spätere Schutzgerätevarianten.

## Geltungsbereich

Dieses Arbeitspaket definiert ausschließlich den herstellerneutralen MCB 1P. Herstellerdaten, konkrete Artikelnummern, weitere Polzahlen und RCCB/RCBO bleiben außerhalb dieses Arbeitspakets.

## Fachlicher Vertrag

Der MCB 1P bildet genau einen geschützten aktiven Leiter ab.

- Gerätefamilie: `MCB`
- Polzahl: `1P`
- Referenzpräfix in KiCad: `Q`
- Strompfade: genau 1
- elektrische Anschlüsse: genau 2
- Neutralleiteranschluss: keiner
- Schutzleiteranschluss: keiner
- Herstellerbezug: keiner
- Footprint-Policy: `optional`

Nennstrom, Auslösecharakteristik, Bemessungsspannung und Ausschaltvermögen sind Geräte- bzw. Variantendaten und dürfen nicht durch die reine Symbolgeometrie fest verdrahtet werden.

## Pinvertrag

Der verbindliche KiCad-Pinvertrag für `Z_MCB:MCB` lautet:

| Pin | Bedeutung | Elektrischer Typ | Pflicht |
|---|---|---|---|
| `1` | erster Anschluss des geschützten Strompfads | `passive` | ja |
| `2` | zweiter Anschluss des geschützten Strompfads | `passive` | ja |

Die Pins `1` und `2` beschreiben die beiden Enden desselben einpoligen Strompfads. Die Symboldefinition erzwingt keine herstellerspezifische Einspeiserichtung. Eine konkrete obere/untere Einspeisung ist nur dann zulässig, wenn sie durch Produktdaten oder eine projektspezifische Regel ausdrücklich festgelegt wird.

Für das herstellerneutrale Referenzsymbol bleiben beide Pins deshalb elektrisch `passive`.

## Grafischer Goldstandard

Die bisherige reine Rechteckdarstellung ist technisch prüfbar, aber als fachlicher Goldstandard nicht ausreichend eindeutig. Das Referenzsymbol muss einen erkennbaren einpoligen Schalt-/Schutzgerätepfad darstellen.

Verbindliche Anforderungen:

1. genau zwei Anschluss-Pins,
2. eindeutiger durchgehender fachlicher Bezug zwischen Pin 1 und Pin 2,
3. sichtbares Schalt-/Schutzgerätemerkmal innerhalb der Symbolgrafik,
4. keine herstellerspezifischen Logos oder Bauformen,
5. keine fest eingebrannten Werte wie `B16`,
6. KiCad-Raster, Pinlänge, Linienbreite und Textgrößen bleiben mit den bestehenden `ZSYM-*`-Regeln konform,
7. Referenz `Q` und Wert `MCB` bleiben außerhalb der Funktionsgrafik lesbar,
8. die Grafik muss in der SVG-Vorschau und im realen KiCad-Schaltplan eindeutig erkennbar bleiben.

Die konkrete Geometrie wird im Folgearbeitspaket umgesetzt und anschließend durch Vorschau und KiCad-Praxisprüfung validiert.

## Qualitätsstatus

Für Sprint 006 gilt eine eindeutige Statusfolge:

`Entwurf` → `Geprüft` → `Praxisgetestet`

### Entwurf

Der Status gilt, solange mindestens ein Goldstandard-Kriterium noch nicht nachgewiesen ist.

### Geprüft

`Geprüft` darf erst vergeben werden, wenn mindestens folgende Nachweise vorliegen:

- Symbol entspricht dem fachlichen und grafischen Vertrag,
- Pinvertrag ist automatisiert geprüft,
- Z_-Qualitätsregeln sind vollständig erfüllt,
- SVG-Vorschau ist aktualisiert,
- Dokumentation und Katalog sind konsistent,
- Referenzprojekt enthält das Symbol tatsächlich.

### Praxisgetestet

`Praxisgetestet` darf erst vergeben werden, wenn zusätzlich dokumentiert ist:

- Projekt wurde in KiCad geöffnet,
- Symbol wurde real im Referenzschaltplan verwendet,
- ERC wurde ausgeführt,
- das Ergebnis der Praxisprüfung ist nachvollziehbar dokumentiert.

Damit wird die in AP-0115 erkannte Statusabweichung aufgelöst: Das vorhandene Referenzprojekt bleibt bis zum Nachweis der Goldstandard-Kriterien `Entwurf`.

## Ableitungsregel für spätere Varianten

Weitere MCB-Varianten dürfen erst nach Abschluss des 1P-Goldstandards abgeleitet werden. Sie übernehmen dessen Grundregeln und erweitern ausschließlich die für ihre Polzahl erforderlichen Strompfade und Anschlüsse.

Insbesondere dürfen `1P+N`, `2P`, `3P`, `3P+N` und `4P` nicht durch Kopieren ungeprüfter Zwischenstände entstehen.

## Definition of Done

- fachlicher Vertrag für MCB 1P ist festgelegt,
- Pinvertrag `1`/`2` ist verbindlich dokumentiert,
- beide Pins bleiben im herstellerneutralen Symbol `passive`,
- grafische Mindestanforderungen sind festgelegt,
- Statusfolge `Entwurf → Geprüft → Praxisgetestet` ist eindeutig definiert,
- Ableitungsregel für spätere MCB-Varianten ist festgelegt,
- die konkrete Symboländerung ist bewusst in das Folgearbeitspaket verschoben.
