# Z_RCD-Referenz

## Zweck

`Z_RCD:RCD` ist der herstellerneutrale Referenzbaustein für einen Fehlerstrom-Schutzschalter im Projekt.

KiCad bleibt der Standard. Projektspezifische Eigenschaften sind deshalb konsequent mit `Z_` gekennzeichnet.

## Referenzdaten

| Merkmal | Wert |
|---|---:|
| Polzahl | 2 |
| Bemessungsstrom | 40 A |
| Bemessungsdifferenzstrom | 30 mA |
| RCD-Typ | A |
| Prüftaste | vorhanden |
| Footprint Policy | optional |
| Empfohlener Footprint | `Z_DIN_Module_36mm:Z_DIN_Module_36mm` |

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
