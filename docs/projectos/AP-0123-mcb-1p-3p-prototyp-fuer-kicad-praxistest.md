# AP-0123 – MCB 1P/3P Prototyp für KiCad-Praxistest

## Ziel

Für den praktischen KiCad-Test werden ein einpoliger und ein dreipoliger Leitungsschutzschalter als zusammenhängender ProjectOS-Prototyp aus Symbol, Footprint und herstellerneutralem 3D-Modell bereitgestellt.

## Gemeinsame Geometrie

- Modulraster: `18 mm`
- MCB-Länge in Draufsicht inklusive neutral abstrahierter Schraubklemmen: `84 mm`
- Anschlusszone der Platine: je `10 mm` an beiden Stirnseiten
- Platinenlänge: `104 mm`
- Bohrung: `Ø 4 mm`
- Lötpad: `Ø 6 mm`
- Padmitten liegen jeweils mittig in der 10-mm-Anschlusszone, also bei `Y = ±47 mm`.
- Mehrpolige Varianten verwenden dasselbe feste 18-mm-Raster.

## MCB 1P

- Platinen-/Footprint-Abmessung: `104 x 18 mm`
- Pads: `2`
- Padpositionen: `(0,-47)` und `(0,+47)`
- Symbol: `Z_MCB:MCB`
- Footprint: `Z_MCB:Z_MCB_1P_18mm`
- 3D-Modell: `Z_MCB_1P`

## MCB 3P

- Platinen-/Footprint-Abmessung: `104 x 54 mm`
- entspricht drei 18-mm-Modulen nebeneinander
- Pads: `6`
- X-Raster: `-18 / 0 / +18 mm`
- Y-Positionen: `-47 / +47 mm`
- Symbol-Pins: `1/2`, `3/4`, `5/6`
- Symbol: `Z_MCB:MCB_3P`
- Footprint: `Z_MCB:Z_MCB_3P_54mm`
- 3D-Modell: `Z_MCB_3P`

## 3D-Koordinatenvertrag

Die gemeinsame OpenSCAD-Geometrie ist direkt auf das PCB-Koordinatensystem ausgerichtet:

- `X` = Modulbreite,
- `Y` = Gerätelänge in Draufsicht,
- `Z` = Höhe über der Platine,
- Ursprung = geometrische Mitte der MCB-Draufsicht auf der PCB-Ebene.

Damit sollen KiCad-Modelle mit `scale 1/1/1`, `rotate 0/0/0` und `offset 0/0/0` verwendbar sein.

## Sammelschienen-Regel

Das 18-mm-Padraster ist die verbindliche generische ProjectOS-Basis. Konkrete Hersteller-Sammelschienen können geometrisch abweichen; für den Prototyp ist entscheidend, dass die elektrischen Padachsen der einzelnen Pole sauber im 18-mm-Raster übereinanderliegen. Konkrete Schienen werden später als Praxis-/Kompatibilitätsprofile validiert.

## Lokaler Export

Unter Windows erzeugt

```text
tools\windows\export_z_mcb_family_3d.bat
```

für 1P und 3P jeweils STEP und WRL und führt zuvor eine Maßhaltigkeitsprüfung durch.

## Status

`bereit für lokalen KiCad-Praxistest – endgültige Freigabe nach Sichtprüfung von 1P und 3P sowie späterem Sammelschienen-Test`
