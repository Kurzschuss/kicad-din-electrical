# Z_3DModell.3dshapes

Dieser Ordner ist die versionierte Repositoryquelle für geprüfte KiCad-3D-Modelle der KiCad DIN Electrical Suite.

KiCad verwendet dafür die bereits registrierte Umgebungsvariable:

```text
KICAD_Z_3DMODEL_DIR
```

Eine Footprintreferenz soll bevorzugt so aufgebaut sein:

```text
${KICAD_Z_3DMODEL_DIR}/Z_Beispiel.step
```

Unterstützte native ProjectOS-/KiCad-Artefakte sind `.step`, `.stp` und `.wrl`.

## Regeln

- Nur fachlich geprüfte und lizenzrechtlich zulässige Modelle versionieren.
- Modellname und zugehöriger Footprint müssen eindeutig nachvollziehbar sein.
- Keine automatisch aus Produktnamen erfundene Geometrie erzeugen.
- Herstellerdateien nicht ungeprüft oder automatisch aus dem Internet übernehmen.
- Transformationen (`offset`, `scale`, `rotate`) bleiben in der KiCad-`model`-Referenz des Footprints nachvollziehbar.
- Ein technischer F.Fab-Hüllkörper im Z_Cockpit ist kein Ersatz für eine echte Datei in diesem Ordner.

Der aktuelle Modellbestand darf leer sein. Das Z_Cockpit zeigt diesen Zustand ausdrücklich als fehlende echte 3D-Modellabdeckung an.

Weitere Details: `docs/03_Developer/Z_COCKPIT_3D_VORSCHAUEN.md`.
