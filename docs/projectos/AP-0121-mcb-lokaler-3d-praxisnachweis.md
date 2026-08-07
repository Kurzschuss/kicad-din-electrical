# AP-0121 – Lokaler MCB-3D-Praxisnachweis

## Ziel

Der in AP-0119 vorbereitete Export und die in AP-0120 angelegte KiCad-3D-Bindung werden auf einem realen Windows-Entwicklungsrechner praktisch geprüft.

## Verwendeter Ablauf

1. Branch `agent/sprint-006-mcb-goldstandard` lokal aktualisiert,
2. `tools\windows\export_z_mcb_3d.bat` ausgeführt,
3. OpenSCAD und FreeCAD/FreeCADCmd durch die Windows-Werkzeugerkennung gefunden,
4. `models\Z_MCB_1P\generated\Z_MCB_1P.step` erzeugt,
5. `models\Z_MCB_1P\generated\Z_MCB_1P.wrl` erzeugt,
6. Modell in KiCad über die Footprint-Eigenschaften und den 3D-Betrachter praktisch geprüft.

## Ergebnis

Der lokale Praxisnachweis ist erfolgreich.

Bestätigt wurden:

- STEP-Export erfolgreich,
- WRL-Export erfolgreich,
- Exportprozess endet ohne FreeCAD-Aufräumfehler,
- KiCad kann das erzeugte MCB-Modell darstellen,
- Skalierung `1 / 1 / 1` ist als reale Ausgangsskalierung verwendbar,
- Rotation `0 / 0 / 0` ist als Ausgangsorientierung verwendbar,
- Versatz `0 / 0 / 0` ist als Ausgangslage verwendbar,
- die herstellerneutrale MCB-Geometrie ist sichtbar,
- keine Herstellerkennzeichnung oder Fremdgeometrie ist Bestandteil des ProjectOS-Modells.

## Erkenntnis zur 3D-Pfadbindung

Während des Praxislaufs lag das erzeugte Modell zunächst nur in einem temporären Repository-Arbeitsverzeichnis. Dadurch konnte die im Footprint hinterlegte `${KIPRJMOD}`-Referenz das Modell nicht auflösen.

Nach Bereitstellung des erzeugten Modells im eigentlichen lokalen Repository unter

```text
models/Z_MCB_1P/generated/
```

konnte KiCad das Modell über einen direkten lokalen Pfad erfolgreich laden und darstellen. Damit ist nachgewiesen, dass die erzeugten STEP-/WRL-Dateien selbst funktionsfähig sind.

Der direkte lokale Windows-Pfad ist ausdrücklich **kein** portabler Repository-Vertrag und darf nicht als benutzerspezifischer Pfad in den ProjectOS-Footprint übernommen werden.

Die portable, repository-unabhängige KiCad-3D-Pfadstrategie wird deshalb separat in AP-0122 festgelegt und automatisiert abgesichert.

## Architekturregel

Die herstellerneutrale OpenSCAD-Quelle bleibt die Geometrie-Single-Source-of-Truth. STEP und WRL sind reproduzierbar erzeugte Zielartefakte. Benutzerabhängige absolute Pfade gehören nicht in versionierte KiCad-Bibliotheksobjekte.

## Status

`abgeschlossen – lokaler STEP/WRL-Export und visuelle KiCad-3D-Prüfung erfolgreich nachgewiesen`
