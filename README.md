# kicad-din-electrical

KiCad-Bibliotheken für DIN-Schaltgeräte, Reiheneinbaugeräte und zugehörige Footprints.

## Bibliotheksnamen

Alle projektinternen Bibliotheken verwenden das Präfix `Z_`, damit sie in KiCad eindeutig erkennbar und alphabetisch gebündelt sind.

### Symbole

Die Symbolbibliotheken liegen unter:

- `symbols/DIN_Electrical_Symbols/`
- `symbols/`

Jede Symbolbibliotheksdatei beginnt mit `Z_`, zum Beispiel:

- `Z_MCB.kicad_sym`
- `Z_CONTACTOR.kicad_sym`
- `Z_MAIN_SWITCH.kicad_sym`

Qualifizierte Symbol-IDs verwenden das Format:

```text
Z_<Bibliothek>:<Symbol>
```

Beispiel:

```text
Z_MCB:MCB
```

Die alte Sammelbibliotheks-ID `DIN_Electrical_Symbols:<Symbol>` darf nicht mehr verwendet werden.

### Footprints

Die Footprint-Dateien liegen direkt unter:

```text
footprints/
```

Alle Footprint-Dateien beginnen ebenfalls mit `Z_`, zum Beispiel:

- `Z_DIN_Module_18mm.kicad_mod`
- `Z_DIN_Terminal_Block.kicad_mod`

Qualifizierte Footprint-IDs verwenden das Format:

```text
Z_DIN_Rail:<Footprint>
```

Beispiel:

```text
Z_DIN_Rail:Z_DIN_Module_18mm
```

Die alte Bibliotheks-ID `DIN_Rail:<Footprint>` darf nicht mehr verwendet werden.

## KiCad-Einrichtung

In KiCad müssen die Symbolbibliotheken mit ihrem jeweiligen Dateinamen ohne Endung registriert werden. Die Footprints liegen gemeinsam im Verzeichnis `footprints/`.

Die CI-Prüfungen stellen sicher, dass Dateinamen, interne Namen und Referenzen konsistent bleiben.
