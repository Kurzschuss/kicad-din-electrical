# AP-0067 – KiCad-Bibliotheksprüfung und Referenzvalidierung

## Ziel

KiCad-Symbol-, Pin-, Footprint- und 3D-Modellreferenzen werden gegen einen lokalen, reproduzierbaren Bibliotheks-Snapshot geprüft.

## KiCad-Standard zuerst

ProjectOS übernimmt die KiCad-Struktur als führenden Vertrag. Symbole, Footprints und 3D-Modelle werden jedoch unabhängig voneinander bewertet.

Ein vorhandenes Symbol bedeutet ausdrücklich **nicht**, dass zwingend ein Footprint oder 3D-Modell vorhanden sein muss. Je Ziel und Artefaktart gilt eine der Anforderungen:

- `REQUIRED` – Artefakt muss vorhanden sein,
- `OPTIONAL` – Artefakt darf fehlen,
- `NOT_APPLICABLE` – Artefakt ist fachlich nicht anwendbar.

Standardwerte:

- Symbol: `REQUIRED`
- Footprint: `OPTIONAL`
- 3D-Modell: `OPTIONAL`

## Prüfungen

- erforderliche Artefaktarten sind vorhanden,
- qualifizierte Bibliotheksreferenz existiert im Snapshot,
- optionale SHA-256-Prüfsumme stimmt überein,
- zugeordnete Symbolpins existieren im Symbol,
- als nicht anwendbar markierte, dennoch vorhandene Artefakte erzeugen eine Warnung.

## Fehlerkennungen

- `ERR-KICAD-0018` – Bibliotheksreferenz ist nicht qualifiziert
- `ERR-KICAD-0019` – erforderliches KiCad-Artefakt fehlt
- `ERR-KICAD-0020` – Bibliothekseintrag wurde nicht gefunden
- `ERR-KICAD-0021` – Prüfsumme stimmt nicht überein
- `ERR-KICAD-0022` – zugeordneter Symbolpin fehlt
- `WARN-KICAD-0001` – Artefakt vorhanden, obwohl nicht anwendbar

## Grenzen

AP-0067 liest noch keine nativen KiCad-Dateien. Der Snapshot ist die stabile Eingabegrenze für spätere Parser und Adapter.
