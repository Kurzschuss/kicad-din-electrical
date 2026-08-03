# Z_-Symbolmaße

Diese Referenz konkretisiert die verbindliche Symbolrichtlinie für projektspezifische `Z_`-Symbole. KiCad bleibt der technische Standard; die nachfolgenden Werte sind die dokumentierten Projektvorgaben für eigene Erweiterungen.

| Merkmal | Standardwert | Zulässige Abweichung |
|---|---:|---|
| Anschlussraster | 100 mil | nur mit dokumentierter `Z_`-Regel oder Ausnahme |
| Unterraster für grafische Details | 50 mil | keine Pins oder Anschlussgeometrie |
| Pinlänge | 100 mil | klassenspezifisch dokumentierbar |
| Pinabstand | 100 mil oder Vielfaches | nur bei fachlicher Notwendigkeit |
| Linienbreite | 10 mil | klassenspezifisch dokumentierbar |
| Textgröße | 50 mil | größere Werte für Überschriften zulässig |

## Referenzbreiten

Die Breite wird an der elektrischen Funktion und Lesbarkeit ausgerichtet. Für das MCB-Referenzpaket gelten zunächst folgende Zielwerte:

| Variante | Zielbreite |
|---|---:|
| 1P | 400 mil |
| 1P+N | 600 mil |
| 3P | 800 mil |
| 3P+N | 1000 mil |

Diese Breiten sind `Z_`-Projektwerte und keine umdefinierten offiziellen KiCad-Vorgaben. Abweichungen benötigen eine eigene Regel-ID oder eine versionierte Ausnahme.

## Maschinenlesbare Zuordnung

- `ZSYM-003`: Anschlussraster
- `ZSYM-004`: Pinlänge
- `ZSYM-005`: Linienbreite
- `ZSYM-006`: Textgröße

Das MCB-Paket aus Issue #87 dient als erster praktischer Nachweis dieser Werte.
