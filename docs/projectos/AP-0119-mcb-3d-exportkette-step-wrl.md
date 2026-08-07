# AP-0119 – Reproduzierbare MCB-3D-Exportkette für STEP und WRL

## Ziel

Die ProjectOS-eigene OpenSCAD-Quelle des herstellerneutralen MCB 1P erhält eine reproduzierbare Exportkette für STEP und KiCad-kompatibles WRL/VRML. Fremde Hersteller-CAD-Daten werden dabei nicht verwendet.

## Single Source of Truth

Die editierbare Geometrie bleibt:

`models/Z_MCB_1P/Z_MCB_1P.scad`

STEP und WRL sind abgeleitete Artefakte und dürfen nicht manuell zu einer zweiten führenden Geometriequelle werden.

## Exportwerkzeuge

Die Exportkette verwendet lokal installierte Open-Source-Werkzeuge:

1. `OpenSCAD` rendert die Projektquelle nach STL.
2. `FreeCADCmd` übernimmt das temporäre STL-Netz.
3. FreeCAD erzeugt daraus die abgeleiteten Ausgaben STEP und WRL.

Der Export wird durch `tools/export_z_mcb_3d.py` gesteuert.

## Bedienung

Werkzeuge prüfen:

```text
python tools/export_z_mcb_3d.py --check-tools
```

Export starten:

```text
python tools/export_z_mcb_3d.py
```

Erwartete Ausgaben:

```text
models/Z_MCB_1P/generated/Z_MCB_1P.step
models/Z_MCB_1P/generated/Z_MCB_1P.wrl
```

## Schutzregeln

- keine TraceParts-Geometrie wird geladen,
- keine Siemens- oder sonstige Herstellergeometrie wird importiert,
- der Export arbeitet ausschließlich aus der ProjectOS-eigenen OpenSCAD-Quelle,
- erzeugte Dateien bleiben bis zur lokalen Prüfung unveröffentlicht/unfreigegeben,
- ein erfolgreicher Dateiexport allein setzt den Qualitätsstatus nicht auf `Geprüft`.

## Automatische Absicherung

`tests/test_export_z_mcb_3d.py` prüft:

- die fest definierte ProjectOS-Quelle,
- die erwarteten STEP-/WRL-Zielnamen,
- die FreeCAD-Konvertierungsanweisungen,
- dass keine TraceParts- oder Siemens-Herkunft in die Konvertierung eingebaut wird.

Die Tests führen bewusst keinen externen CAD-Prozess aus. Damit bleibt die reguläre Testsuite auch auf Systemen ohne OpenSCAD/FreeCAD reproduzierbar.

## Noch offener Praxisnachweis

Die Exportkette ist implementiert, aber in diesem Arbeitspaket wurden keine STEP-/WRL-Dateien als geprüftes Repository-Asset freigegeben. Der nächste Schritt muss auf einer Entwicklungsmaschine mit installierten Werkzeugen erfolgen:

1. `--check-tools` erfolgreich ausführen,
2. STEP und WRL erzeugen,
3. Dateien visuell kontrollieren,
4. WRL bzw. STEP dem KiCad-Footprint zuordnen,
5. KiCad-3D-Viewer öffnen,
6. Lage, Skalierung und Orientierung dokumentieren.

## Definition of Done

- reproduzierbares Exportskript vorhanden,
- Toolchain explizit dokumentiert,
- STEP-/WRL-Zielpfade maschinenlesbar im Modellmanifest hinterlegt,
- Exportlogik automatisiert statisch abgesichert,
- externe Hersteller-CAD-Geometrie ausgeschlossen,
- KiCad-Praxisprüfung als separates Folgearbeitspaket abgegrenzt.
