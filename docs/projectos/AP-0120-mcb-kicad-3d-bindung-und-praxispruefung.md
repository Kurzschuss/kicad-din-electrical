# AP-0120 – MCB-1P KiCad-3D-Bindung und Praxisprüfung

## Ziel

Das ProjectOS-eigene MCB-1P-3D-Modell wird an einen eigenen KiCad-Footprint gebunden. Die Bindung ist so vorbereitet, dass nach lokalem STEP-Export Lage, Skalierung und Orientierung im KiCad-3D-Viewer praktisch geprüft werden können.

## Neuer KiCad-Footprint

Der MCB erhält einen eigenen mechanischen Footprint:

- Bibliothek: `Z_MCB.pretty`
- Footprint: `Z_MCB_1P_18mm`
- Referenzpräfix: `Q**`
- Referenzbreite: 18 mm
- Referenzhöhe: 90 mm
- Board-only / nicht in BOM und Positionsdateien

Der vorhandene generische Footprint `Z_DIN_Module_18mm` bleibt unverändert und wird nicht mit einem MCB-spezifischen 3D-Modell vermischt.

## 3D-Modellreferenz

Der Footprint referenziert ausschließlich das aus der ProjectOS-eigenen OpenSCAD-Quelle erzeugte STEP-Modell:

`models/Z_MCB_1P/generated/Z_MCB_1P.step`

Startwerte für die KiCad-Transformation:

- Offset: `0 / 0 / 0`
- Scale: `1 / 1 / 1`
- Rotation: `0 / 0 / 0`

Diese Werte sind bewusst nur der neutrale Ausgangspunkt. Erst der reale KiCad-3D-Viewer entscheidet, ob Offset oder Rotation angepasst werden müssen.

## Automatische Absicherung

`tests/test_z_mcb_3d_kicad_binding.py` prüft:

1. den 18-mm-Referenzumriss,
2. das Referenzpräfix `Q**`,
3. die Bindung an das ProjectOS-eigene STEP-Modell,
4. neutrale Ausgangswerte für Offset, Skalierung und Rotation,
5. das Fehlen von TraceParts- und Herstellerreferenzen im Footprint.

## Noch offener Praxisnachweis

Der STEP-Export und die visuelle Prüfung können nicht allein durch Repository-Textänderungen ersetzt werden. Lokal sind deshalb folgende Schritte auszuführen:

1. `python tools/export_z_mcb_3d.py --check-tools`
2. `python tools/export_z_mcb_3d.py`
3. KiCad öffnen.
4. `Z_MCB_1P_18mm` im Footprint-Editor bzw. Referenzprojekt laden.
5. 3D-Viewer öffnen.
6. Prüfen, ob das Gerät mittig auf dem 18-mm-Footprint liegt.
7. Prüfen, ob Front/Rückseite sowie Oben/Unten korrekt orientiert sind.
8. Prüfen, ob die Skalierung exakt in Millimetern passt.
9. Eventuelle Offset-/Rotationskorrekturen dokumentieren und erst danach festschreiben.

## Freigabestatus

AP-0120 bereitet die Bindung technisch vollständig vor, schließt den visuellen Praxisnachweis aber bewusst nicht vorweg.

Der 3D-Status bleibt deshalb `Entwurf`, bis STEP/WRL lokal erzeugt und der KiCad-3D-Viewer dokumentiert geprüft wurde.

## Definition of Done

- eigener MCB-1P-Footprint vorhanden,
- 18-mm-Referenzabmessungen hinterlegt,
- ProjectOS-eigenes STEP-Modell referenziert,
- Hersteller-/TraceParts-Geometrie ausgeschlossen,
- Bindung automatisiert getestet,
- lokale KiCad-Prüfschritte dokumentiert,
- Praxisfreigabe bewusst noch offen.
