# Z_Cockpit – 3D-Vorschauen und Modellabdeckung

Stand: 10. August 2026

## Ziel

Das Z_Cockpit zeigt den 3D-Stand eines Geräts beziehungsweise eines zugeordneten Footprints nachvollziehbar an. Dabei wird strikt zwischen einem **echten KiCad-3D-Modell** und einer rein technischen **Hüllkörper-Vorschau** unterschieden.

Es werden keine nicht vorhandenen Gerätegehäuse erfunden.

## Datenquellen

Die 3D-Auswertung verwendet ausschließlich vorhandene Repositoryquellen:

- Symbol-zu-Footprint-Zuordnung aus `metadata/footprint_mapping.csv`;
- native KiCad-Footprints unter `footprints/*.pretty/*.kicad_mod`;
- dort vorhandene KiCad-`model`-Referenzen;
- Repository-3D-Modellpfad `3dmodels/Z_3DModell.3dshapes/`;
- vorhandene `F.Fab`-Rechteckgeometrie als mechanische Hüllinformation.

Der für KiCad bereits registrierte Pfad lautet:

```text
KICAD_Z_3DMODEL_DIR = <Repository>/3dmodels/Z_3DModell.3dshapes
```

Empfohlene Repositoryreferenz in einem Footprint:

```text
${KICAD_Z_3DMODEL_DIR}/Z_Beispiel.step
```

## Unterstützte Modellformate

ProjectOS behandelt native KiCad-3D-Artefakte in den Formaten:

- `.step`;
- `.stp`;
- `.wrl`.

Der Z_Cockpit-Vorschaugenerator parst die komplexe STEP-/VRML-Geometrie nicht selbst als alternatives CAD-System. Er prüft die vorhandene KiCad-Modellreferenz und die Repositorydatei. Die eigentliche Modellgeometrie bleibt KiCad-Quelle.

## Statusmodell

### `Modell`

Ein Footprint besitzt eine auflösbare Repository-`model`-Referenz und die referenzierte Datei ist vorhanden.

Dieser Zustand zählt als echtes 3D-Modell.

### `Modellreferenz fehlt`

Eine `model`-Referenz ist im Footprint vorhanden, kann aber nicht auf eine vorhandene Repositorydatei unter `KICAD_Z_3DMODEL_DIR` aufgelöst werden.

Dieser Zustand zählt nicht als vorhandenes 3D-Modell.

### `Hüllkörper`

Es ist kein echtes 3D-Modell vorhanden, aber der Footprint besitzt verwertbare `F.Fab`-Rechteckgeometrie. Daraus wird deterministisch eine isometrische technische Hüllkörperansicht erzeugt.

Wichtig: Der Hüllkörper ist **keine Gerätegehäuse- oder STEP-Modellbehauptung**. Er zeigt nur die bereits vorhandene mechanische F.Fab-Grundkontur räumlich. Die Tiefe ist rein für die technische Lesbarkeit der Vorschau gewählt und keine Produktabmessung.

### `Fehlt`

Weder ein echtes 3D-Modell noch verwertbare `F.Fab`-Hüllgeometrie ist vorhanden.

### `Nicht zugeordnet`

Für das Symbol ist kein Footprint in der zentralen Footprint-Zuordnung hinterlegt.

## Aktueller Repositorybestand

Zum Implementierungszeitpunkt enthalten die derzeit zentral zugeordneten Footprints noch keine echten KiCad-3D-Modellreferenzen.

Vorhandene technische Hüllkörper können nur dort erzeugt werden, wo bereits geeignete `F.Fab`-Geometrie existiert. Insbesondere die generischen DIN-Modul-Footprints mit vorhandener mechanischer Kontur können so sichtbar gemacht werden. Leere Footprint-Platzhalter bleiben ausdrücklich `Fehlt`.

Damit ist die Infrastruktur für echte Modelle vollständig angebunden, ohne einen falschen Abdeckungsstand vorzutäuschen.

## Generator

Erzeugen:

```text
python -m tools.generate_3d_previews
```

Prüfen:

```text
python -m tools.generate_3d_previews --check
```

Ausgabe:

```text
docs/site/3d-previews/*.svg
```

Der Generator ist deterministisch und verändert keine KiCad-Quelldateien.

## Z_Cockpit-Integration

### Startseite

Die Startseite zeigt getrennte Kennzahlen für:

- echte `3D-Modelle`;
- verfügbare `3D-Vorschauen`.

Eine Hüllkörper-Vorschau erhöht nur die Vorschauzahl, nicht die Zahl echter Modelle.

### Geräte

In der Geräteansicht wird der bisherige 3D-Platzhalter durch den tatsächlichen Status ersetzt. Im festen rechten Eigenschaftenbereich stehen:

- 3D-Status;
- vorhandene Modellreferenz;
- technische 3D-Vorschau beziehungsweise eindeutiger Fehlstatus.

Symbol- und Footprintvorschau bleiben unverändert vorhanden.

### Bibliotheken

Die freigegebene Bibliotheksarbeitslogik bleibt erhalten. Ergänzt werden:

- 3D-Status je Symbol;
- Anzahl echter 3D-Modelle je Bibliothek;
- Anzahl technischer 3D-Vorschauen;
- Filter `3D-Vorschauen`;
- 3D-Vorschau im festen rechten Symbolinspektor.

Der separate Scrollbereich für Geräte-IDs bleibt erhalten.

### Einstellungen

Unter `Pfade` wird der Repositorypfad der 3D-Modelle angezeigt:

```text
3dmodels/Z_3DModell.3dshapes/
```

## Windows-Starter

`tools/windows/open_z_cockpit.bat` erzeugt die technischen 3D-Vorschauen vor dem Z_Cockpit neu. Dadurch entspricht eine lokal geöffnete Cockpit-Ansicht dem aktuellen Footprint-/Modellstand.

## CI und Release

Die vollständige ProjectOS-CI und der ProjectOS-Release prüfen mit:

```text
python tools/generate_3d_previews.py --check
```

ob die versionierten Vorschauen dem Generatorstand entsprechen.

## Architekturgrenze

Die 3D-Vorschau ist read-only gegenüber KiCad-Quellen.

Sie:

- erzeugt keine STEP-/VRML-Gerätemodelle aus Vermutungen;
- ändert keine Footprints;
- trägt keine `model`-Referenzen automatisch ein;
- lädt keine Herstellerdateien aus dem Internet;
- zählt eine Hüllkörperansicht niemals als echtes 3D-Modell.

Echte Produktmodelle können später als eigene, fachlich geprüfte Repository-Artefakte ergänzt und anschließend über die normale KiCad-`model`-Referenz angebunden werden.
