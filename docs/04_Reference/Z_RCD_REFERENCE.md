# Z_RCD-Referenz

## Zweck

`Z_RCD:RCD` ist der herstellerneutrale Referenzbaustein für einen 2-poligen Fehlerstrom-Schutzschalter (RCD/FI) im Projekt.

KiCad bleibt der Standard. Projektspezifische Eigenschaften sind deshalb konsequent mit `Z_` gekennzeichnet.

Die elektrische Symbolgeometrie bildet die gemeinsame Funktion der Gerätefamilie ab. Die konkreten Bemessungswerte der einzelnen Gerätevarianten liegen datengetrieben im Gerätekatalog.

## Symbolgeometrie

Die Funktionsdarstellung enthält:

- zwei mechanisch gekoppelte Schaltkontakte für L und N;
- Prüfschaltung mit Kennzeichnung `T`;
- Summenstromerfassung über beide aktiven Leiter;
- Auslöse-/Bewertungsblock `IΔ >`;
- mechanisch gekoppelte Prüftaste;
- vertikale Anschlussführung mit `1/2` für L und `3/4` für N.

Die Darstellung orientiert sich an der im Projekt freigegebenen FI/RCD-Vorlage und bleibt herstellerneutral.

## Referenzdaten des Symbols

Die im Bibliothekssymbol hinterlegten Z_-Eigenschaften bilden weiterhin eine repräsentative Referenzvariante ab:

| Merkmal | Wert |
|---|---:|
| Polzahl | 2 |
| Bemessungsstrom | 40 A |
| Bemessungsdifferenzstrom | 30 mA |
| RCD-Typ | A |
| Bemessungskurzschlussstrom | 6 kA |
| Schließ- und Abschaltvermögen | 1,5 kA |
| Prüftaste | vorhanden |
| Footprint Policy | optional |
| Empfohlener Footprint | `Z_DIN_Module_36mm:Z_DIN_Module_36mm` |

## Gerätefamilie

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

## Anschlüsse

| Pin | Bedeutung |
|---|---|
| 1 | Eingang L |
| 2 | Ausgang L |
| 3 | Eingang N |
| 4 | Ausgang N |

## DIN-Footprintkonzept

Die herstellerneutrale Referenz verwendet eine mechanische 2-TE-Hüllkontur mit 36 mm Breite und 90 mm Höhe. Der Footprint ist als `board_only` gekennzeichnet, besitzt keine elektrischen Pads und dient ausschließlich der Platzierungs-, Gehäuse- und Dokumentationsansicht.

Die Konturen liegen auf:

- `F.Fab`: nominelle Gerätehülle 36 × 90 mm,
- `F.CrtYd`: geschlossene 36 × 90-mm-Belegungsfläche mit 0,05 mm Linienbreite.

Die Footprint Policy bleibt `optional`, da reale RCD-Abmessungen, Klemmenlagen und Einbautiefen vom Hersteller und Gerätetyp abhängen. Vor einer konkreten Konstruktion muss der Footprint deshalb gegen das Datenblatt des ausgewählten Geräts geprüft oder ersetzt werden.

## Reproduzierbares KiCad-Referenzprojekt

Unter `examples/Z_RCD_Reference/` liegt ein eigenständiges Beispielprojekt mit:

- platziertem `Z_RCD:RCD` als `Q1`,
- zugeordnetem Footprint `Z_DIN_Module_36mm:Z_DIN_Module_36mm`,
- projektlokalen Bibliothekstabellen auf Basis der `KICAD_Z_*`-Variablen,
- dokumentiertem Ablauf für die reale ERC-Prüfung.

Die vier externen Anschlüsse sind absichtlich als offen markiert. Dadurch bleibt das Beispiel elektrisch neutral und kann nach der automatischen Bibliothekseinrichtung unmittelbar in KiCad geöffnet werden.

## Abgrenzung

Das Symbol beschreibt die elektrische Funktion im Schaltplan. Es ersetzt keine Auswahl nach nationalen Installationsregeln, keine Bemessung und keine Prüfung einer realen Anlage.

Der generische Footprint ist keine Bohr-, Anschluss- oder Fertigungsfreigabe für ein konkretes RCD.

## Qualitätsstatus

Der maschinell prüfbare Paketstand ist `Geprüft`. `Praxisgetestet` wird erst nach realer Platzierung in KiCad und dokumentiertem ERC vergeben.
