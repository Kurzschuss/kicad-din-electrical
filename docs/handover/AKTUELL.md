# Aktueller Handover

Stand: **16.08.2026 – Tagesabschluss / RCBO-GUI-Prüfung PASS**

Für die nächste Fortsetzung zuerst lesen:

1. [`TAGESABSCHLUSS_2026-08-16.md`](TAGESABSCHLUSS_2026-08-16.md)
2. [`TAGESABSCHLUSS_2026-08-15.md`](TAGESABSCHLUSS_2026-08-15.md)
3. [`FORTSCHREIBUNG_2026-08-15_KICAD_SYMBOL_LOAD_TEST_PASS.md`](FORTSCHREIBUNG_2026-08-15_KICAD_SYMBOL_LOAD_TEST_PASS.md)
4. [`FORTSCHREIBUNG_2026-08-15_RCBO_TYP_A_SYMBOL.md`](FORTSCHREIBUNG_2026-08-15_RCBO_TYP_A_SYMBOL.md)
5. [`FORTSCHREIBUNG_2026-08-14_Z_I_OVERLAP_AUDIT.md`](FORTSCHREIBUNG_2026-08-14_Z_I_OVERLAP_AUDIT.md)
6. [`FORTSCHREIBUNG_2026-08-14_Z_I_MERGE.md`](FORTSCHREIBUNG_2026-08-14_Z_I_MERGE.md)
7. [`ARBEITSSTAND_2026-08-14_Z_I_SYMBOLBIBLIOTHEK.md`](ARBEITSSTAND_2026-08-14_Z_I_SYMBOLBIBLIOTHEK.md)
8. Danach für den breiteren Projektkontext: [`ARBEITSSTAND_2026-08-13_GESAMT_HANDOVER.md`](ARBEITSSTAND_2026-08-13_GESAMT_HANDOVER.md)

## Aktueller RCBO-/FI-LS-Endstand

Die Typ-A-RCBO-Familie `Z_RCBO_1P_N:RCBO_1P_N` ist als gemeinsame Bauart `1P+N / 2P` umgesetzt:

- kein separates zweites 2P-Symbol;
- 64 Typ-A-Planungsvarianten;
- Nennstrom 6/10/13/16/20/25/32/40 A;
- Bemessungsdifferenzstrom 10/30 mA;
- Kennlinie B/C;
- Ausschaltvermögen 6/10 kA;
- Typ A;
- PR #248 erfolgreich gemergt.

Die RCBO-Symbolgrafik wurde anhand der abgestimmten Referenz neu aufgebaut. Enthalten sind insbesondere Testkreis, drei mechanisch gekoppelte Schaltkontakte, Überstromauslöser im L-Zweig, Summenstromwandler, rechter Fehlerstrom-/Betätigungsblock und die Klemmenkennzeichnung `1 / 3 N / 2 / 4 N`.

PR #249 wurde erfolgreich gemergt; Squash-Merge:

```text
99aee707ab975e4ba9d7c536c7012c9434417798
```

Repository-Prüfstand nach dem RCBO-Merge:

- 7/7 RCBO-spezifische Tests bestanden;
- 934/934 Gesamttests bestanden;
- Bibliotheksvalidator: 0 Fehler;
- ProjectOS: 10/10 Prüfungen bestanden;
- 75 Symbolvorschauen aktuell;
- 285 generierte Gerätevarianten aktuell;
- Gerätekatalog: 287 Gerätedateien / 19 Familien / 0 Fehler.

## Echter lokaler KiCad-Ladetest

Der automatische lokale KiCad-Test wurde am 15.08.2026 erfolgreich ausgeführt.

Verwendete CLI:

```text
C:\Program Files\KiCad\10.99\bin\kicad-cli.exe
```

Version:

```text
10.99.0-2307-g5c04cac95a, release build
```

Automatisches Ergebnis: **PASS**

- RCBO: 1 logisches Symbol, 1/1 gerendert;
- Z_I: 52 logische Top-Level-Symbole;
- KiCad-Export: 55 Unit-SVGs wegen des Mehrfacheinheiten-Schützes;
- Re-Save-Test von RCBO und Z_I erfolgreich;
- erneuter Export der Re-Save-Kopien erfolgreich;
- `Contactor_3P_1NO_1NC`: 4/4 Units strukturell vorhanden.

Durch den echten KiCad-Parser wurden zusätzlich Fehler entdeckt und im Branch `agent/kicad-local-symbol-load-test` korrigiert:

1. PowerShell-Parserfehler bei `"$Label:"` → `"${Label}:"`;
2. freie `; ...`-Kommentarzeilen in `Z_RCBO_1P_N.kicad_sym` entfernt, weil KiCad damit die Bibliothek nicht lud;
3. Testlogik von 52 erwarteten SVGs auf 52 logische Symbole / 55 Unit-SVGs korrigiert.

## Manuelle RCBO-GUI-Prüfung vom 16.08.2026

Die manuelle Kontrolle des im Schaltplaneditor platzierten Symbols ist abgeschlossen: **PASS**.

Während der Sichtprüfung wurde die RCBO-Geometrie iterativ an die Referenz angepasst. Freigegebener Stand im Prüfbranch:

- sichtbare Klemmenbezeichnungen `1 / 3 N / 2 / 4 N` ohne doppelte automatische Pintexte;
- drei mechanisch gekoppelte Schaltkontakte in korrekter Anordnung;
- mittlerer Kontaktwinkel an die Referenz angepasst;
- gestrichelte mechanische Kopplung durch die Kontaktgruppe und den rechten Betätigungsblock;
- obere Drahtbrücke links korrigiert;
- rechter Betätigungs-/Auslöseblock in der Höhe angepasst;
- linker Testzweig mit Widerstand, eigenem Schaltkontakt und E-förmiger Betätigung mit schräger mechanischer Anlenkung nach Referenz;
- übrige Leiterführung und Summenstromwandler beibehalten.

Die zuletzt in KiCad sichtbare Fassung wurde vom Anwender mit „sollte passen“ freigegeben. RCBO-Neuzeichnung ist damit **nicht mehr der nächste Arbeitspunkt**.

## Aktueller Z_I-Endstand

`Z_I_ElectricalComponents` v14 ist in `main` integriert:

- 52 Top-Level-Symbole;
- 254 KiCad-Pindefinitionen;
- PR #247 erfolgreich gemergt;
- 8 direkte Funktionsdubletten im Overlap-Audit;
- 3 strukturelle Schütz-Overlaps;
- 41 Symbole ohne direktes kanonisches Gegenstück.

Der echte lokale KiCad-Ladetest bestätigt zusätzlich, dass die Bibliothek vom KiCad-Parser geladen und vollständig gerendert werden kann.

## Nächster verbindlicher Arbeitsschritt

RCBO ist in der GUI freigegeben. Als Nächstes direkt mit der restlichen **manuellen KiCad-GUI-Endkontrolle** fortsetzen:

1. `Contactor_3P_1NO_1NC` im Symbolwähler mit Units A–D einzeln anzeigen und prüfen.
2. Potential-/Pfeilsymbole auf Fangpunkte prüfen.
3. Alle 52 Z_I-Symbole auf Textrotation, abgeschnittene Texte und unplausible Pinpositionen prüfen.
4. Bei PASS den Prüfbranch nach `main` übernehmen.
5. Danach gezielte **Z_I-v15-Normalisierungsplanung** beginnen.

Nicht erneut bei RCBO-Matrix, RCBO-Neuzeichnung oder automatischem KiCad-Ladetest beginnen.

`main` bleibt die Single Source of Truth für bereits gemergte Arbeit. Der Branch `agent/kicad-local-symbol-load-test` enthält den aktuellen Prüfstand und die noch zu übernehmenden KiCad-Kompatibilitäts- und GUI-Korrekturen.
