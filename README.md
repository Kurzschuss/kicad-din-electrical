# kicad-din-electrical

KiCad-Bibliotheken für DIN-Schaltgeräte, Reiheneinbaugeräte und zugehörige Footprints.

## Bibliotheksnamen

Alle projektinternen Bibliotheken verwenden das Präfix `Z_`, damit sie in KiCad eindeutig erkennbar und alphabetisch gebündelt sind.

### Symbole

Alle Symbolbibliotheken liegen unter:

- `symbols/DIN_Electrical_Symbols/`

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

Die Footprint-Bibliotheken liegen unter:

```text
footprints/
```

Für jede `.kicad_sym`-Datei existiert ein gleichnamiger `.pretty`-Ordner. Beispiel:

```text
symbols/DIN_Electrical_Symbols/Z_DIN_Control.kicad_sym
footprints/Z_DIN_Control.pretty/
```

Eine `.pretty`-Bibliothek darf mehrere `.kicad_mod`-Dateien enthalten. Jede Footprint-Datei beginnt mit `Z_`, und ihr interner Footprint-Name muss dem Dateinamen ohne Endung entsprechen.

Beispiel:

```text
footprints/Z_DIN_Control.pretty/Z_DIN_Pushbutton.kicad_mod
footprints/Z_DIN_Control.pretty/Z_DIN_Selector_Switch.kicad_mod
```

Qualifizierte Footprint-IDs verwenden den Namen des `.pretty`-Ordners und den Namen des enthaltenen Footprints:

```text
Z_<Bibliothek>:Z_<Footprint>
```

Beispiel:

```text
Z_DIN_Control:Z_DIN_Pushbutton
```

Die alten Bibliotheks-IDs `DIN_Rail:<Footprint>` und `Z_DIN_Rail:<Footprint>` dürfen nicht mehr verwendet werden.

## KiCad-Einrichtung

In KiCad müssen die Symbolbibliotheken mit ihrem jeweiligen Dateinamen ohne Endung registriert werden. Die Footprint-Bibliotheken werden aus den einzelnen `.pretty`-Ordnern unter `footprints/` eingebunden.

Die CI-Prüfungen stellen sicher, dass Dateinamen, interne Namen, Ordnerstruktur und Referenzen konsistent bleiben.
