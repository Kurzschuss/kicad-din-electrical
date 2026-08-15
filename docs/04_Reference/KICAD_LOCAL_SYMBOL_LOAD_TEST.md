# Lokaler KiCad-Symbol-Ladetest

## Zweck

Dieser Test ist die Brücke zwischen den repository-internen Parser-/Strukturtests und einem echten KiCad-Lauf auf Windows.

Geprüft werden die aktuell besonders relevanten Bibliotheken:

- `symbols/Z_RCBO_1P_N.kicad_sym`
- `symbols/Z_I_ElectricalComponents.kicad_sym`

## Testskript

```text
tools/windows/kicad_symbol_load_test.ps1
```

Das Skript sucht `kicad-cli.exe` automatisch in `PATH` und unter üblichen KiCad-Installationspfaden in `C:\Program Files\KiCad`.

## Automatischer Testumfang

1. KiCad-Version mit `kicad-cli version --format about` erfassen.
2. RCBO-Bibliothek mit dem echten KiCad-Parser laden und per `sym export svg` rendern.
3. `Z_I_ElectricalComponents` vollständig mit `sym export svg` rendern.
4. Erwartete Anzahl prüfen:
   - RCBO: 1 Top-Level-Symbol
   - Z_I: 52 Top-Level-Symbole
5. Beide Bibliotheken mit `sym upgrade --force` in **separate Build-Kopien** neu speichern lassen; die Quellen werden nicht verändert.
6. Die neu gespeicherten KiCad-Kopien erneut vollständig laden/rendern.
7. Beim zusammengesetzten `Contactor_3P_1NO_1NC` strukturell prüfen, dass Units 1–4 vorhanden sind.
8. Aus den durch KiCad selbst gerenderten SVGs eine lokale HTML-Galerie erzeugen.

Die verwendeten KiCad-CLI-Kommandos sind Bestandteil der offiziellen KiCad-CLI: `sym export svg`, `sym upgrade` und `version`.

## Ausgabe

Alle Ausgaben liegen nur unter:

```text
build/kicad-symbol-load-test/
```

Wichtigste Dateien:

```text
RESULT.txt
KICAD_VERSION.txt
VISUAL_CHECK.html
```

Die Build-Ausgabe gehört nicht in die Symbolbibliotheken und verändert die Quelldateien nicht.

## Start unter Windows PowerShell

Vom Repository aus:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tools\windows\kicad_symbol_load_test.ps1
```

Alternativ mit explizitem Repository-Pfad:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tools\windows\kicad_symbol_load_test.ps1 `
  -RepoPath "C:\Users\uwezi\Documents\GitHub\kicad-din-electrical"
```

## Manuelle Endkontrolle nach automatischem PASS

Der CLI-Test beweist, dass KiCad die Bibliotheken laden, rendern und neu speichern kann. Folgende UI-/Fangpunktprüfungen bleiben bewusst manuell:

1. `Z_RCBO_1P_N:RCBO_1P_N` in KiCad platzieren und `1 / 3 N / 2 / 4 N` sowie die vier Anschlussfangpunkte prüfen.
2. `Contactor_3P_1NO_1NC` im Symbolwähler öffnen und alle vier Units A–D einzeln anzeigen.
3. Potential- und Pfeilsymbole aus `Z_I_ElectricalComponents` platzieren und Fangpunkte prüfen.
4. Die durch KiCad erzeugte `VISUAL_CHECK.html` mit allen 52 Z_I-Symbolen auf abgeschnittene Texte, falsche Rotation und unplausible Pinpositionen prüfen.

## Freigaberegel

Der lokale KiCad-Ladetest gilt als bestanden, wenn:

- das Skript mit `AUTOMATISCHER KICAD-LADETEST: PASS` endet;
- `RESULT.txt` PASS meldet;
- die vier manuellen Punkte ohne Fehler bestätigt wurden.

Erst danach wird der Handover von „lokaler KiCad-Ladetest offen“ auf „bestanden“ gestellt und die Z_I-v15-Normalisierungsplanung begonnen.
