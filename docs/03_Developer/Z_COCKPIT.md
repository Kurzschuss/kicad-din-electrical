# Z_Cockpit erzeugen und testen

`Z_Cockpit` ist die zentrale, tabellenbasierte Bibliotheks- und Geräteübersicht der KiCad DIN Electrical Suite.

Die angezeigten Geräte werden nicht in der Oberfläche doppelt gepflegt. Der technische Gerätekatalog unter `data/devices/` bleibt die einzige Datenquelle.

## Erzeugen

```text
python -m tools.generate_z_cockpit
```

Die Ausgabe wird hier abgelegt:

```text
docs/site/z-cockpit.html
```

`docs/site/z-cockpit.html` ist ein **lokal erzeugtes Arbeitsartefakt**. Die Datei wird über `.gitignore` ausgeschlossen und nicht committed.

Der Modulaufruf ist verbindlich, weil der Generator gemeinsame Funktionen aus dem Python-Paket `tools` verwendet.

## Unter Windows öffnen

```text
tools\windows\open_z_cockpit.bat
```

Alternativ direkt aus PowerShell mit der Projektumgebung:

```powershell
.\.venv\Scripts\python.exe -m tools.generate_z_cockpit
```

Danach im Browser bei Bedarf `Strg+F5` für einen harten Reload.

## Modulare Seitenarchitektur

Die zentrale Seitendefinition liegt unter:

```text
tools/z_cockpit/pages.py
```

Jede Seite besitzt:

- eine stabile technische Seiten-ID;
- eine deutsche Bezeichnung;
- eine deutsche Kurzbeschreibung;
- einen Status, ob die Seite bereits umgesetzt ist.

Aktuell umgesetzt:

- Start;
- Geräte;
- Bibliotheken;
- Hersteller;
- Qualität;
- Diagnose;
- Sicherheit.

Registriert, aber noch nicht umgesetzt:

- Dokumentation;
- Einstellungen.

Die Seitenregistrierung ist die verbindliche Grundlage für Navigation, Tests und spätere Erweiterungen. Neue Bereiche werden dort ergänzt, statt unabhängige Einzeloberflächen anzulegen.

## Geräteansicht

Die Geräteansicht ist tabellenbasiert und enthält:

- Filter für Gerätefamilie, Hersteller, Polzahl, Charakteristik, Nennstrom und Status;
- technische Geräte-ID;
- Symbol- und Footprint-Zuordnung;
- Zeilenauswahl;
- statischen Eigenschaftenbereich rechts;
- Symbolvorschau;
- Footprintvorschau bzw. technischen Vorschau-/Statushinweis.

## Bibliotheksansicht

Die Bibliotheksansicht verwendet dieselbe tabellenorientierte Bedienlogik.

Der obere Bereich enthält keine separaten Summary-Kacheln mehr. Die Gesamtwerte stehen in den Filterbezeichnungen.

Fest im oberen Bereich bleiben:

- Überschrift und Kurzbeschreibung;
- `Bibliotheksliste`;
- Filter.

Nur die Bibliothekstabelle scrollt.

Ein Klick auf eine Bibliothekszeile öffnet direkt darunter den Bibliotheksdetailbereich mit Symboltabelle. Es ist immer nur eine Bibliothek gleichzeitig geöffnet.

Rechts befindet sich ein dauerhaft verankerter Eigenschaftenbereich für das ausgewählte Symbol. Dort werden angezeigt:

- Bibliothek;
- Symbol;
- Geräteanzahl;
- Footprint;
- Symbolvorschau;
- Geräte-IDs.

Die Eigenschaften und die Symbolvorschau bleiben fest stehen. Die Geräte-IDs liegen darunter in einem eigenen vertikal scrollbareren Bereich. Lange IDs werden umgebrochen; die Symboltabelle muss deshalb nicht wegen der Geräte-IDs horizontal erweitert werden.

Beim Öffnen einer Bibliothek wird das erste Symbol automatisch ausgewählt. Andere Symbolzeilen können per Maus sowie Enter/Leertaste gewählt werden.

## Herstelleransicht

Die Herstellerseite ist eine read-only Auswertung des technischen Gerätekatalogs. Sie führt keine zweite Herstellerdatenbank ein.

Aus den vorhandenen Gerätedaten werden dynamisch aggregiert:

- Hersteller;
- Produktserien;
- Geräteanzahl je Hersteller und Serie;
- zugeordnete Gerätefamilien;
- Quellenstatus;
- technische Geräte-IDs.

`Generic` wird in der Oberfläche als `Herstellerneutral` angezeigt, während der originale Katalogwert im Eigenschaftenbereich sichtbar bleibt.

Der linke Bereich enthält eine filterbare Herstellertabelle mit Filtern für Hersteller, Serie, Gerätefamilie und Quellenstatus. Ein ausgewählter Hersteller wird rechts in einem festen Eigenschaftenbereich dargestellt. Dort stehen die Serienübersicht sowie darunter eine separat scrollbarere Liste der zugeordneten Geräte-IDs.

Die bestehenden ProjectOS-Domänenmodelle `Manufacturer`, `ProductSeries` und `ManufacturerProduct` bleiben davon getrennt. Die Cockpit-Seite liest ausschließlich den bestehenden Gerätekatalog; spätere persistierte Herstellerverwaltung kann auf diesen Domainobjekten aufbauen, ohne die Katalogauswertung zu duplizieren.

## Diagnoseansicht

Die Diagnose-Seite ist eine read-only Arbeitsliste für bereits erkannte Repositorybefunde. Sie führt keine automatische Reparatur aus.

Sie verbindet zwei bestehende Prüfpfade:

- den **ProjectOS-Projektvalidator** mit den stabilen `PRJ-*`-Prüfungen für Projektmodell, Bibliotheken, Gerätekatalog, Generatorstände und Cockpit-Struktur;
- die bereits vorhandene **repositoryweite Projektanalyse** für Geräte-IDs, Symbolreferenzen, Footprints, Symbol-/Footprintvorschauen und ungenutzte Symbole.

Die Befunde werden nach Fehlern und Warnungen priorisiert und können nach Status, Quelle und Bereich gefiltert werden. Ein ausgewählter Befund zeigt rechts dauerhaft Prüfcode, Referenz, Meldung, zusätzliche Details und die vorhandene Reparaturempfehlung.

Die ProjectOS-Wissensgraph-Diagnostik unter `distributions/projectos_knowledge_diagnostics.py` und `distributions/z_cockpit_diagnostics_worklist.py` bleibt ein separater Laufzeitpfad. Da das statisch erzeugte Z_Cockpit derzeit keine persistierte `ProjectOSProjectMemory`-Instanz lädt, werden dort keine Laufzeitbefunde erfunden. Eine spätere Persistenzanbindung kann diese Diagnosen ergänzen.

## Projektstatus und Qualität

Die Startseite liest das zentrale Projektmodell aus `project_state.yaml` und zeigt Projektfortschritt, nächste Aufgaben und Projektbestandteile.

Die Qualitätsseite verbindet zwei Ebenen:

- **Projektkonsistenz** aus `tools.project_validator` mit stabilen `PRJ-*`-Prüfungen;
- **Bibliotheksgesundheit** aus der bestehenden Quality Engine für Gerätezuordnungen, Footprints und Vorschauen.

Der Projektvalidator prüft Projektmodell, Bibliotheken, Gerätekatalog, Generatorstände, HTML-Ausgaben, Symbolvorschauen und das zentrale Cockpit-Seitenmodell. Details und CLI-Aufruf sind in `docs/03_Developer/PROJECT_VALIDATOR.md` dokumentiert.

Der Projektpunkt `Projektanalyse und Konsistenzprüfung umsetzen` (`projektvalidator`) ist erledigt. Hersteller- und Diagnoseansicht sind ebenfalls als abgeschlossene Cockpit-Bausteine im zentralen Projektmodell dokumentiert. Der GitHub-Ruleset-Punkt bleibt separat als `blocked` geführt.

## Prüfung

Die automatisierten Tests prüfen unter anderem:

- Übernahme der echten Kataloggeräte;
- deutsche Standardanzeige;
- Gerätefilter und technische Geräte-ID;
- Symbol- und Footprint-Zuordnung;
- Bibliotheksfilter;
- aufklappbare Bibliotheksdetails;
- statischen Symbolinspektor;
- separates Scrollverhalten der Geräte-ID-Liste;
- Hersteller-/Serienaggregation aus dem Gerätekatalog;
- Herstellerfilter und statischen Herstellerinspektor;
- Diagnoseaggregation aus Projektvalidator und Projektanalyse;
- Diagnosefilter, Detailinspektor und HTML-Escaping;
- eindeutige Seiten-IDs;
- zentrale Seitenregistrierung;
- Projektstatus-, Qualitäts- und Sicherheitsintegration;
- Projektvalidator und maschinenlesbaren Konsistenzbericht;
- HTML-Escaping von Repositorydaten.

GitHub Actions erzeugt die Cockpit-Datei bei jedem vollständigen CI-Lauf und prüft die relevanten Repository-, Generator-, Qualitäts- und KiCad-Verträge. Zusätzlich wird `build/Z_PROJECT_VALIDATION.json` als maschinenlesbarer Projektvalidator-Bericht erzeugt.

## Aktueller Entwicklungsstand

Die lokale HTML-Anwendung besitzt inzwischen die grundlegende Cockpit-Struktur einschließlich Start-, Geräte-, Bibliotheks-, Hersteller-, Qualitäts-, Diagnose- und Sicherheitsansicht.

Weiterer fachlicher Ausbau ist noch offen bei:

- Dokumentation;
- Einstellungen;
- 3D-Vorschauen;
- direkten KiCad-Editoraufrufen;
- Persistenzanbindung für Laufzeitdiagnosen.

Für die noch nicht umgesetzten Cockpit-Seiten ist aktuell keine verbindliche Reihenfolge festgelegt. Sie werden deshalb nicht automatisch als nächster Entwicklungsschritt ausgewählt.

Der aktuelle visuell freigegebene Bibliotheksstand ist zusätzlich unter `docs/handover/ARBEITSSTAND_2026-08-10_MCB_Z_COCKPIT.md` dokumentiert.
