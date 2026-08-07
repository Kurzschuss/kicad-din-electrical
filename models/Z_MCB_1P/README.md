# Z_MCB_1P – herstellerneutrales 3D-Referenzmodell

## Zweck

Dieses Modell ist die ProjectOS-eigene, herstellerneutrale 3D-Referenz für einen einpoligen Leitungsschutzschalter im 18-mm-Modulraster.

Die Geometrie wurde von Grund auf neu als parametrische OpenSCAD-Quelle erstellt. Es wurden weder TraceParts-CAD-Daten noch Siemens- oder andere Herstellergeometrien importiert, kopiert oder bereinigt.

## Dateien

- `Z_MCB_1P.scad` – parametrische Originalquelle,
- `model.json` – maschinenlesbare Referenzmaße, Herkunft und Freigabestatus.

## Geometrischer Umfang

Das Entwurfsmodell bildet ausschließlich generische Merkmale ab:

- 18-mm-Modulbreite,
- neutraler Gehäusekörper,
- abstrahierter Bedienbereich,
- obere und untere Anschlusszone,
- vereinfachte rückseitige Aufnahme für eine 35-mm-DIN-Schiene,
- keine Logos,
- keine Herstellerartikelnummern,
- keine fest eingebrannten Kennwerte wie `B16` oder `10 kA`.

Die derzeitigen Körpermaße sind ProjectOS-Referenzmaße und keine Garantie für die mechanische Austauschbarkeit mit einem konkreten Herstellerprodukt.

## TraceParts-Regel

Der im Projekt diskutierte TraceParts-Datensatz wird nur als externe Referenzquelle geführt. Seine CAD-Geometrie ist kein Bestandteil dieses Modells und darf nicht stillschweigend als ProjectOS-Asset übernommen werden.

Hersteller-CAD bleibt grundsätzlich getrennt vom herstellerneutralen Objektmodell. Eine spätere konkrete Produktzuordnung darf auf Herstellerdaten verweisen, ändert aber nicht die neutrale Referenzgeometrie.

## Exportstrategie

OpenSCAD ist die editierbare Single Source of Truth für die erste neutrale Geometrie. STEP und KiCad-kompatible 3D-Ausgaben werden erst committed, wenn der Export reproduzierbar automatisiert und anschließend in KiCad geprüft werden kann.

Bis dahin bleibt der 3D-Status `Entwurf`.

## Freigaberegel

`Geprüft` setzt mindestens voraus:

- reproduzierbaren Export aus der Projektquelle,
- konsistente Abmessungen zum 18-mm-Footprint,
- keine fremden Herstellerassets,
- automatisierte Strukturprüfung,
- visuelle Prüfung des exportierten Modells.

`Praxisgetestet` setzt zusätzlich eine dokumentierte Darstellung im KiCad-3D-Viewer bzw. in einem realen Referenzprojekt voraus.
