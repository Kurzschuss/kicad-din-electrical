# Arbeitsstand / Chat-Übergabe – MCB und Z_Cockpit

Stand: 2026-08-10  
Repository: `Kurzschuss/kicad-din-electrical`  
Maßgeblicher Entwicklungsstand: `main` nach Merge von PR #175  
Aktueller `main`-Merge-Commit aus PR #175: `652fadcd8067320cdbfb720597a7d5dfb02c6fe6`

## Zweck dieses Handovers

Dieser Handover ist die Fortsetzungsgrundlage für einen neuen Chat. Er dokumentiert den realen Stand nach den zuletzt abgeschlossenen MCB- und Z_Cockpit-Arbeiten. Bei Abweichungen zwischen älteren Chat-Zusammenfassungen und dem Repository gilt der aktuelle `main`-Stand als Single Source of Truth.

Der ältere Handover `PROJECTOS_ZWISCHENSTAND_2026-08-09.md` betrifft einen früheren ProjectOS-Zwischenstand und ist für die hier dokumentierte MCB-/Z_Cockpit-Arbeit nicht maßgeblich.

## 1. MCB / Leitungsschutzschalter – final freigegebener Stand

Die Symbolgeometrie ist vom Benutzer ausdrücklich visuell freigegeben worden (`so ist es in ordnung`). Deshalb im nächsten Chat **keine weitere MCB-Geometrieänderung ohne neuen ausdrücklichen Benutzerwunsch**.

### 1P

Technische Symbol-ID bleibt stabil:

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
- der freie linke Trennungsstrich wurde zuletzt auf 75 mil verlängert;
- der Leerraum zum rechten Kontaktstrich wurde auf 50 mil vergrößert;
- rechter Kontaktstrich bleibt am jeweiligen schrägen Schaltkontakt angeschlossen;
- 3P-Gesamtbreite 1000 mil als dokumentierte Z_MCB-Ausnahme; die globale 800-mil-Zielregel wurde nicht stillschweigend geändert.

Letzter MCB-Feinschliff: PR #174 `MCB 3P: Trennungsstriche feinabstimmen`, gemergt mit Commit `327fd176a52298c4daf724700634683bed9b0c25`.

### MCB-Varianten

Die 3P-Serie wird datengetrieben erzeugt, nicht als 42 manuell kopierte Symbolkörper.

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

## 2. Z_Cockpit – Stand nach PR #175

PR #175: `Z_Cockpit: Bibliotheken als filterbare Tabellenansicht`

Status:

- gemergt;
- Merge-Commit: `652fadcd8067320cdbfb720597a7d5dfb02c6fe6`;
- finaler PR-Head: `93b80aa2f643c5a65ab2d61bc85ad82dc8580769`;
- finaler CI-Lauf: `ProjectOS complete test suite` Run #468 = **SUCCESS**.

### Geräteansicht

Der unnötige obere Leerraum wurde reduziert:

- Seite `Geräte` hat kein zusätzliches äußeres Seiten-Padding mehr;
- `device-main` und `details` verwenden kompakteres oberes Padding;
- die H2-Überschriften beginnen ohne zusätzlichen oberen Standardabstand.

Die bestehende Excel-artige Geräteansicht bleibt erhalten:

- Filter-Dropdowns;
- tabellarische Geräteliste;
- Zeilenauswahl;
- Detailbereich rechts;
- Symbol-/Footprint-Vorschau.

### Bibliotheksansicht

Die Bibliotheksansicht wurde an die Bedienlogik der Geräteansicht angeglichen.

Oben bleibt die kompakte Zusammenfassung sichtbar:

- Bibliotheken;
- Symbole;
- Gerätezuordnungen;
- Footprints;
- Vorschaupaare.

Darunter befindet sich jetzt eine Excel-artige Arbeitsansicht mit:

- Filter `Bibliothek`;
- Filter `Symbole vorhanden`;
- Filter `Gerätezuordnung`;
- Filter `Footprints`;
- Filter `Vorschauen`;
- tabellarischer Bibliotheksliste;
- Zeilenauswahl;
- Bibliotheksdetails rechts;
- Symboltabelle der ausgewählten Bibliothek;
- sichtbarer Ergebnisanzahl;
- festem oberen Summary-Bereich und scrollbar gehaltenem unteren Arbeitsbereich.

Bestehende Sicherheits-/Layoutverträge wurden beibehalten:

- Repositorydaten werden HTML-escaped;
- der bisherige `library-list-scroll`-Vertrag bleibt bestehen;
- `library-card` bleibt als kompatibler Detailcontainer erhalten;
- das Bibliotheks-JavaScript wird explizit als `script type="text/javascript"` erzeugt, sodass der bestehende Escape-Test weiterhin nackte `<script>`-Einschleusung aus Repositorydaten erkennt.

## 3. CI-Nachweis des aktuellen UI-Standes

Finaler Lauf für PR #175: **Run #468 erfolgreich**.

Bestätigt:

- Repository Health: grün;
- vollständige Pytest-Suite: **729 passed**;
- Python-Syntaxprüfung: grün;
- Z_-Qualitätsprofil: **17 konforme Regeln**;
- KiCad-Bibliotheksvalidator: **0 Fehler**;
- Generatorcheck Gerätevarianten: **45 aktuell**;
- Gerätekatalog: **47 Gerätedateien**, **19 Gerätefamilien**, **0 Fehler**;
- Bibliotheksreferenz: aktuell;
- Qualitätsbericht: aktuell;
- Symbolvorschauen: **21 aktuell**;
- HTML-Referenz: aktuell;
- HTML-Gerätekatalog: aktuell;
- Z_Cockpit-Erzeugung: erfolgreich.

Der Bibliotheksvalidator meldet weiterhin Hinweise/Warnungen zu noch nicht hinterlegten Datenblättern/Herstellern und vorbereiteten leeren Bibliotheken. Diese sind keine Fehler und haben den Lauf nicht blockiert.

## 4. Lokaler Z_Cockpit-Generator

`docs/site/z-cockpit.html` ist absichtlich **kein versionierter Quellbestand**, sondern lokaler Generator-Output.

Die Datei steht in `.gitignore`:

```text
docs/site/z-cockpit.html
```

Daher gilt:

- lokal erzeugen und im Browser öffnen: ja;
- in GitHub Desktop committen: nein;
- nach einem Generatorlauf soll sie nicht als regulärer Repository-Change erscheinen.

Lokaler Befehl unter Windows/PowerShell:

```powershell
.\.venv\Scripts\python.exe -m tools.generate_z_cockpit
```

Danach im Browser `Strg+F5` für einen harten Reload.

## 5. Bekannte lokale Windows-Besonderheit

Im Benutzer-Setup war `git` in PowerShell nicht im PATH. GitHub Desktop enthält aber ein funktionierendes Git unter seinem eigenen Installationspfad. Für normale Arbeit bevorzugt GitHub Desktop (`Fetch origin` / `Pull origin`). Für Python-/Generatorbefehle funktioniert das VS-Code-PowerShell-Terminal.

`build/`, `__pycache__/`, `.pytest_cache/` und `.venv/` sind lokale/ignorierte Arbeitsartefakte und sollen nicht committed werden.

## 6. Exakt nächster Schritt im neuen Chat

**Kein neuer MCB-Fix.** Die MCB-Darstellung ist freigegeben.

Als erstes beim Benutzer lokal:

1. GitHub Desktop: `Fetch origin`;
2. GitHub Desktop: `Pull origin`;
3. im Repository ausführen:

   ```powershell
   .\.venv\Scripts\python.exe -m tools.generate_z_cockpit
   ```

4. Browser mit `Strg+F5` neu laden;
5. visuell prüfen:
   - `Geräte`: oberer Leerraum deutlich reduziert;
   - `Bibliotheken`: feste Zusammenfassung oben;
   - darunter Excel-artige Bibliothekstabelle;
   - Dropdown-Filter funktionieren;
   - Zeile auswählen → Bibliotheksdetails rechts;
   - Symboltabelle im Detailbereich sichtbar;
   - unterer Bereich scrollbar.

Wenn diese Ansicht vom Benutzer bestätigt wird, gilt PR #175 auch visuell als abgenommen. Danach erst den nächsten fachlichen Z_Cockpit-/Bibliotheksausbau festlegen.

## 7. Letzte relevante PR-Kette

Für Rückfragen zur Entstehung der MCB-Darstellung:

- #163: 3P-MCB-Familie / B-C-D-Stromvarianten;
- #164, #167, #168, #169, #170, #171, #172, #173: schrittweise MCB-Geometrie-/Preview-Korrekturen;
- #174: finaler 3P-Trennungsstrich-/Abstands-Feinschliff, anschließend vom Benutzer freigegeben;
- #175: Z_Cockpit-Bibliotheken als filterbare Tabellenansicht + kompaktere Geräteansicht.

Die PR-Kette ist bereits in `main` enthalten.
