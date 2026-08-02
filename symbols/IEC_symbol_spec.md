# IEC/DIN KiCad Symbol Specification

The library targets IEC 60617 / DIN-style electrical documentation.

## Core symbols

- MCB / Leitungsschutzschalter: 1P, 2P, 3P, 4P
- RCD / FI: 2P and 4P
- RCBO / FI-LS: 1P+N
- Fuse / Sicherung
- Motor protection / Motorschutz
- Contactor / Schütz
- Main switch / Hauptschalter
- Distribution / Verteilung

## Symbol requirements

Each production symbol should define:
- graphical body
- electrical pins with unique numbers
- pin names and electrical types
- Reference and Value fields
- Manufacturer and Part Number fields where applicable
- Datasheet and Footprint fields
- Description

## Validation

Before release, each `.kicad_sym` file must be opened with a compatible KiCad Symbol Editor and checked for syntax, pin connectivity, field visibility and ERC behavior.
