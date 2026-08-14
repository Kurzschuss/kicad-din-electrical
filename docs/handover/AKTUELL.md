# Aktueller Handover

Stand: **15.08.2026**

Für die nächste Fortsetzung zuerst lesen:

1. [`FORTSCHREIBUNG_2026-08-15_RCBO_TYP_A_SYMBOL.md`](FORTSCHREIBUNG_2026-08-15_RCBO_TYP_A_SYMBOL.md)
2. [`FORTSCHREIBUNG_2026-08-14_Z_I_OVERLAP_AUDIT.md`](FORTSCHREIBUNG_2026-08-14_Z_I_OVERLAP_AUDIT.md)
3. [`FORTSCHREIBUNG_2026-08-14_Z_I_MERGE.md`](FORTSCHREIBUNG_2026-08-14_Z_I_MERGE.md)
4. [`ARBEITSSTAND_2026-08-14_Z_I_SYMBOLBIBLIOTHEK.md`](ARBEITSSTAND_2026-08-14_Z_I_SYMBOLBIBLIOTHEK.md)
5. Danach für den breiteren Projektkontext: [`ARBEITSSTAND_2026-08-13_GESAMT_HANDOVER.md`](ARBEITSSTAND_2026-08-13_GESAMT_HANDOVER.md)

## Aktueller RCBO-/FI-LS-Endstand

Die Typ-A-RCBO-Familie `Z_RCBO_1P_N:RCBO_1P_N` ist jetzt vollständig erweitert und visuell korrigiert:

- `1P+N` und `2P` werden im Projekt als gemeinsame Bauart geführt;
- kein separates zweites 2P-Symbol;
- 64 Typ-A-Planungsvarianten;
- Nennstrom 6/10/13/16/20/25/32/40 A;
- Bemessungsdifferenzstrom 10/30 mA;
- Kennlinie B/C;
- Ausschaltvermögen 6/10 kA;
- Typ A;
- PR #248 erfolgreich gemergt.

Die RCBO-Symbolgrafik wurde anhand der abgestimmten Referenz neu aufgebaut. Enthalten sind insbesondere Testkreis `T/E`, mechanisch gekoppelte Kontakte, Überstromauslöser im L-Zweig, Summenstromwandler, rechter Fehlerstrom-/Betätigungsblock und die Klemmenkennzeichnung `1 / 3 N / 2 / 4 N`.

PR #249 wurde erfolgreich gemergt; Squash-Merge:

```text
99aee707ab975e4ba9d7c536c7012c9434417798
```

Abschlussprüfung:

- 7/7 RCBO-spezifische Tests bestanden;
- 934/934 Gesamttests bestanden;
- Bibliotheksvalidator: 0 Fehler;
- ProjectOS: 10/10 Prüfungen bestanden;
- 75 Symbolvorschauen aktuell;
- 285 generierte Gerätevarianten aktuell;
- Gerätekatalog: 287 Gerätedateien / 19 Familien / 0 Fehler.

## Aktueller Z_I-Endstand

`Z_I_ElectricalComponents` v14 ist in `main` integriert:

- 52 Top-Level-Symbole
- 254 KiCad-Pindefinitionen
- PR #247 erfolgreich gemergt
- Squash-Merge `bc7d74c4d8cba31bfbf22ae644c64e6d3e1dc29a`
- PR-CI Run #698: SUCCESS
- nachgelagerte Main-CI Run #701: SUCCESS

Der Repository-Overlap-Audit ist ebenfalls abgeschlossen:

- **8 direkte Funktionsdubletten** zu bestehenden kanonischen Z_-Symbolen;
- **3 strukturelle Schütz-Overlaps**;
- **41 Symbole ohne direktes kanonisches Gegenstück im aktuellen Repository**.

Die vorhandenen kanonischen Bibliotheken wie `Z_MCB`, `Z_RCD`, `Z_CONTACTOR`, `Z_FUSE`, `Z_Motor_Protection`, `Z_RCBO_1P_N` und `Z_Terminal_Block` bleiben weiterhin die Projekt-Baselines. `Z_I_ElectricalComponents` bleibt zunächst Import-/Quellbibliothek.

## Wichtige offene Qualitätsarbeit

Die 41 neuen Z_I-Abdeckungen werden nicht automatisch als kanonisch freigegeben. Vor einer Promotion sind insbesondere zu prüfen beziehungsweise zu normalisieren:

1. 100-mil-Pin-/Anschlussraster;
2. Standard-Pinlänge 100 mil statt der häufig quellbedingt verwendeten 50 mil;
3. ERC-Pintypen nur mit belegter elektrischer Semantik;
4. Benennung von `1P+N` / `3P+N` statt rein numerischer Varianten, wo fachlich zutreffend;
5. `Z_Footprint_Policy = none` für die fünf eindeutig virtuellen Pfeil-/Potential-Symbole;
6. Projekt-/Taxonomie-Scope und mögliche Überschneidung mit offiziellen KiCad-Standardbibliotheken bei allgemeinen Elektronik-Basissymbolen.

## Nächster verbindlicher Arbeitsschritt

1. **Lokaler KiCad-Ladetest** der in `main` integrierten Bibliotheken.
2. RCBO-Symbol in KiCad platzieren und Klemmen `1 / 3 N / 2 / 4 N` sowie Anschlussfangpunkte visuell prüfen.
3. Alle 52 Z_I-Symbole auswählbar/anzeigbar prüfen.
4. `Contactor_3P_1NO_1NC` mit allen vier Units prüfen.
5. Potentiale, Textausrichtung und Anschlussfangpunkte prüfen.
6. Danach gezielte **v15-Normalisierungsplanung** für die wirklich neuen Kandidaten; bestehende kanonische Dubletten nicht blind neu zeichnen.
7. Anschließend wieder in den breiteren Projekt-Backlog aus dem Gesamt-Handover vom 13.08.2026 einsteigen.

`main` bleibt die Single Source of Truth. Bei Widersprüchen zwischen historischen Handovers und dem aktuellen Repository gilt der aktuelle Repository-Stand.