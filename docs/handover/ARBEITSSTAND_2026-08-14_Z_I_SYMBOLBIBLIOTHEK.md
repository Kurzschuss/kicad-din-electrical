# Arbeitsstand 14.08.2026 – Z_I-Symbolbibliothek

## Zweck dieses Handovers

Dieser Handover dokumentiert die vollständige Aufbereitung der sechs gelieferten JavaScript-/SVG-Symbolmodule zur KiCad-Bibliothek `Z_I_ElectricalComponents`, die dabei getroffenen fachlichen Entscheidungen, die Qualitätsprüfungen bis v14 sowie den Stand der GitHub-Integration.

Für eine spätere Fortsetzung gilt: **nicht bei v1 anfangen und nicht erneut aus den JS-Dateien konvertieren. Ausgangspunkt ist v14.**

## Ausgangsquellen

Bearbeitet wurden genau diese sechs Module:

- `modul_verbindungen.js`
- `modul_verbraucher.js`
- `modul_elektronik.js`
- `modul_kontakte.js`
- `modul_potenziale.js`
- `modul_sicherungen.js`

Die Quellen enthalten zusammen **51 registrierte Symbole**. Zusätzlich wurde in KiCad ein zusammengesetztes Mehrfacheinheiten-Schütz erzeugt. Der Zielstand enthält deshalb **52 Top-Level-KiCad-Symbole**.

## Zielbibliothek und geprüfter Stand

Zieldatei:

`symbols/Z_I_ElectricalComponents.kicad_sym`

Technischer Stand v14:

- 51/51 ursprüngliche JS-Symbole abgedeckt
- plus `Contactor_3P_1NO_1NC`
- 52 Top-Level-Symbole
- 254 KiCad-Pindefinitionen
- 236/236 ursprüngliche JS-`.port`-Punkte auf den erwarteten KiCad-Pinpositionen
- zusätzlich 6 dokumentierte Potential-Pins als bewusste KiCad-Anpassung
- keine doppelten Top-Level-Symbolnamen
- keine doppelten Pin-IDs innerhalb der geprüften Symbole
- Klammer-/S-Expression-Struktur geprüft

Originale, geometrisch korrigierte v14-Datei aus der Arbeitsumgebung:

- SHA-256: `b621a66a7cabfcc44a61a115ca7027e06819c382ecd646fd370696c8f20565ac`

Für die Repository-Konvention wurde anschließend ausschließlich die explizite Property `Z_Footprint_Policy = optional` für alle 52 Symbole ergänzt. Geometrie und Pins wurden dabei nicht verändert.

Repository-normalisierte Fassung:

- SHA-256: `c0ed71dec0c2134e4b746c7942f3e46bb633aa2f6c09dd5b201f6bfda4c3259b`
- Git-Blob-SHA: `57826daa449799b34139cf62c80c3c4348489286`
- Größe: 207457 Byte

Diese Hashes sind der Referenzpunkt für einen späteren Upload/Abgleich.

## Enthaltene Symbolgruppen

### 01 – Verbindungen

- `Terminal_FeedThrough`
- `Arrow_Output`
- `Arrow_Input`

### 02 – Potentiale

- `Potential_L1`
- `Potential_L1_L2`
- `Potential_L1_L2_L3`

### 03 – Elektronik

- `Resistor`
- `Potentiometer`
- `LDR`
- `Capacitor`
- `Diode`
- `LED`
- `Transistor_NPN`
- `Transistor_PNP`
- `TRIAC`
- `DIAC`
- `IC_Blank_4Pin`
- `IC_Blank_6Pin`
- `IC_Blank_8Pin`
- `IC_Blank_10Pin`
- `Arduino_Uno`
- `Arduino_R4`
- `Arduino_Nano`
- `PowerSupply_ACDC`
- `Relay_Module_PCB`
- `Buzzer`
- `TerminalBlock_PCB_2P`

### 04 – Schutzgeräte

- `MCB_1P`
- `MCB_2P`
- `MCB_3P`
- `Fuse`
- `MotorProtection_3P`
- `RCD_2P`
- `RCD_4P`
- `RCBO_2P`
- `RCBO_4P`

### 05 – Verbraucher / Antriebe

- `Converter_ACAC`
- `Converter_ACDC_Rectifier`
- `PowerSupply_ACDC_PE`
- `Motor_3Ph`
- `Motor_Dahlander_6T`
- `Lamp`
- `Motor_DC`
- `Motor_AC_1Ph`
- `Heater_Resistive`

### 06 – Schaltgeräte / Kontakte

- `Contactor_MainContacts_3P`
- `Contactor_Coil`
- `PushButton`
- `Switch`
- `AuxContact_NO`
- `AuxContact_NC`
- `Contactor_3P_1NO_1NC`

## Fachliche Regeln, die beibehalten werden müssen

1. **Quelltreue vor Vermutung.** Anschlussnamen wurden nur übernommen, wenn sie in der jeweiligen JS-/SVG-Quelle eindeutig belegt waren. Es wurden keine IEC-Bezeichnungen erfunden, nur weil sie fachlich plausibel wären.
2. **ERC-Pintypen bleiben konservativ `passive`.** Die Quellen liefern keine verlässlichen ERC-Typinformationen. Eine spätere Verfeinerung ist möglich, aber nur mit belegbarer Semantik.
3. **Virtuelle Symbole bleiben virtuell.** Ein-/Ausgangspfeile sowie Potentialdarstellungen sind aus BOM/PCB ausgeschlossen.
4. **Potentiale sind ein dokumentierter Sonderfall.** `modul_potenziale.js` hat keine normalen `.port`-Punkte; dort wird über eine eigene Potential-Verbindungslogik gearbeitet. Für KiCad wurden deshalb L1/L2/L3-Pins bewusst ergänzt.
5. **Keine erfundenen Footprints.** Die importierten Symbole sind überwiegend herstellerneutral. `Z_Footprint_Policy` ist deshalb `optional`; konkrete Footprints werden erst mit belastbaren Geräte-/Herstellerdaten ergänzt.
6. **Bestehende kanonische Bibliotheken nicht ungeprüft ersetzen.** `Z_MCB`, `Z_RCD`, `Z_CONTACTOR` usw. bleiben die vorhandenen Projekt-Baselines. `Z_I_ElectricalComponents` ist zunächst eine zusätzliche Import-/Quellbibliothek. Eine spätere Promotion einzelner Z_I-Symbole in kanonische Bibliotheken braucht einen expliziten Vergleich.

## Schütz-Mehrfacheinheit

Zusätzlich zu den sechs Quellmodulen wurde `Contactor_3P_1NO_1NC` als KiCad-Mehrfacheinheiten-Symbol aufgebaut:

- Unit 1: Spule `A1/A2`
- Unit 2: Hauptkontakte `1–6`
- Unit 3: Schließer `13–14`
- Unit 4: Öffner `21–22`

Die Einzel-Symbole bleiben daneben erhalten.

## Wichtige Korrekturen im Verlauf v1 bis v14

Die Bibliothek wurde nicht nur einmal konvertiert, sondern in mehreren Qualitätsstufen bereinigt:

- v1: erste vollständige KiCad-Konvertierung der 51 Quellsymbole
- v2: einheitliche Symbolnamen / sprechende IEC-/DIN-orientierte Namen
- v3: virtuelle Symbole korrekt aus BOM/PCB ausgeschlossen, Kategorien und Metadaten ergänzt
- v4: Mehrfacheinheiten-Schütz `Contactor_3P_1NO_1NC`
- v5: Schutzgeräte-Anschlussbezeichnungen korrigiert und vereinheitlicht
- v6: Verbraucher/Antriebe gegen die tatsächlichen Quelllabels geprüft
- v7: Elektronik-Gruppe korrigiert; u. a. Arduino Nano A6/A7 und AC/DC-Netzteil mit PE
- v8: Verbindungen/Potentiale und 51/51-Quellabdeckung vollständig geprüft
- v9: wartbare Produktionsfassung mit stabilem Bibliotheksnamen und Validierungsskript
- v10: KiCad-Testprojekt mit Übersicht + sechs Gruppenblättern vorbereitet
- v11: Release-/Qualitätsdokumentation und bibliotheksübergreifender Testabgleich
- v12: visueller Katalog aller 51 Quellsymbole
- v13: JS-SVG ↔ KiCad-Geometrievergleich
- v14: die beim Geometrievergleich gefundenen Abweichungen korrigiert

v14 korrigierte insbesondere:

- 22 gestrichelte Linien, die zuvor als Volllinien vorlagen
- 6 falsche Konturstärken
- 203 Textdefinitionen hinsichtlich Lage/Ausrichtung/Rotation
- vertikale Beschriftung von `UNO`, `R4`, `NANO`

Acht SVG-`path`/`ellipse`-Sonderfälle bleiben KiCad-Approximationen; sie wurden zusätzlich visuell geprüft.

## GitHub-Integrationsstand am 14.08.2026

Repository:

`Kurzschuss/kicad-din-electrical`

Angelegter Integrations-Branch:

`agent/import-z-i-electricalcomponents-v14`

Vor der Integration wurde geprüft:

- `symbols/Z_I_ElectricalComponents.kicad_sym` existierte auf `main` noch nicht.
- Die gleiche Datei existierte auch auf `agent/qet-phase1-converter` noch nicht.
- `docs/00_Project/LIBRARY_GUIDELINES.md` verlangt für neue/überarbeitete Z_-Bibliotheken eine explizite Footprint-Policy.
- `tools/validate_libraries.py` erwartet für eine `symbols/Z_*.kicad_sym` eine gleichnamige `.pretty`-Bibliothek.
- Deshalb ist als Begleitpfad vorgesehen: `footprints/Z_I_ElectricalComponents.pretty/` – zunächst bewusst ohne erfundene konkrete Footprints.

### Wichtiger technischer Blocker

Der ChatGPT-GitHub-Connector hat sowohl den Low-Level-Git-Blob-Upload der 207-kB-Datei als auch den Upload größerer KiCad-Textsegmente durch seinen Sicherheitslayer blockiert (`Sicherheitsstatus der Anfrage konnte nicht bestimmt werden`). Diese Sperre wurde **nicht umgangen und nicht abgeschwächt**.

Daraus folgt: **Zum Zeitpunkt dieses Handovers ist die v14-Bibliothek noch nicht als `symbols/Z_I_ElectricalComponents.kicad_sym` im Repository materialisiert.** Der Integrations-Branch und diese Dokumentation existieren, die große Bibliotheksdatei selbst muss in einer Git-fähigen lokalen Umgebung oder über einen zulässigen Datei-Upload nachgezogen werden.

## Exakter nächster Integrationsschritt

In einer lokalen Git-Arbeitskopie auf Basis des Integrations-Branches:

1. Die repository-normalisierte v14-Datei als `symbols/Z_I_ElectricalComponents.kicad_sym` ablegen.
2. SHA-256 prüfen: `c0ed71dec0c2134e4b746c7942f3e46bb633aa2f6c09dd5b201f6bfda4c3259b`.
3. `footprints/Z_I_ElectricalComponents.pretty/README.md` anlegen; keine Footprints erfinden.
4. Repository-Generatoren/Prüfungen ausführen:
   - `python tools/validate_libraries.py`
   - `python tools/generate_library_reference.py`
   - `python tools/generate_symbol_previews.py`
   - `python tools/generate_quality_report.py`
   - `python -m tools.generate_html_reference`
   - `python tools/generate_3d_previews.py`
   - anschließend die vollständige Test-Suite des Repositories
5. Generierte Referenzen/Vorschauen mit committen, falls die Repository-Checks Änderungen verlangen.
6. PR `agent/import-z-i-electricalcomponents-v14` → `main` erstellen.
7. Erst bei grüner CI nach `main` mergen.

## Danach fachlich weitermachen

Nach erfolgreicher Materialisierung und grüner CI ist der nächste sinnvolle Arbeitsblock:

1. **Lokaler KiCad-Ladetest** aller 52 Symbole, inklusive aller vier Units des zusammengesetzten Schützes.
2. **Overlap-Audit** gegen bestehende kanonische Bibliotheken (`Z_MCB`, `Z_RCD`, `Z_CONTACTOR`, weitere Z_-Pakete).
3. Entscheiden, welche Z_I-Symbole dauerhaft als Importbibliothek bleiben und welche nach fachlicher Prüfung in kanonische Einzelbibliotheken überführt werden.
4. ERC-Pintypen nur dort verfeinern, wo die elektrische Funktion eindeutig belegt ist.
5. Hersteller-/Footprint-Metadaten nur aus belastbaren Quellen ergänzen.
6. Danach wieder in den allgemeinen Projekt-Backlog aus dem Gesamt-Handover vom 13.08.2026 einsteigen.

## Kurzfassung für die nächste Sitzung

**Startpunkt:** v14, nicht erneut konvertieren. 52 Symbole / 254 Pins. Repository-normalisierte SHA-256 `c0ed71dec0c2134e4b746c7942f3e46bb633aa2f6c09dd5b201f6bfda4c3259b`. Integrations-Branch `agent/import-z-i-electricalcomponents-v14`. Als erstes die große `.kicad_sym` lokal in den Branch materialisieren, Repository-Generatoren laufen lassen, CI grün bekommen und dann nach `main` mergen. Danach KiCad-Sichtprüfung und Overlap-Audit.