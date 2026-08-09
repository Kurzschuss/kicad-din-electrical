# Z_MCB – versionierte 3P-Breitenabweichung

Version: 1

## Geltungsbereich

Diese Ausnahme gilt ausschließlich für das Symbol `Z_MCB:MCB_3P`.

## Abweichung

`docs/04_Reference/Z_SYMBOL_DIMENSIONS.md` nennt für 3P-MCB zunächst eine Zielbreite von **800 mil**. Für `Z_MCB:MCB_3P` wird ab dieser Version eine geometrische Breite von **1000 mil** verwendet.

## Begründung

Die freigegebene Referenzdarstellung verlangt gleichzeitig:

- den vollständigen linken Betätigungs-/Auslöseweg des 1P-Goldstandards,
- drei gleichartige Schaltpole,
- einen Polabstand von 300 mil,
- je einen schrägen Auslösepfeil pro Pol,
- genau einen kurzen mechanischen Kopplungsstrich zwischen benachbarten Polen.

Mit 800 mil Gesamtbreite müsste entweder der linke Betätigungsweg verkürzt oder der Polabstand gegenüber der Referenz zusammengedrückt werden. Beides verschlechtert die Lesbarkeit und weicht von der freigegebenen Darstellung ab. Die 1000-mil-Ausnahme bewahrt deshalb die 1P-Geometrie unverändert und ergänzt zwei weitere Pole im 300-mil-Raster.

## Unveränderte Regeln

Die Ausnahme ändert keine globalen Z_-Regeln. Weiterhin gelten insbesondere:

- Anschlussraster: 100 mil,
- Pinlänge: 100 mil,
- Linienbreite: 10 mil,
- Primärtext: 50 mil,
- Anschlussnummern: 1/2, 3/4, 5/6,
- elektrische Pins: `passive`,
- Stromflussdarstellung: oben nach unten.

Die 1P-Referenzbreite von 400 mil bleibt unverändert.
