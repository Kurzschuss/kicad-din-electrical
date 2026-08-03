# Z_MCB Qualitätsstatus

## Referenzpaket

- Bibliothek: `Z_MCB`
- Symbol: `Z_MCB:MCB`
- Quelle: `symbols/Z_MCB.kicad_sym`
- Footprint Policy: `optional`
- Projektstatus: `z_conform`

## Regelbefunde

| Regel-ID | Prüfung | Ergebnis |
|---|---|---|
| `ZSYM-001` | Projektkennung `Z_` | `z_conform` |
| `ZSYM-002` | explizite `Z_Footprint_Policy` | `z_conform` |
| `ZSYM-003` | Anschlussraster 100 mil | `z_conform` |
| `ZSYM-004` | Pinlänge 100 mil | `z_conform` |
| `ZSYM-005` | Linienbreite 10 mil | `z_conform` |
| `ZSYM-006` | Primärtextgröße 50 mil | `z_conform` |

## Einordnung

Das Referenzsymbol folgt den dokumentierten `Z_`-Projektregeln. KiCad bleibt der technische Standard; die zusätzliche Eigenschaft `Z_Footprint_Policy` ist ausdrücklich als projektspezifische `Z_`-Erweiterung gekennzeichnet.

Der Status bezieht sich auf den derzeit implementierten Regelsatz. Weitere Regeln können zusätzliche Prüfungen ergänzen, ohne bestehende Ergebnisse zu verbergen.
