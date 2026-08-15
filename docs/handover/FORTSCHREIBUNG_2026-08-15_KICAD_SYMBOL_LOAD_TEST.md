# Fortschreibung 2026-08-15 – lokaler KiCad-Symbol-Ladetest vorbereitet

## Ausgangspunkt

Nach Abschluss der RCBO-/FI-LS-Arbeit (PR #248 und #249) und der Integration von `Z_I_ElectricalComponents` v14 ist der nächste verbindliche Qualitätsschritt der echte lokale KiCad-Ladetest.

## Neu vorbereitet

Branch:

```text
agent/kicad-local-symbol-load-test
```

Testskript:

```text
tools/windows/kicad_symbol_load_test.ps1
```

Dokumentation:

```text
docs/04_Reference/KICAD_LOCAL_SYMBOL_LOAD_TEST.md
```

## Automatischer Test

Das Skript verwendet die lokal installierte echte `kicad-cli.exe` und prüft nicht-destruktiv:

- RCBO-Bibliothek wird geladen und als SVG gerendert: erwartet 1 Symbol;
- `Z_I_ElectricalComponents` wird geladen und vollständig als SVG gerendert: erwartet 52 Symbole;
- beide Bibliotheken werden mit `sym upgrade --force` in Build-Kopien durch KiCad neu gespeichert;
- die neu gespeicherten Kopien werden erneut geladen und gerendert;
- `Contactor_3P_1NO_1NC` enthält strukturell Units 1–4;
- KiCad-Version und Ergebnis werden unter `build/kicad-symbol-load-test/` protokolliert;
- `VISUAL_CHECK.html` wird aus den echten KiCad-SVG-Renderings erzeugt.

## Noch nicht erledigt

Der Test wurde in dieser Sitzung noch **nicht auf dem lokalen Windows-/KiCad-System ausgeführt**.

Nach automatischem PASS müssen manuell geprüft werden:

1. RCBO: Klemmen `1 / 3 N / 2 / 4 N` und Fangpunkte;
2. `Contactor_3P_1NO_1NC`: Units A–D im KiCad-Symbolwähler;
3. Potential-/Pfeilsymbole: Fangpunkte;
4. komplette KiCad-Galerie der 52 Z_I-Symbole: Text, Rotation, Pinpositionen.

## Nächster Schritt

Den Branch lokal holen und ausführen:

```powershell
cd "C:\Users\uwezi\Documents\GitHub\kicad-din-electrical"
git fetch origin
git checkout agent/kicad-local-symbol-load-test
git pull --ff-only origin agent/kicad-local-symbol-load-test
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tools\windows\kicad_symbol_load_test.ps1
```

Danach `build\kicad-symbol-load-test\RESULT.txt` und bei Bedarf einen Screenshot bzw. den PowerShell-Log in die nächste Sitzung geben.

Erst nach lokalem PASS und manueller Sichtprüfung wird dieser Branch/Prüfstand nach `main` übernommen und anschließend die Z_I-v15-Normalisierungsplanung begonnen.
