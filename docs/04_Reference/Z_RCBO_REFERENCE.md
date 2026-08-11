# Z_RCBO 1P+N – Referenz

## Zweck

`Z_RCBO_1P_N:RCBO_1P_N` ist der herstellerneutrale Referenzbaustein für einen FI/LS-Schalter (RCBO) mit einem geschützten Außenleiter und mitgeschaltetem Neutralleiter.

Das Symbol verbindet die im Projekt bereits etablierte Darstellungslogik für Leitungsschutz und Fehlerstromschutz. Es ersetzt keine Produktauswahl, keine Schutzbemessung und keine Prüfung einer realen Anlage.

## Bibliotheken

Kanonisches Gerätesymbol:

```text
symbols/Z_RCBO_1P_N.kicad_sym
Z_RCBO_1P_N:RCBO_1P_N
```

Die bereits vorhandene Bibliothek `symbols/Z_RCBO.kicad_sym` bleibt als separater Platzhalter unangetastet. `Z_RCBO_Busbar_1P_N:RCBO_Busbar_1P_N` bleibt ein eigenständiges Hilfssymbol für Verbindungsschienen und ist nicht Bestandteil der RCBO-Gerätefunktion.

## Funktionsdarstellung

Das 1P+N-Symbol enthält:

- zwei mechanisch gekoppelte Hauptkontakte für L und N;
- vier Anschlüsse `1`, `2`, `3`, `4` mit N-Kennzeichnung an `3` und `4`;
- Prüfschaltung mit Kennzeichnung `T`;
- Summenstromerfassung über Außen- und Neutralleiter;
- gemeinsame Auslöse-/Betätigungseinheit;
- sichtbare Kennzeichnung `I>` für Überstromauslösung;
- sichtbare Kennzeichnung `IΔ` für Fehlerstromauslösung.

Die Darstellung ist eine herstellerneutrale Funktionsdarstellung. Sie soll die kombinierte MCB-/RCD-Funktion im Schaltplan lesbar machen und ist keine Wiedergabe eines konkreten inneren Hersteller-Schaltplans.

## Referenzdaten des Symbols

Die im Bibliothekssymbol hinterlegten `Z_`-Eigenschaften bilden eine repräsentative Planungsvariante ab:

| Merkmal | Referenzwert |
|---|---:|
| Schaltung | 1P+N |
| Pole | 2 |
| geschützte Pole | 1 |
| Bemessungsstrom | 16 A |
| Kennlinie | B |
| Bemessungsdifferenzstrom | 30 mA |
| RCD-Typ | A |
| Bemessungsausschaltvermögen | 6 kA |
| Prüftaste | vorhanden |
| Footprint Policy | optional |

## Typ-A-Basisserie

Quelle:

```text
data/device_series/generic/rcbo-1p-n-type-a-template-series.yaml
```

Die Serie erzeugt 14 herstellerneutrale Planungsvarianten aus:

- Bemessungsstrom: 6 A, 10 A, 16 A, 20 A, 25 A, 32 A, 40 A;
- Kennlinie: B, C;
- Bemessungsdifferenzstrom: 30 mA;
- RCD-Typ: A;
- Bemessungsausschaltvermögen: 6 kA.

Die Varianten werden unter

```text
data/devices/generated/generic.rcbo-1p-n-type-a-template-series/
```

erzeugt.

## Typ-F-Zusatzserie

Quelle:

```text
data/device_series/generic/rcbo-1p-n-type-f-template-series.yaml
```

Für Typ F wird bewusst keine vollständige theoretische Matrix erzeugt. Die erste konservative Serie enthält nur die aktuell explizit belegten Planungsvarianten:

- 6 A, Kennlinie C, 30 mA, 6 kA;
- 16 A, Kennlinie C, 30 mA, 6 kA.

Weitere Typ-F-Kombinationen werden erst ergänzt, wenn sie mit Primärquellen sauber belegt und für den Projektumfang sinnvoll sind.

## Evidenzbasis

Aktuelle Siemens-Produktdaten belegen 1P+N-RCBOs unter anderem mit folgenden Kenngrößen:

- Typ A, 30 mA, 6 kA, Kennlinie B/C und Bemessungsströmen bis 40 A;
- Typ F, 30 mA, 6 kA, 1P+N, Kennlinie C.

Primärquellen, Beispiele:

- https://mall.industry.siemens.com/mall/en/de/Catalog/Product/5SU1356-6KK20
- https://mall.industry.siemens.com/mall/en/de/Catalog/Product/5SU1356-7KK20
- https://mall.industry.siemens.com/mall/de/de/Catalog/Product/5SU1356-7KK32
- https://mall.industry.siemens.com/mall/tr/tr/Catalog/Product/5SU1356-7KK40
- https://mall.industry.siemens.com/mall/NO/NO/Catalog/Product/?mlfb=5SU1356-6KK40-ZW02
- https://mall.industry.siemens.com/mall/en/us/Catalog/Product/5SV13164KK06
- https://ausschreibungstexte.siemens.com/tiplv/Data/E/Electrical_Distribution%2C/Low-Voltage_Components__Protection%2C_/R/R/Type_F/_DPMD_ABJ175_001_000_%2C__DPMD_AAA811_001_000_%2C_type__DPMD_AAA040_001_000_%2C__DPMD_ACC471_001_000_%2C__DPMD_AAA359_001_000_%2C__DPMD_AAA478_001_000_%2C__DPMD_AAB580_001_000%2CB_%2C__DPMD/%28LV_Q88VVKF5KJ2MKF1AZAAN09K69M_5SV13164KK16%29

Diese Quellen dienen als technische Evidenz für die Geräteklasse und die verwendeten Planungswerte. Die generischen Varianten sind keine Behauptung, dass jede Kombination bei jedem Hersteller oder in jeder Baureihe verfügbar ist.

## Modulbreite und Footprint

Im bestehenden DIN-Verteilerplaner ist `RCBO_1P_N` mit 2 TE als konservativem Planungswert hinterlegt. Am Markt existieren auch kompaktere 1-TE-Geräte. Deshalb gilt:

- `modules: 2` ist ein herstellerneutraler Platzbedarf für die Projektplanung;
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
