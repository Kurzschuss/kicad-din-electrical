# Z_RCD-Referenzprojekt

Dieses KiCad-Projekt demonstriert das herstellerneutrale Referenzpaket `Z_RCD:RCD` mit dem empfohlenen mechanischen Footprint `Z_DIN_Module_36mm:Z_DIN_Module_36mm`.

## Voraussetzungen

1. `run_tests.bat` im Repository-Hauptordner ausführen.
2. Dabei werden die `KICAD_Z_*`-Pfade und die globalen `Z_`-Bibliotheken eingerichtet.
3. Anschließend `Z_RCD_Reference.pro` oder direkt `Z_RCD_Reference.sch` mit KiCad öffnen.

Das Beispiel verwendet bewusst projektlokale `sym-lib-table`- und `fp-lib-table`-Dateien. Sie verweisen ausschließlich auf:

- `${KICAD_Z_SYMBOL_DIR}/Z_RCD.kicad_sym`
- `${KICAD_Z_FOOTPRINT_DIR}/Z_DIN_Module_36mm.pretty`

## Inhalt

- ein platziertes `Z_RCD:RCD`
- Referenz `Q1`
- 2-polige Anschlussstruktur mit `L_IN`, `L_OUT`, `N_IN` und `N_OUT`
- Footprintzuordnung `Z_DIN_Module_36mm:Z_DIN_Module_36mm`
- alle vier externen Anschlüsse absichtlich als offen markiert

## ERC-Prüfung

In KiCad:

1. Schaltplaneditor öffnen.
2. **Prüfen → Elektrische Regeln prüfen** auswählen.
3. ERC ausführen.
4. Das Ergebnis dokumentieren, bevor der Paketstatus auf `Praxisgetestet` angehoben wird.

Der Repository-Status bleibt bis zu dieser realen KiCad-Prüfung `Geprüft`. Die automatisierten Tests kontrollieren nur Struktur, Bibliotheksverweise, Symbolkennung, Pinbelegung und Footprintzuordnung.

## Kompatibilität

Der Schaltplan liegt im von aktuellen KiCad-Versionen importierbaren Eeschema-Format Version 4 vor. Beim ersten Speichern darf KiCad ihn in das aktuelle `.kicad_sch`-Format überführen. Die `Z_`-Bibliotheksnamen und die projektlokalen Tabellen bleiben dabei maßgeblich.
