# AP-0118 – MCB-Vorschau, Referenzprojekt und neutrales 3D-Modell

## Ziel

Der in AP-0117 umgesetzte MCB-1P-Goldstandard wird in den abgeleiteten Darstellungen nachgezogen. Gleichzeitig wird die 3D-Strategie so festgelegt, dass das herstellerneutrale ProjectOS-Objekt keine fremden Hersteller-CAD-Assets übernimmt.

## SVG-Vorschau

Der vorhandene Vorschaugenerator konnte bislang nur Rechtecke und Pins darstellen. Die neue MCB-Funktionsgrafik aus Polylinien wäre deshalb in der Browser-Vorschau unsichtbar geblieben.

Der Generator wurde um Polyline-Unterstützung erweitert und die MCB-Vorschau entsprechend aktualisiert. Damit zeigt die technische SVG-Vorschau jetzt nicht mehr nur den Rechteckkörper und die beiden Pins, sondern auch den definierten Schalt-/Schutzgerätepfad.

Die Entwicklerdokumentation beschreibt Polylinien jetzt als unterstützte Phase-1-Grafikform.

## Referenzprojekt

Das Referenzprojekt bleibt bewusst im Status `Entwurf`, solange kein realer KiCad-Praxisnachweis vorliegt. Die Projektdokumentation trennt daher weiterhin zwischen:

- reproduzierbarer Bibliotheksanbindung,
- Goldstandard-Definition,
- tatsächlicher Platzierung im KiCad-Schaltplan,
- ERC-Prüfung,
- Praxisstatus.

Eine behauptete Platzierung oder ERC-Freigabe wird nicht vorweggenommen.

## Entscheidung zum 3D-Modell

Das neutrale 3D-Modell wird von ProjectOS selbst erstellt.

Verbindliche Regel:

> Externe Hersteller-CAD-Daten, einschließlich TraceParts-Downloads, sind Referenzquellen und keine ProjectOS-eigenen 3D-Assets. Herstellerlogos zu entfernen oder Beschriftungen zu ändern macht ein fremdes CAD-Modell nicht automatisch zu einem neutralen ProjectOS-Modell.

Deshalb wurde unter `models/Z_MCB_1P/` eine eigene parametrische OpenSCAD-Quelle angelegt. Laut Modellmanifest wurden weder TraceParts-Geometrie noch Herstellergeometrie importiert.

## Neutrale Referenzgeometrie

Die erste ProjectOS-Geometrie verwendet bewusst einfache, generische Merkmale:

- Modulbreite: 18 mm,
- Referenzhöhe: 90 mm,
- Referenztiefe: 70 mm,
- abstrahierte obere und untere Anschlussbereiche,
- neutraler Betätiger,
- vereinfachte Aufnahme für 35-mm-DIN-Schiene,
- keine Herstellerlogos,
- keine Artikelnummern,
- keine fest eingebrannten elektrischen Kennwerte.

Die Maße sind Projekt-Referenzmaße. Sie behaupten keine mechanische Identität mit einem konkreten Herstellerprodukt.

## Single Source of Truth

Für die erste neutrale 3D-Geometrie gilt:

- `models/Z_MCB_1P/Z_MCB_1P.scad` = editierbare Geometriequelle,
- `models/Z_MCB_1P/model.json` = maschinenlesbare Maße, Herkunft und Status,
- STEP/WRL werden erst nach reproduzierbarer Exportkette als abgeleitete Assets committed.

Damit bleibt Configuration/Source before generated Asset gewahrt und ein unkontrolliertes Einchecken fremder CAD-Dateien wird vermieden.

## Automatische Absicherung

`tests/test_z_mcb_3d_reference_model.py` prüft mindestens:

- ProjectOS-eigene Herkunft,
- keine importierte TraceParts-/Herstellergeometrie,
- Status `Entwurf`,
- 18-mm-Modulvertrag,
- zentrale Referenzmaße,
- keine Herstellerbezeichnungen oder fest eingebrannten B16/10-kA-Kennwerte in der Modellquelle.

## Offene Praxisnachweise

Noch offen bleiben:

1. reproduzierbarer STEP-/WRL-Export,
2. Zuordnung des exportierten Modells zum passenden KiCad-Footprint,
3. visuelle Kontrolle im KiCad-3D-Viewer,
4. reale Platzierung des MCB-Symbols im Referenzschaltplan,
5. ERC-Lauf und dokumentiertes Ergebnis.

Diese Punkte werden in den Folgearbeitspaketen behandelt.

## Definition of Done

- neue Funktionsgrafik ist in der SVG-Vorschau abbildbar,
- Vorschaugenerator unterstützt Polylinien,
- Referenzprojekt behauptet keine nicht erfolgte Praxisprüfung,
- herstellerneutrale 3D-Strategie ist verbindlich dokumentiert,
- eigenes parametrisches MCB-1P-Modell ist angelegt,
- Herkunft und Referenzmaße sind maschinenlesbar dokumentiert,
- Modellneutralität ist automatisiert abgesichert,
- STEP/WRL und KiCad-Praxisprüfung sind klar als Folgearbeit abgegrenzt.
