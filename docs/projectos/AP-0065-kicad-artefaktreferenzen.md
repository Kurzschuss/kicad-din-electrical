# AP-0065 – KiCad-Symbol-, Footprint- und 3D-Modellreferenzen

## Ziel

AP-0065 führt ein fachliches Referenzmodell für KiCad-Artefakte ein. Es speichert keine Binär- oder Bibliotheksdateien im Domänenobjekt, sondern nachvollziehbare Referenzen auf Symbole, Footprints und 3D-Modelle.

## Domänenobjekte

- `KiCadLibraryReference`: Bibliothek, Artefaktname und optionaler relativer Pfad
- `KiCadAssetReference`: Zuordnung eines Artefakts zu einem Kataloggerät oder Herstellerprodukt
- `KiCadAssetType`: `SYMBOL`, `FOOTPRINT`, `MODEL_3D`
- `KiCadAssetTargetType`: `CATALOG_DEVICE`, `MANUFACTURER_PRODUCT`
- `KiCadAssetStatus`: `DRAFT`, `ACTIVE`, `RETIRED`

## Invarianten

- Bibliotheks- und Artefaktnamen dürfen nicht leer sein.
- Dateipfade müssen relativ sein und dürfen keine aufsteigenden `..`-Segmente enthalten.
- Optionale SHA-256-Prüfsummen bestehen aus genau 64 hexadezimalen Zeichen.
- Ausgemusterte Artefakte dürfen weder reaktiviert noch geändert werden.
- Dieselbe qualifizierte Bibliotheksreferenz darf einem Ziel je Artefakttyp nur einmal zugeordnet werden.
- Zustandsänderungen und Referenzänderungen erhöhen die Revision.

## Fehlerkennungen

- `ERR-KICAD-0001`: Bibliotheksname fehlt
- `ERR-KICAD-0002`: Artefaktname fehlt
- `ERR-KICAD-0003`: unsicherer oder absoluter Pfad
- `ERR-KICAD-0004`: ungültige SHA-256-Prüfsumme
- `ERR-KICAD-0005`: ausgemustertes Artefakt darf nicht reaktiviert werden
- `ERR-KICAD-0006`: ausgemustertes Artefakt darf nicht geändert werden
- `ERR-KICAD-0007`: doppelte Zielzuordnung

## Abgrenzung

Nicht Bestandteil dieses Arbeitspakets sind das Parsen nativer KiCad-Dateien, automatische Pin-Zuordnungen, Dateiimporte, Bibliothekssynchronisation und geometrische 3D-Prüfungen. Diese Funktionen bauen später auf den stabilen Referenzen dieses Pakets auf.
