# AP-0121 – Lokaler MCB-3D-Praxisnachweis

## Ziel

Der in AP-0119 vorbereitete Export und die in AP-0120 angelegte KiCad-3D-Bindung werden auf einem realen Windows-Entwicklungsrechner praktisch geprüft.

Dieses Arbeitspaket gilt erst als abgeschlossen, wenn der Export tatsächlich ausgeführt und das Modell im KiCad-3D-Viewer visuell bestätigt wurde.

## Vorbereitung

Für Windows steht der Starter bereit:

```text
tools\windows\export_z_mcb_3d.bat
```

Der Starter verwendet bevorzugt `.venv\Scripts\python.exe`, prüft zuerst die externen Werkzeuge und startet den Export nur bei vollständiger Toolchain.

Benötigt werden:

- OpenSCAD,
- FreeCAD mit `FreeCADCmd`,
- KiCad für die anschließende 3D-Viewer-Prüfung.

## Ablauf

1. aktuellen Branch `agent/sprint-006-mcb-goldstandard` lokal holen,
2. `tools\windows\export_z_mcb_3d.bat` starten,
3. prüfen, ob folgende Dateien erzeugt wurden:
   - `models\Z_MCB_1P\generated\Z_MCB_1P.step`,
   - `models\Z_MCB_1P\generated\Z_MCB_1P.wrl`,
4. `footprints\Z_MCB.pretty\Z_MCB_1P_18mm.kicad_mod` in KiCad öffnen,
5. 3D-Viewer starten,
6. Lage, Skalierung und Orientierung des Modells prüfen.

## Prüfkriterien

Der Praxisnachweis ist bestanden, wenn:

- STEP und WRL ohne Fehler erzeugt werden,
- das Modell mit realer Größe dargestellt wird,
- die 18-mm-Modulbreite zum Footprint passt,
- Vorderseite und Rückseite korrekt orientiert sind,
- das Modell nicht seitlich oder vertikal versetzt erscheint,
- keine Herstellerkennzeichnung oder Fremdgeometrie sichtbar ist.

## Korrekturregel

Falls Offset, Skalierung oder Rotation im KiCad-3D-Viewer nicht stimmen, werden ausschließlich die Transformationswerte der MCB-spezifischen Footprint-Bindung korrigiert. Die herstellerneutrale OpenSCAD-Quelle bleibt die Geometrie-Single-Source-of-Truth.

## Nachweis

Für den Abschluss werden dokumentiert:

- Ausgabe des Windows-Starters,
- erzeugte STEP-/WRL-Dateien,
- verwendete OpenSCAD-/FreeCAD-Versionen,
- bestätigte KiCad-Version,
- finale Offset-, Scale- und Rotate-Werte,
- Ergebnis der visuellen 3D-Viewer-Prüfung.

## Status

`vorbereitet – lokaler Praxislauf ausstehend`
