# Z_RCBO 1P+N / 2P – Referenz

## Zweck

`Z_RCBO_1P_N:RCBO_1P_N` ist der herstellerneutrale Referenzbaustein für einen FI/LS-Schalter (RCBO) mit zwei geschalteten Polen. In der Projektbezeichnung werden **1P+N** und **2P** für diese Bauart gemeinsam geführt.

Die elektrische Semantik bleibt unverändert: ein geschützter Außenleiter plus mitgeschalteter Neutralleiter. Es wird **kein zweites 2P-Symbol** erzeugt.

Das Symbol verbindet Leitungsschutz- und Fehlerstromschutzfunktion in einer gemeinsamen Funktionsdarstellung. Es ersetzt keine Produktauswahl, keine Schutzbemessung und keine Prüfung einer realen Anlage.

## Bibliotheken

Kanonisches Gerätesymbol:

```text
symbols/Z_RCBO_1P_N.kicad_sym
Z_RCBO_1P_N:RCBO_1P_N
```

Die bereits vorhandene Bibliothek `symbols/Z_RCBO.kicad_sym` bleibt als separater Platzhalter unangetastet. `Z_RCBO_Busbar_1P_N:RCBO_Busbar_1P_N` bleibt ein eigenständiges Hilfssymbol für Verbindungsschienen und ist nicht Bestandteil der RCBO-Gerätefunktion.

## Freigegebene Symbolgeometrie

Die Referenzdarstellung wurde am 14.08.2026 visuell abgestimmt und anschließend als neue Basis für `Z_RCBO_1P_N:RCBO_1P_N` übernommen.

Die freigegebene Darstellung enthält:

- Anschlusskennzeichnung **`1`, `3 N`, `2`, `4 N`**;
- zwei mechanisch gekoppelte Hauptkontakte für L und N;
- Überstromauslöser im L-Zweig;
- Test-/Prüfkreis links mit Kennzeichnung `T` und `E`;
- Summenstromwandler um L und N mit zwei dargestellten Kernbereichen;
- gestrichelte mechanische Kopplung;
- oberen Betätigungs-/Fehlerstromblock rechts;
- unteren Auslöse-/Betätigungsblock rechts;
- elektrische Rückführung des unteren rechten Kreises zum Leiter von **Klemme 4 / N**.

Bei der visuellen Abstimmung wurden ausdrücklich drei Details korrigiert:

1. Der Draht links oben endet **vor** der gestrichelten mechanischen Kopplungslinie.
2. Die Proportionen der Betätigungs-/Auslöseblöcke rechts wurden an die Referenz angepasst.
3. Die untere rechte Leitung ist mit dem Leiter des Schaltkontakts **Klemme 4 / N** verbunden.

Die Darstellung ist eine herstellerneutrale Funktionsdarstellung und keine Wiedergabe eines konkreten inneren Hersteller-Schaltplans.

## Referenzdaten des Symbols

Die im Bibliothekssymbol hinterlegten `Z_`-Eigenschaften bilden weiterhin eine repräsentative Planungsvariante ab:

| Merkmal | Referenzwert |
|---|---:|
| Projektbezeichnung | 1P+N / 2P |
| Pole | 2 |
| geschützte Pole | 1 |
| Bemessungsstrom | 16 A |
| Kennlinie | B |
| Bemessungsdifferenzstrom | 30 mA |
| RCD-Typ | A |
| Bemessungsausschaltvermögen | 6 kA |
| Prüftaste | vorhanden |
| Footprint Policy | optional |

## Typ-A-Planungsmatrix

Quelle:

```text
data/device_series/generic/rcbo-1p-n-type-a-template-series.yaml
```

Die Serie enthält **64 herstellerneutrale Planungsvarianten**:

- Bemessungsstrom: **6 A, 10 A, 13 A, 16 A, 20 A, 25 A, 32 A, 40 A**;
- Bemessungsdifferenzstrom: **10 mA, 30 mA**;
- Auslösecharakteristik: **B, C**;
- Bemessungsausschaltvermögen: **6 kA, 10 kA**;
- RCD-Charakteristik: **Typ A**;
- Bauart/Projektbezeichnung: **1P+N / 2P**.

Rechnung:

```text
8 Nennströme × 2 Fehlerströme × 2 Kennlinien × 2 Ausschaltvermögen = 64 Varianten
```

Die bereits vorhandenen Basis-IDs für 30 mA / 6 kA (`b6`, `b10`, `b16`, …, `c40`) bleiben erhalten. Dadurch werden bestehende Katalogreferenzen nicht unnötig gebrochen. Neue Kombinationen tragen Fehlerstrom und Ausschaltvermögen im Varianten-Identifier.

Die Varianten werden unter

```text
data/devices/generated/generic.rcbo-1p-n-type-a-template-series/
```

erzeugt.

### Einordnung der Matrix

Die 64 Kombinationen sind eine **herstellerneutrale Planungsabdeckung nach Projektvorgabe**. Sie sind nicht als Behauptung zu verstehen, dass jede Kombination bei jedem Hersteller oder in jeder Produktserie lieferbar ist.

Vor einer konkreten Produktauswahl müssen insbesondere Nennstrom, Kennlinie, Bemessungsdifferenzstrom, Ausschaltvermögen, Polschaltung, Klemmenbelegung und Modulbreite am realen Gerät geprüft werden.

## Typ-F-Zusatzserie

Quelle:

```text
data/device_series/generic/rcbo-1p-n-type-f-template-series.yaml
```

Typ F bleibt bewusst separat und konservativ. Die bestehende Serie enthält weiterhin nur:

- 6 A, Kennlinie C, 30 mA, 6 kA;
- 16 A, Kennlinie C, 30 mA, 6 kA.

Die neue 64er Matrix gilt **nur für Typ A**.

## Bisherige Evidenzbasis

Die bereits dokumentierten Siemens-Produktdaten belegen für die Geräteklasse unter anderem Typ-A-RCBOs mit 30 mA, 6 kA, Kennlinie B/C und Bemessungsströmen bis 40 A sowie einzelne Typ-F-Geräte. Diese Evidenz deckt **nicht automatisch die vollständige neue 64er Planungsmatrix** ab.

Primärquellen aus dem bisherigen Paket:

- https://mall.industry.siemens.com/mall/en/de/Catalog/Product/5SU1356-6KK20
- https://mall.industry.siemens.com/mall/en/de/Catalog/Product/5SU1356-7KK20
- https://mall.industry.siemens.com/mall/de/de/Catalog/Product/5SU1356-7KK32
- https://mall.industry.siemens.com/mall/tr/tr/Catalog/Product/5SU1356-7KK40
- https://mall.industry.siemens.com/mall/NO/NO/Catalog/Product/?mlfb=5SU1356-6KK40-ZW02
- https://mall.industry.siemens.com/mall/en/us/Catalog/Product/5SV13164KK06

## Modulbreite und Footprint

Im bestehenden DIN-Verteilerplaner ist `RCBO_1P_N` mit 2 TE als konservativem Planungswert hinterlegt. Am Markt existieren auch kompaktere Geräte. Deshalb gilt:

- `modules: 2` ist ein herstellerneutraler Planungswert;
- `Z_Footprint_Policy = optional`;
- vor einer konkreten mechanischen Konstruktion muss das ausgewählte Produktdatenblatt geprüft werden;
- aus dem generischen Katalogwert darf keine Fertigungs- oder Platzierungsfreigabe abgeleitet werden.

## Anschlüsse

| Pin | Bedeutung |
|---|---|
| 1 | Eingang L |
| 2 | Ausgang L |
| 3 | Eingang N |
| 4 | Ausgang N |

## Verbindungsschiene

Das vorhandene Symbol

```text
Z_RCBO_Busbar_1P_N:RCBO_Busbar_1P_N
```

beschreibt nur eine logische L/N-Verbindungsschiene für RCBO-Gruppen. Die reale Kompatibilität von Phasenschiene, Neutralleiterführung, Klemmenposition und Teilung muss immer gegen die konkret ausgewählten Geräte geprüft werden.

## Qualitätsziel

Mit Symbol, Gerätedaten, Referenzdokumentation und automatisierten Tests kann das RCBO-Paket den Reifegrad `Geprüft` erreichen. `Praxisgetestet` bleibt einem dokumentierten KiCad-Beispiel mit realer Platzierung und Prüfung vorbehalten.
