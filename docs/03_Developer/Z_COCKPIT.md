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
- Qualität;
- Sicherheit.

Registriert, aber noch nicht umgesetzt:

- Hersteller;
- Diagnose;
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

## Projektstatus und Qualität

Die Startseite liest das zentrale Projektmodell aus `project_state.yaml` und zeigt Projektfortschritt, nächste Aufgaben und Projektbestandteile.

Die Qualitäts- und Sicherheitsseiten sind sichtbar angebunden. Der im Projektmodell als nächster `planned` geführte Punkt ist derzeit:

- `Projektanalyse und Konsistenzprüfung umsetzen` (`projektvalidator`).

Der GitHub-Ruleset-Punkt bleibt separat als `blocked` geführt.

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
- eindeutige Seiten-IDs;
- zentrale Seitenregistrierung;
- Projektstatus-, Qualitäts- und Sicherheitsintegration;
- HTML-Escaping von Repositorydaten.

GitHub Actions erzeugt die Cockpit-Datei bei jedem vollständigen CI-Lauf und prüft die relevanten Repository-, Generator-, Qualitäts- und KiCad-Verträge.

## Aktueller Entwicklungsstand

Die lokale HTML-Anwendung besitzt inzwischen die grundlegende Cockpit-Struktur einschließlich Start-, Geräte-, Bibliotheks-, Qualitäts- und Sicherheitsansicht.

Weiterer fachlicher Ausbau ist noch offen bei:

- Hersteller;
- Diagnose;
- Dokumentation;
- Einstellungen;
- 3D-Vorschauen;
- direkten KiCad-Editoraufrufen.

Für die noch nicht umgesetzten Cockpit-Seiten ist aktuell keine verbindliche Reihenfolge festgelegt. Der allgemeine nächste Projektpunkt wird deshalb aus `project_state.yaml` abgeleitet.

Der aktuelle visuell freigegebene Bibliotheksstand ist zusätzlich unter `docs/handover/ARBEITSSTAND_2026-08-10_MCB_Z_COCKPIT.md` dokumentiert.
