# Arbeitsstand 2026-08-10 – Z_Cockpit Layout und Ausbau

## Visuell festgelegter Stand

Die obere Darstellung der Z_Cockpit-Seiten wird am Bibliotheksbereich ausgerichtet.

Verbindliches Muster:

```text
Menü-/Seitentitel (kurze Erklärung zum Bereich)
```

Die Erklärung steht in kleinerer, zurückhaltender Schrift direkt in derselben Überschriftszeile. Eine zusätzliche zweite Erklärungszeile unmittelbar unter dem Seitentitel soll vermieden werden.

`Einstellungen`, `Sicherheit`, `Benutzer`, `Berechtigungen` und `Fehler melden` verwenden dieses Muster direkt. Start, Qualität, Hersteller, Diagnose und Dokumentation werden im erzeugten Cockpit ebenfalls auf dieses gemeinsame Kopfzeilenmuster normalisiert.

`Geräte` und `Bibliotheken` werden strukturell nicht umgebaut. Die bereits freigegebene Bibliotheksansicht bleibt Referenz für die kompakte Kopfgestaltung.

## Nicht verändern

Ohne neue ausdrückliche Anforderung bleiben unverändert:

- freigegebene MCB-Geometrie;
- freigegebene RCD/FI-Geometrien 2P und 3+N/4P;
- Bibliotheksarbeitslogik;
- rechter Eigenschaften-/Vorschaubereich;
- separates Scrollverhalten der Geräte-ID-Listen.

## Dreistufiger Z_Cockpit-Ausbau – abgeschlossen

Die festgelegte Reihenfolge ist vollständig umgesetzt:

1. **Benutzerverwaltung – umgesetzt**
2. **Whitelist- und Berechtigungsverwaltung – umgesetzt**
3. **Issue- und Fehlermeldungsworkflow – umgesetzt**

Die fachliche Gesamtdokumentation steht in:

```text
docs/projectos/Z_COCKPIT_AUSBAU_BENUTZER_WHITELIST_ISSUES.md
```

## Benutzerverwaltung

Die vorhandenen ProjectOS-Bausteine für Benutzer, Rollen, Berechtigungen, Benutzer-Lifecycle und Rechteherkunft sind in eine eigene Z_Cockpit-Seite integriert. Ohne ProjectOS-Projektdatei werden keine Benutzer erfunden. Für reale Projektdaten kann ein vorhandenes v4-Bundle explizit angebunden werden:

```text
python -m tools.generate_z_cockpit --project-bundle <projektdatei>
```

Detaildokumentation: `docs/03_Developer/Z_COCKPIT_BENUTZERVERWALTUNG.md`.

## Whitelist- und Berechtigungsverwaltung

Der Navigationspunkt `Berechtigungen` zeigt ProjectOS-Berechtigungszuweisungen inklusive Quelle, Wirkung, Scope, Risikoklasse, Gültigkeit, Widerrufsstatus und effektiver Entscheidung. DENY/Blacklist bleibt vorrangig und wird über den vorhandenen `ProjectOSAuthorizationEvaluator` ausgewertet.

Die Repository-Entwickler-Whitelist aus `config/authorized_developers.json` bleibt davon strikt getrennt. Das statische Cockpit schreibt keine Rechte oder Entwicklerfreigaben.

Detaildokumentation: `docs/03_Developer/Z_COCKPIT_BERECHTIGUNGEN.md`.

## Issue- und Fehlermeldungsworkflow

Der Navigationspunkt `Fehler melden` erzeugt einen strukturierten lokalen Markdown-Bericht. Projekt-, Diagnose-, Sicherheits- und Repositoryprüfdaten können kontrolliert ergänzt werden. Die sichtbare Berichtsvorschau bleibt die Übergabegrenze; sensible Benutzer-/Berechtigungsbestände, Tokens, Passwörter, Schlüssel und ungeprüfte Dateiinhalte werden nicht automatisch übernommen.

`GitHub-Issue vorbereiten` kopiert den geprüften Bericht und öffnet das offizielle GitHub-Issue-Formular; das Issue wird nicht automatisch abgesendet.

Detaildokumentation: `docs/03_Developer/Z_COCKPIT_FEHLERMELDUNG.md`.

## 3D-Vorschauen und Modellabdeckung – umgesetzt

Die Geräte- und Bibliotheksansicht wertet vorhandene KiCad-3D-Modellreferenzen und technische F.Fab-Hüllgeometrie aus.

Verbindliche Statuswerte:

- `Modell`: echte KiCad-`model`-Referenz und vorhandene Repositorydatei;
- `Modellreferenz fehlt`: Referenz vorhanden, Datei nicht auflösbar;
- `Hüllkörper`: kein echtes Modell, aber technische Vorschau aus bereits vorhandener `F.Fab`-Kontur;
- `Fehlt`: weder Modell noch verwertbare Hüllgeometrie;
- `Nicht zugeordnet`: kein Footprint zugeordnet.

Eine Hüllkörper-Vorschau zählt ausdrücklich **nicht** als echtes 3D-Modell. Es werden keine Produktgehäuse oder Herstellergeometrien erfunden.

Technische Quellen und Dateien:

```text
3dmodels/Z_3DModell.3dshapes/
tools/generate_3d_previews.py
tools/z_cockpit/three_d_preview.py
docs/site/3d-previews/
docs/03_Developer/Z_COCKPIT_3D_VORSCHAUEN.md
```

Die Startseite zeigt getrennte Kennzahlen für echte 3D-Modelle und technische 3D-Vorschauen. Geräte erhalten im festen rechten Bereich eine dritte Vorschaukarte. Bibliotheken erhalten 3D-Status, 3D-Filter, Abdeckungszahlen und die technische Vorschau im vorhandenen Inspektor; die freigegebene Bibliotheksarbeitslogik und der separate Geräte-ID-Scrollbereich bleiben erhalten.

Der Windows-Starter aktualisiert die 3D-Vorschauen vor dem Öffnen des Cockpits. CI und Release prüfen die deterministischen Vorschauen mit `python tools/generate_3d_previews.py --check`.

## Direkte KiCad-Editoraufrufe – umgesetzt

Geräte- und Bibliotheksinspektor erhalten lokale Aktionen, ohne ihre bestehende Arbeitslogik oder Scrollstruktur umzubauen:

- `Symbol-Editor öffnen`;
- `Footprint direkt öffnen`, wenn ein Repository-Footprint vorhanden ist.

Die HTML-Datei startet keine Executables. Sie verwendet ausschließlich das lokale URI-Schema `kicad-z:`. `tools/windows/open_z_cockpit.bat` registriert dieses Schema unter `HKCU`, also nur für den aktuellen Benutzer und ohne Administratorrechte.

Der Handler `tools/windows/open_kicad_from_cockpit.ps1` akzeptiert nur validierte technische IDs. Dateipfade werden nicht aus der URL übernommen, sondern ausschließlich aus festen Repositorypfaden konstruiert.

Footprints werden über den KiCad-Frame `fpedit` direkt mit der zugehörigen `.kicad_mod`-Datei geöffnet.

Für Symbole gibt es upstream derzeit keinen stabilen öffentlichen CLI-Aufruf, der eine konkrete `Bibliothek:Symbol`-ID direkt selektiert. Der Handler prüft deshalb Bibliothek und Top-Level-Symbol, kopiert die technische Referenz in die Zwischenablage und öffnet den Symbol Editor über den KiCad-Manager-Hotkey `Ctrl+L`.

Detaildokumentation:

```text
docs/03_Developer/Z_COCKPIT_KICAD_EDITORAUFRUFE.md
```

## Persistierte Laufzeitdiagnosen – umgesetzt

Die bisher ausschließlich im Speicher vorhandene `ProjectOSProjectMemory` kann jetzt als lokaler, versionierter Runtime-Snapshot persistiert und vom Z_Cockpit wieder eingelesen werden.

Verbindlicher Grundsatz:

```text
Quelle persistieren – Diagnose reproduzierbar neu berechnen
```

Persistiert werden:

- ProjectOS-Wissensknoten;
- typisierte Wissensbeziehungen;
- bekannte Message-IDs;
- bekannte Correlation-IDs;
- Speicherzeitpunkt.

Nicht persistiert werden abgeleitete Diagnoseergebnisse, Ampelzustände, Schweregrad-Zählungen oder Reparaturempfehlungen.

Lokaler Standardpfad:

```text
build/PROJECTOS_RUNTIME_MEMORY.json
```

`build/` bleibt durch `.gitignore` ausgeschlossen. Fehlt die Datei, bleiben Projektvalidator und repositoryweite Projektanalyse vollständig verfügbar; die fehlende Runtimequelle ist nicht blockierend.

Beim Erzeugen des Cockpits wird ein vorhandener Snapshot validiert und über die bestehende `ZCockpitDiagnosticsWorklistView` erneut analysiert. Laufzeitbefunde erscheinen als Quelle `Laufzeitdiagnose` und erhalten `RT-*`-Codes. Ein fehlerfreier persistierter Graph wird als nicht blockierender `RT-OK`-Hinweis sichtbar.

Technische Dateien:

```text
distributions/projectos_project_memory_persistence.py
tools/z_cockpit/runtime_diagnostics.py
docs/03_Developer/Z_COCKPIT_LAUFZEITDIAGNOSEN.md
```

Die bestehende ProjectOS-Projektbundle-v4-Persistenz für Benutzerverwaltung bleibt unverändert. Der Wissensgraph-Snapshot ist bewusst ein separater lokaler Runtime-Zustand und erzwingt keine Migration vorhandener Projektdateien.

## Projektmodell

`benutzerverwaltung`, `whitelist_verwaltung`, `issue_fehlermeldung`, `3d_vorschauen`, `kicad_editoraufrufe` und `runtime_diagnostics_persistence` stehen in `project_state.yaml` auf `done`.

Damit ist aktuell keine normale `planned`- oder `in_progress`-Aufgabe im zentralen Projektmodell offen. Der Entwicklungsnavigator zeigt entsprechend `Keine ausführbare Aufgabe offen.`

## Separat offen

Die bisher dokumentierten normalen Z_Cockpit-Folgepunkte sind abgeschlossen. Separat offen bleibt nur:

- GitHub-Ruleset-Aktivierung (`blocked`, separate gemeinsame Freigabe erforderlich).

Neue fachliche oder technische Arbeiten müssen künftig wieder explizit als neuer Ausbaupunkt geplant werden; der blockierte Ruleset wird nicht automatisch als nächste Aufgabe gewählt.
