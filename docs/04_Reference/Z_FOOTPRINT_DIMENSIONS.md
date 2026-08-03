# Z_-Footprintmaße

KiCad ist der Standard. Projektspezifische Referenzmaße und Prüfregeln werden mit `Z_` beziehungsweise `ZFP-` gekennzeichnet.

## Referenz: DIN-Modul 18 mm

| Merkmal | Sollwert |
|---|---:|
| Courtyard-Breite | 18,00 mm |
| Courtyard-Höhe | 90,00 mm |
| Courtyard-Linienbreite | 0,05 mm |
| Courtyard-Layer | `F.CrtYd` |
| Ursprung | geometrische Mitte |

Die Referenzkontur reicht damit von `x=-9 mm` bis `x=+9 mm` und von `y=-45 mm` bis `y=+45 mm`.

## Freigaberegel

Ein Footprint ist im Release-Profil nicht freigabefähig, wenn die Courtyard-Kontur fehlt, nicht geschlossen ausgewertet werden kann oder von den dokumentierten Referenzwerten abweicht.
