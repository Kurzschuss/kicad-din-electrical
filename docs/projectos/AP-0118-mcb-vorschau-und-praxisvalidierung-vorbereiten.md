# AP-0118 – MCB-Vorschau und Praxisvalidierung vorbereiten

## Ziel

Die in AP-0117 eingeführte Funktionsgrafik des MCB-1P-Goldstandards wird in der automatischen SVG-Vorschau sichtbar gemacht. Gleichzeitig wird das Referenzprojekt so dokumentiert, dass die noch ausstehende reale KiCad-Praxisprüfung reproduzierbar und ohne Status-Selbstbestätigung durchgeführt werden kann.

## Ausgangslage

Die bisherige Vorschaugenerierung unterstützte nur Rechtecke und Pins. Die neue MCB-Funktionsgrafik verwendet zusätzlich KiCad-Polylinien und war deshalb in der bestehenden SVG-Vorschau nicht sichtbar.

Das Referenzprojekt enthält weiterhin bewusst noch keine als erfolgt markierte KiCad-Praxisprüfung. Die Manifestfelder `symbol_placed`, `erc_checked` und `opened_in_kicad` bleiben bis zur tatsächlich ausgeführten Prüfung `false`.

## Umsetzung Symbolvorschau

`tools/generate_symbol_previews.py` unterstützt jetzt zusätzlich KiCad-Polylinien.

Neu hinzugefügt wurden:

- strukturierte `Polyline`-Daten,
- Parser für `(polyline (pts ...))`,
- SVG-Ausgabe als `<polyline>`,
- Regressionstests für Parsing und Rendering.

Damit zeigt `docs/site/symbol-previews/Z_MCB/MCB.svg` neben Grundkörper und Pins auch die in AP-0117 definierte Schalt-/Schutzgerätegrafik.

## Aktualitätsvertrag

Die Vorschau bleibt aus der KiCad-Symboldatei ableitbar. `python tools/generate_symbol_previews.py --check` kann dadurch weiterhin erkennen, wenn die gespeicherte SVG-Datei nicht mehr dem Symbolstand entspricht.

Die MCB-spezifischen Regressionstests prüfen zusätzlich, dass die Goldstandard-Vorschau mindestens zwei Polylinien enthält und die zentrale Funktionsgrafik nicht versehentlich verloren geht.

## Vorbereitung der Praxisvalidierung

Die README des Referenzprojekts enthält jetzt einen verbindlichen Ablauf für die reale KiCad-Prüfung:

1. Projekt in KiCad öffnen,
2. Bibliotheksbindung prüfen,
3. `Z_MCB:MCB` tatsächlich platzieren,
4. beide Pins in einen einfachen Teststrompfad einbinden,
5. Darstellung kontrollieren,
6. ERC ausführen,
7. Befunde beheben oder dokumentieren,
8. erst danach die Manifestfelder aktualisieren.

Diese Reihenfolge verhindert, dass ein erfolgreicher automatisierter Testlauf fälschlich als Praxisnachweis verwendet wird.

## Statusschutz

Automatisierte Tests sichern ab, dass das Referenzprojekt bis zur realen Praxisvalidierung auf `Entwurf` bleibt und die drei Praxisfelder nicht vorzeitig auf `true` gesetzt werden.

Damit gilt weiterhin:

- Automatisierte Tests und Vorschauen = technischer Nachweis,
- reale KiCad-Platzierung und ERC = Praxisnachweis.

## Offener Punkt

Die eigentliche KiCad-Praxisvalidierung ist mit diesem Arbeitspaket bewusst noch nicht als erledigt markiert. Sie erfordert eine reale KiCad-Sitzung und wird im Folgearbeitspaket durchgeführt bzw. dokumentiert.

## Definition of Done

- Polylinien werden durch den Vorschaugenerator unterstützt,
- MCB-SVG enthält die Goldstandard-Funktionsgrafik,
- Parser und Rendering sind automatisiert getestet,
- Praxisvalidierungsablauf ist im Referenzprojekt dokumentiert,
- Manifest bleibt bis zum realen Nachweis auf `Entwurf`,
- automatisierter Schutz gegen vorzeitige Statusanhebung ist vorhanden,
- reale KiCad-Validierung ist als nächster Schritt eindeutig abgegrenzt.
