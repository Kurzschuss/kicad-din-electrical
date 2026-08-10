# Arbeitsstand / Chat-Übergabe – MCB und Z_Cockpit

Stand: 2026-08-10, Tagesabschluss  
Repository: `Kurzschuss/kicad-din-electrical`  
Maßgeblicher Entwicklungsstand: `main` nach Merge von PR #180  
Aktueller `main`-Merge-Commit: `497f597cbc576ca041552fe651d5daa990e4ab16`

## Zweck dieses Handovers

Dieser Handover ist die Fortsetzungsgrundlage für den nächsten Chat. Er dokumentiert den realen Repository-Stand nach den heute abgeschlossenen MCB- und Z_Cockpit-Arbeiten. Bei Abweichungen zwischen Chat-Zusammenfassungen und Repository gilt `main` als Single Source of Truth.

Der ältere Handover `PROJECTOS_ZWISCHENSTAND_2026-08-09.md` bleibt als historischer ProjectOS-Zwischenstand erhalten. Für die aktuelle MCB-/Z_Cockpit-Arbeit ist dieses Dokument maßgeblich.

## 1. MCB / Leitungsschutzschalter – final freigegebener Stand

Die MCB-Symbolgeometrie wurde vom Benutzer ausdrücklich visuell freigegeben. Deshalb im nächsten Chat **keine weitere MCB-Geometrieänderung ohne neuen ausdrücklichen Benutzerwunsch**.

### 1P

Technische Symbol-ID:

- `Z_MCB:MCB`

Freigegebene Darstellung:

- Anschluss `1` oben und `2` unten;
- rechter vertikaler Anschlussstrang;
- langer schräger Schaltkontakt;
- linker Betätigungs-/Auslösepfad mit mittig angesetztem senkrechtem Abschluss;
- diagonal ausgerichteter Pfeil mit freigegebener Pfeilspitze;
- Pfeilschaft liegt ohne sichtbare Lücke am schrägen Schaltkontakt an;
- 1P-Referenzbreite 400 mil;
- vorhandene Z_-Regeln bleiben maßgeblich.

### 3P

Technische Symbol-ID:

- `Z_MCB:MCB_3P`

Freigegebene Darstellung:

- Anschluss-Paare `1/2`, `3/4`, `5/6`;
- 300-mil-Polabstand;
- gleiche freigegebene Schalt-/Pfeilgeometrie auf allen drei Polen;
- vollständiger linker Betätigungsweg nur am ersten Pol;
- zwischen Pol 1–2 und Pol 2–3 jeweils zwei sichtbare waagrechte Segmente;
- freier linker Trennungsstrich 75 mil;
- Leerraum zum rechten Kontaktstrich 50 mil;
- rechter Kontaktstrich bleibt am jeweiligen schrägen Schaltkontakt angeschlossen;
- 3P-Gesamtbreite 1000 mil als dokumentierte Z_MCB-Ausnahme.

Letzter MCB-Feinschliff: PR #174 `MCB 3P: Trennungsstriche feinabstimmen`, Merge-Commit `327fd176a52298c4daf724700634683bed9b0c25`.

### MCB-Varianten

Die 3P-Serie wird datengetrieben erzeugt.

Auslösecharakteristiken:

- B
- C
- D

Nennströme:

- 2 A
- 4 A
- 6 A
- 10 A
- 13 A
- 16 A
- 20 A
- 25 A
- 32 A
- 40 A
- 50 A
- 63 A
- 80 A
- 125 A

Damit existieren 42 3P-Varianten. Die CI meldet insgesamt 45 erzeugte Gerätevarianten als aktuell.

## 2. Z_Cockpit – heute abgeschlossener Stand

Die aktuelle Bibliotheksansicht wurde am Ende der Sitzung vom Benutzer ausdrücklich visuell bestätigt: **`so passt es`**.

Damit gilt der Stand nach PR #180 als fachlich und visuell abgenommen.

### Geräteansicht

Die bestehende Excel-artige Geräteansicht bleibt unverändert erhalten:

- Filter-Dropdowns;
- tabellarische Geräteliste;
- Zeilenauswahl;
- statischer Eigenschaftenbereich rechts;
- Symbol-/Footprint-Vorschau;
- kompakter oberer Seitenabstand.

### Bibliotheksansicht – oberer Bereich

Die fünf früheren Summary-Kacheln wurden entfernt.

Die Gesamtwerte stehen jetzt direkt in den Filterbezeichnungen:

- `Bibliothek (29)`;
- `Symbole vorhanden (21)`;
- `Gerätezuordnung (47)`;
- `Footprints (1)`;
- `Vorschauen (1)`.

Die Beschreibung steht klein und in Klammern direkt hinter `Bibliotheken`.

Beim Scrollen bleiben fest:

- Überschrift;
- `Bibliotheksliste`;
- Filterbereich.

Nur der eigentliche Tabellenbereich scrollt.

### Bibliotheksansicht – aufklappbare Bibliotheken

Ein Klick auf eine Bibliothekszeile öffnet direkt darunter den Detailbereich.

Verhalten:

- immer nur eine Bibliothek gleichzeitig geöffnet;
- Klick auf eine andere Bibliothek schließt die bisherige und öffnet die neue;
- erneuter Klick auf die aktive Bibliothek schließt sie;
- Filter schließen eine geöffnete Bibliothek, wenn sie dadurch ausgeblendet wird;
- Tastaturbedienung mit Enter/Leertaste und `aria-expanded` bleibt vorhanden.

Im aufgeklappten Bereich stehen:

- Bibliothekskennzahlen;
- Symboltabelle;
- Symbolauswahl.

### Bibliotheksansicht – statischer Eigenschaftenbereich rechts

Der rechte Bereich ist nach dem Vorbild der Geräteansicht dauerhaft im Cockpit verankert.

Beim Öffnen einer Bibliothek wird automatisch das erste Symbol ausgewählt. Ein Klick auf ein anderes Symbol aktualisiert den rechten Bereich.

Oben im rechten Bereich bleiben fest:

- `Eigenschaften`;
- Bibliothek;
- Symbol;
- Geräteanzahl;
- Footprint;
- Symbolvorschau.

Darunter befindet sich `Geräte-IDs` in einem **eigenen vertikal scrollbareren Bereich**.

Wichtig:

- die Geräte-IDs wurden aus der breiten Symboltabelle entfernt;
- deshalb ist kein horizontales Scrollen wegen langer IDs mehr nötig;
- lange IDs werden umgebrochen;
- nur die Geräte-ID-Liste scrollt vertikal;
- der Eigenschaften-/Vorschaubereich bleibt stehen;
- die Bibliotheksliste links behält ihr eigenes, bereits bestätigtes Scrollverhalten.

## 3. Relevante PR-Kette der heutigen Z_Cockpit-Abnahme

### PR #175 – Bibliotheken als filterbare Tabellenansicht

- Merge-Commit: `652fadcd8067320cdbfb720597a7d5dfb02c6fe6`
- finaler CI-Lauf #468: **SUCCESS**

### PR #177 – Bibliothekskopf kompakter und Liste fixieren

- Summary-Kacheln entfernt;
- Kennzahlen in Filterbezeichnungen übernommen;
- Beschreibung hinter Überschrift verschoben;
- Kopf/Filter fest, Tabellenbereich scrollbar.
- Merge-Commit: `ec5452b34ec03b24eeb6d4c031ae25d66b546e81`
- finaler CI-Lauf #473: **SUCCESS**

### PR #178 – Bibliotheksdetails direkt in der Liste aufklappen

- rechter Bibliotheksdetailkasten entfernt;
- Bibliotheksdetails und Symboltabelle direkt unter der gewählten Bibliothekszeile;
- Merge-Commit: `7ddd6b0b3334b04fd1f527d47afc862fc2e65451`
- finaler CI-Lauf #476: **SUCCESS**

### PR #179 – Symbolvorschau und Geräte-IDs im rechten Inspektor

- statischer Eigenschaftenbereich rechts ergänzt;
- Symbolvorschau dort angezeigt;
- Geräte-IDs aus der Symboltabelle entfernt und rechts als Liste dargestellt;
- Merge-Commit: `932f04c9b3af189c35117faa0b32e97612626bac`
- finaler CI-Lauf #479: **SUCCESS**

### PR #180 – Eigenschaften fixieren und Geräte-IDs separat scrollen

- rechter Eigenschaftenbereich fest verankert;
- Eigenschaften und Symbolvorschau bleiben stehen;
- nur Geräte-IDs scrollen vertikal;
- Merge-Commit: `497f597cbc576ca041552fe651d5daa990e4ab16`
- finaler CI-Lauf #481: **SUCCESS**
- anschließend vom Benutzer visuell bestätigt: **`so passt es`**

## 4. CI-Nachweis des aktuellen Endstands

Finaler Lauf für PR #180: `ProjectOS complete test suite` Run #481 = **SUCCESS**.

Damit sind insbesondere erfolgreich gelaufen:

- Repository Health;
- vollständige Pytest-Suite;
- Python-Syntaxprüfung;
- Z_-Qualitätsprofil;
- KiCad-Bibliotheksvalidator;
- Generatorcheck Gerätevarianten;
- Gerätekatalogprüfung;
- Bibliotheksreferenz;
- Qualitätsbericht;
- Symbolvorschauen;
- HTML-Referenz;
- HTML-Gerätekatalog;
- Z_Cockpit-Erzeugung.

## 5. Lokaler Z_Cockpit-Generator

`docs/site/z-cockpit.html` ist weiterhin lokaler Generator-Output und wird nicht committed.

Unter Windows/PowerShell:

```powershell
.\.venv\Scripts\python.exe -m tools.generate_z_cockpit
```

Danach im Browser `Strg+F5`.

Für Repository-Aktualisierung bevorzugt GitHub Desktop:

1. `Fetch origin`;
2. `Pull origin`.

## 6. Was im nächsten Chat als Erstes gilt

1. `main` als Single Source of Truth verwenden.
2. Keine MCB-Geometrie ändern, solange der Benutzer das nicht ausdrücklich neu verlangt.
3. Die aktuelle Bibliotheksansicht nach PR #180 **nicht erneut grundlegend umbauen**; sie ist visuell freigegeben.
4. Vor neuer Arbeit kurz `project_state.yaml` und diesen Handover prüfen.

## 7. Dokumentierter nächster Projektpunkt

Im aktuellen `project_state.yaml` sind die Bibliotheks- und grundlegenden Z_Cockpit-Meilensteine als erledigt markiert.

Der nächste als `planned` eingetragene Projektpunkt ist:

- **`Projektanalyse und Konsistenzprüfung umsetzen`** (`projektvalidator`).

Der GitHub-Ruleset-Punkt bleibt separat als `blocked` geführt und ist nicht der nächste normale Entwicklungsschritt.

Für das Z_Cockpit sind außerdem weiterhin registriert, aber noch nicht umgesetzt:

- Hersteller;
- Diagnose;
- Dokumentation;
- Einstellungen.

Für diese vier Seiten ist im Repository derzeit **keine verbindliche Reihenfolge** festgelegt. Deshalb im nächsten Chat nicht eigenmächtig eine davon als nächste Seite auswählen. Wenn der Benutzer weiter am Z_Cockpit arbeiten möchte, zuerst kurz entscheiden, ob der dokumentierte Projektvalidator oder einer dieser sichtbaren Cockpit-Bereiche als nächster fachlicher Ausbau gewünscht ist.

## 8. Tagesabschluss 2026-08-10

Der heutige Arbeitsblock ist abgeschlossen.

Freigegeben und nicht erneut anzufassen ohne neuen Wunsch:

- MCB-Geometrie;
- aktuelle Z_Cockpit-Bibliotheksansicht einschließlich Scrollverhalten und rechtem Eigenschaftenbereich.

Nächste Sitzung beginnt mit diesem Handover und dem aktuellen `main`-Stand.
