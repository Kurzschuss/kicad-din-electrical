# AP-0061 – Fachliches Domänenmodell des Gerätekatalogs

## Status

Implementiert. CI-Bestätigung steht für den neuen Stand noch aus.

## Ziel

Sprint 005 beginnt mit einem hersteller- und technologieunabhängigen Katalogaggregat für elektrische Geräte. Das Modell bildet die fachliche Identität, Kategorie, technische Eigenschaften, Schlagwörter, Lebenszyklus und Revision eines Geräteeintrags ab.

## Komponenten

- `DeviceCategory`
- `CatalogDeviceStatus`
- `DeviceProperty`
- `CatalogDevice`

## Kategorien

Der erste Vertrag unterstützt `MCB`, `RCCB`, `RCBO`, `AFDD`, `SPD`, `CONTACTOR`, `RELAY` und `OTHER`. Die Kategorien sind fachliche Ordnungsmerkmale; gerätespezifische Validierungsprofile bleiben in ihren jeweiligen Domänen.

## Aggregate Root

`CatalogDevice` besitzt:

- technische `ObjectId`,
- stabile fachliche `catalog_id`,
- Namen und Beschreibung,
- Gerätekategorie,
- eindeutige technische Eigenschaften,
- normalisierte Schlagwörter,
- Lebenszyklusstatus,
- optimistische Revision.

Das Aggregat ist unveränderlich. Änderungen erzeugen eine neue Instanz und erhöhen die Revision.

## Invarianten

- Ein Gerät benötigt einen Namen.
- Eigenschaftsschlüssel verwenden `snake_case`.
- Eigenschaftswerte dürfen nicht leer sein.
- Eigenschaftsschlüssel sind je Gerät eindeutig.
- Ein aktives Gerät benötigt mindestens eine technische Eigenschaft.
- Die letzte Eigenschaft eines aktiven Geräts darf nicht entfernt werden.
- Ein ausgemustertes Gerät kann nicht erneut aktiviert werden.
- Revisionen dürfen nicht negativ sein.

## Lebenszyklus

```text
DRAFT → ACTIVE → RETIRED
```

`RETIRED` ist endgültig. Wiederholtes Aktivieren oder Ausmustern eines bereits im Zielzustand befindlichen Geräts erzeugt keine unnötige Revision.

## Fehlerkennungen

- `ERR-CAT-0001`: Eigenschaft nicht gefunden
- `ERR-CAT-0002`: Letzte Eigenschaft eines aktiven Geräts darf nicht entfernt werden
- `ERR-CAT-0003`: Ausgemustertes Gerät darf nicht reaktiviert werden
- `ERR-CAT-0004`: Gerät ohne Eigenschaften darf nicht aktiviert werden

## Abgrenzung

Noch nicht Bestandteil dieses Arbeitspakets sind:

- Hersteller und Produktserien,
- Artikel- und Bestellnummern,
- Normenreferenzen,
- KiCad-Symbole, Footprints und 3D-Modelle,
- SQLite-Persistenz des Katalogs,
- gerätekategoriespezifische Validierungsregeln.

Diese Verantwortungen werden in getrennten Arbeitspaketen ergänzt, damit Domain Ownership erhalten bleibt.

## Tests

Die Tests prüfen Normalisierung, Eigenschaftsinvarianten, unveränderliche Änderungen, Revisionen, Aktivierung, Ausmusterung und den Schutz der letzten Eigenschaft eines aktiven Geräts.
