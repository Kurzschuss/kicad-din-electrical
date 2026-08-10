# Z_RCD-Referenz

## Zweck

`Z_RCD:RCD` ist der herstellerneutrale Referenzbaustein für einen 2-poligen Fehlerstrom-Schutzschalter (RCD/FI) im Projekt.

`Z_RCD:RCD_4P` ergänzt die Bibliothek um einen 3+N-/4-poligen Fehlerstrom-Schutzschalter nach der im Projekt freigegebenen 4P-Vorlage.

KiCad bleibt der Standard. Projektspezifische Eigenschaften sind deshalb konsequent mit `Z_` gekennzeichnet.

Die elektrische Symbolgeometrie bildet die gemeinsame Funktion der Gerätefamilien ab. Die konkreten Bemessungswerte der einzelnen Gerätevarianten liegen datengetrieben im Gerätekatalog.

## Symbolgeometrie 2P

Die Funktionsdarstellung von `Z_RCD:RCD` enthält:

- zwei mechanisch gekoppelte Schaltkontakte für L und N;
- Prüfschaltung mit Kennzeichnung `T`;
- Summenstromerfassung über beide aktiven Leiter;
- Auslöse-/Bewertungsblock;
- mechanisch gekoppelte Prüftaste;
- vertikale Anschlussführung mit `1/2` für L und `3/4` für N.

Die Darstellung orientiert sich an der im Projekt freigegebenen FI/RCD-Vorlage und bleibt herstellerneutral.

## Symbolgeometrie 3+N / 4P

Die freigegebene Funktionsdarstellung von `Z_RCD:RCD_4P` enthält:

- vier mechanisch gekoppelte Schaltkontakte für L1, L2, L3 und N;
- Anschlusskennzeichnung oben `1`, `3`, `5`, `7/N` und unten `2`, `4`, `6`, `8/N`;
- Prüfschaltung mit den Kennzeichnungen `T` und `E`;
- Summenstromwandler über alle vier aktiven Leiter;
- gekoppelte Auslöse-/Betätigungseinheit rechts mit Kreuzsymbol;
- gestrichelte mechanische Kopplung über alle vier Hauptkontakte.

## Referenzdaten der Symbole

Die im Bibliothekssymbol hinterlegten Z_-Eigenschaften bilden repräsentative Referenzvarianten ab:

| Merkmal | `RCD` 2P | `RCD_4P` 3+N/4P |
|---|---:|---:|
| Polzahl | 2 | 4 |
| Bemessungsstrom | 40 A | 40 A |
| Bemessungsdifferenzstrom | 30 mA | 30 mA |
| RCD-Typ | A | A |
| Bemessungskurzschlussstrom | 6 kA | 6 kA |
| Schließ- und Abschaltvermögen | 1,5 kA | 1,5 kA |
| Prüftaste | vorhanden | vorhanden |
| Footprint Policy | optional | optional |
| Empfohlener Footprint | `Z_DIN_Module_36mm:Z_DIN_Module_36mm` | geräteabhängig |

## Gerätefamilie 2P

Die parametrische Serie liegt unter:

```text
data/device_series/generic/rcd-2p-template-series.yaml
```

Sie erzeugt 64 herstellerneutrale Gerätevarianten aus der vollständigen Kombination von:

- Bemessungsstrom: 16 A, 25 A, 40 A, 63 A;
- Bemessungsdifferenzstrom: 10 mA, 30 mA, 300 mA, 500 mA;
- RCD-Typ: A, F;
- Bemessungskurzschlussstrom: 6 kA, 10 kA.

Das Schließ- und Abschaltvermögen beträgt für alle Varianten 1,5 kA.

Die erzeugten Einzelgeräte verwenden gemeinsam `Z_RCD:RCD` und werden unter `data/devices/generated/generic.rcd-2p-template-series/` abgelegt.

## Gerätefamilie 3+N / 4P

Die parametrische Serie liegt unter:

```text
data/device_series/generic/rcd-4p-template-series.yaml
```

Sie erzeugt 72 herstellerneutrale Gerätevarianten aus der vollständigen Kombination von:

- Bemessungsstrom: 25 A, 40 A, 63 A, 125 A;
- Bemessungsdifferenzstrom: 30 mA, 300 mA, 500 mA;
- RCD-Typ: A, B, B+;
- Bemessungskurzschlussstrom: 6 kA, 10 kA.

Das Schließ- und Abschaltvermögen beträgt für alle Varianten 1,5 kA.

Die erzeugten Einzelgeräte verwenden gemeinsam `Z_RCD:RCD_4P` und werden unter `data/devices/generated/generic.rcd-4p-template-series/` abgelegt.

## Anschlüsse

### `Z_RCD:RCD`

| Pin | Bedeutung |
|---|---|
| 1 | Eingang L |
| 2 | Ausgang L |
| 3 | Eingang N |
| 4 | Ausgang N |

### `Z_RCD:RCD_4P`

| Pin | Bedeutung |
|---|---|
| 1 | Eingang L1 |
| 2 | Ausgang L1 |
| 3 | Eingang L2 |
| 4 | Ausgang L2 |
| 5 | Eingang L3 |
| 6 | Ausgang L3 |
| 7 | Eingang N |
| 8 | Ausgang N |

## DIN-Footprintkonzept

Die herstellerneutrale 2P-Referenz verwendet eine mechanische 2-TE-Hüllkontur mit 36 mm Breite und 90 mm Höhe. Der Footprint ist als `board_only` gekennzeichnet, besitzt keine elektrischen Pads und dient ausschließlich der Platzierungs-, Gehäuse- und Dokumentationsansicht.

Die 4P-Serie führt bewusst keinen festen Footprint als Pflichtangabe. Vierpolige RCDs können je nach Hersteller, Baureihe und Bemessungsstrom unterschiedliche mechanische Abmessungen besitzen; die Katalogserie kennzeichnet deshalb nur vier Module als herstellerneutrale Planungsangabe.

Die Footprint Policy bleibt `optional`. Vor einer konkreten Konstruktion muss der Footprint gegen das Datenblatt des ausgewählten Geräts geprüft oder ersetzt werden.

## Reproduzierbares KiCad-Referenzprojekt

Unter `examples/Z_RCD_Reference/` liegt das bestehende eigenständige 2P-Beispielprojekt mit:

- platziertem `Z_RCD:RCD` als `Q1`,
- zugeordnetem Footprint `Z_DIN_Module_36mm:Z_DIN_Module_36mm`,
- projektlokalen Bibliothekstabellen auf Basis der `KICAD_Z_*`-Variablen,
- dokumentiertem Ablauf für die reale ERC-Prüfung.

Die vier externen Anschlüsse sind absichtlich als offen markiert. Dadurch bleibt das Beispiel elektrisch neutral und kann nach der automatischen Bibliothekseinrichtung unmittelbar in KiCad geöffnet werden.

## Abgrenzung

Die Symbole beschreiben die elektrische Funktion im Schaltplan. Sie ersetzen keine Auswahl nach nationalen Installationsregeln, keine Bemessung und keine Prüfung einer realen Anlage.

Generische Footprint- oder Modulwerte sind keine Bohr-, Anschluss- oder Fertigungsfreigabe für ein konkretes RCD.

## Qualitätsstatus

Der maschinell prüfbare Paketstand ist `Geprüft`. `Praxisgetestet` wird erst nach realer Platzierung in KiCad und dokumentiertem ERC vergeben.
