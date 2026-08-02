# Footprintbibliotheken

Dieser Index beschreibt die Footprintstruktur des Projekts. Die Bibliotheken liegen als `.pretty`-Ordner unter `footprints/`.

## Zuordnung

Für jede Symbolbibliothek soll ein gleichnamiger `.pretty`-Ordner existieren.

Beispiel:

```text
symbols/DIN_Electrical_Symbols/Z_DIN_Control.kicad_sym
footprints/Z_DIN_Control.pretty/
```

Eine `.pretty`-Bibliothek darf leer vorbereitet sein oder mehrere `.kicad_mod`-Dateien enthalten.

## Vorhandene Bibliotheksnamen

- `Z_MCB.pretty`
- `Z_FUSE.pretty`
- `Z_RCBO.pretty`
- `Z_RCD.pretty`
- `Z_RCBO_1P_N.pretty`
- `Z_Busbar_1P.pretty`
- `Z_Busbar_2P.pretty`
- `Z_Busbar_4P.pretty`
- `Z_PE_Busbar.pretty`
- `Z_DIN_Power.pretty`
- `Z_DIN_Safety.pretty`
- [`Z_DIN_Control.pretty`](Z_DIN_Control.md)
- `Z_MAIN_SWITCH.pretty`
- `Z_DISTRIBUTION.pretty`
- `Z_CONTACTOR.pretty`
- `Z_DIN_Terminals.pretty`
- `Z_N_PE_Terminal.pretty`
- `Z_MOTOR_PROTECT.pretty`
- `Z_Terminal_Block.pretty`

## Befüllte Beispiele

Im Repository sind unter anderem folgende Footprintdateien dokumentiert:

- [`Z_DIN_Module_18mm.kicad_mod`](Z_DIN_Module_18mm.md)
- `Z_DIN_Terminal_Block.kicad_mod`

Eine qualifizierte Footprint-ID hat dieses Format:

```text
<Bibliothek>:<Footprint>
```

Beispiel:

```text
Z_DIN_Module_18mm:Z_DIN_Module_18mm
```

## Ausbau

Später soll dieser Index automatisch aus den `.pretty`-Ordnern und `.kicad_mod`-Dateien erzeugt werden. Dann können Anzahl, Inhalt und Status jeder Bibliothek ohne manuelle Pflege angezeigt werden.
