# Z_Cockpit erzeugen und testen

`Z_Cockpit` ist die zentrale, tabellenbasierte Projekt-, Bibliotheks- und Geräteübersicht der KiCad DIN Electrical Suite.

## Erzeugen

```text
python -m tools.generate_z_cockpit
```

Ausgabe:

```text
docs/site/z-cockpit.html
```

Die HTML-Datei ist ein lokal erzeugtes Arbeitsartefakt und wird nicht als zweite Datenquelle gepflegt.

Für echte ProjectOS-Benutzer- und Berechtigungsdaten kann ein ProjectOS-v4-Projektbundle angebunden werden:

```text
python -m tools.generate_z_cockpit --project-bundle <projektdatei>
```

Ohne Projektbundle werden weder Benutzer noch ProjectOS-Berechtigungen erfunden. Repositorydaten wie die Entwickler-Whitelist bleiben trotzdem sichtbar.

## Unter Windows öffnen

```text
tools\windows\open_z_cockpit.bat
```

Der Windows-Starter registriert zuerst das lokale `kicad-z:`-Protokoll im aktuellen Benutzerprofil. Damit können die expliziten Editorlinks aus Geräte- und Bibliotheksansicht an den geprüften lokalen Handler übergeben werden. Ein Fehler bei dieser Registrierung blockiert das Cockpit nicht.

Anschließend führt der Starter die vorhandene Repositoryprüfung für den Fehlerbericht und die Erzeugung der technischen 3D-Vorschauen aus:

```text
python -m tools.check_repository_version
python -m tools.generate_3d_previews
```

Ein gesperrter Repositoryzustand blockiert nur die GitHub-Issue-Vorbereitung; das lokale Z_Cockpit und lokale Fehlerberichte bleiben nutzbar. Ein Fehler beim 3D-Vorschaugenerator verhindert dagegen das Öffnen einer potenziell inkonsistenten lokalen Cockpit-Ansicht.

Alternativ:

```powershell
.\.venv\Scripts\python.exe -m tools.generate_3d_previews
.\.venv\Scripts\python.exe -m tools.generate_z_cockpit
```

Beim direkten manuellen Öffnen der HTML-Datei kann der Browser das lokale `kicad-z:`-Protokoll nicht verwenden, wenn es zuvor noch nicht registriert wurde.

## Zentrale Seitenregistrierung

Die Navigation wird aus `tools/z_cockpit/pages.py` erzeugt. Aktuell umgesetzt sind:

- Start;
- Geräte;
- Bibliotheken;
- Hersteller;
- Qualität;
- Diagnose;
- Benutzer;
- Berechtigungen;
- Fehler melden;
- Sicherheit;
- Dokumentation;
- Einstellungen.

Neue Bereiche werden dort registriert und nicht als unabhängige Nebenoberflächen aufgebaut.

## Einheitliche Seitenköpfe

Visuelle Referenz ist die Bibliotheksansicht.

Verbindliches Muster:

```text
Seitentitel (kurze Erklärung zum Menüpunkt)
```

Die Erklärung steht kleiner in derselben Zeile. Eine zusätzliche Erklärungszeile direkt unter dem Titel wird vermieden. Filter-/Arbeitslisten stehen links beziehungsweise im Hauptbereich; ein fester Eigenschaftenbereich rechts wird verwendet, wenn er fachlich sinnvoll ist.

## Datenquellen

Das Cockpit führt keine zweite fachliche Datenhaltung ein.

Wichtige Quellen sind:

- Gerätekatalog unter `data/devices/`;
- KiCad-Symbol- und Footprintbibliotheken;
- KiCad-`model`-Referenzen in den Footprints;
- Repository-3D-Modelle unter `3dmodels/Z_3DModell.3dshapes/`;
- `project_state.yaml`;
- ProjectOS-Projektvalidator und Projektanalyse;
- vorhandene Markdown-Dokumentation;
- optional `ProjectOSUserManagementState` aus einem ProjectOS-v4-Projektbundle;
- Repository-Entwickler-Whitelist unter `config/authorized_developers.json`;
- optionales Repositoryprüfergebnis unter `build/VERSIONSPRUEFUNG.json` für die GitHub-Fehlermeldung.

## Geräte

Die Geräteansicht bietet Filter für Gerätefamilie, Hersteller, Polzahl, Charakteristik, Nennstrom und Status. Technische Geräte-ID, Symbol, Footprint und Vorschauen bleiben sichtbar.

Der rechte Eigenschaftenbereich zeigt drei getrennte Vorschauen:

1. Symbol;
2. Footprint;
3. 3D.

Für 3D wird der tatsächliche Modell-/Vorschaustatus angezeigt. Eine technische F.Fab-Hüllkörperansicht wird ausdrücklich nicht als echtes 3D-Modell gezählt.

Nach Auswahl eines Geräts erscheinen zusätzlich lokale KiCad-Aktionen im bestehenden Eigenschaftenbereich. `Symbol-Editor öffnen` startet den KiCad Symbol Editor; `Footprint direkt öffnen` ist nur für tatsächlich zugeordnete Repository-Footprints aktiv.

## Bibliotheken

Die Bibliotheksansicht ist tabellenbasiert. Bibliotheksdetails werden direkt unter der ausgewählten Bibliothek geöffnet. Rechts bleibt der Symbolinspektor fest stehen; nur lange Geräte-ID-Listen scrollen separat.

Die bestehende Bedienlogik bleibt unverändert. Ergänzt sind:

- Anzahl echter 3D-Modelle;
- Anzahl verfügbarer 3D-Vorschauen;
- Filter `3D-Vorschauen`;
- 3D-Status je Symbol;
- technische 3D-Vorschau im rechten Inspektor;
- lokale Aktionen `Symbol-Editor öffnen` und, bei Zuordnung, `Footprint direkt öffnen`.

Die Editorlinks werden in den bestehenden rechten Inspektor eingefügt. Der Geräte-ID-Bereich behält sein separates Scrollverhalten.

## 3D-Vorschauen

Die 3D-Anbindung unterscheidet folgende Zustände:

- `Modell`: auflösbare KiCad-`model`-Referenz und vorhandene Repositorydatei;
- `Modellreferenz fehlt`: Referenz vorhanden, Datei fehlt oder ist nicht auflösbar;
- `Hüllkörper`: technische isometrische Vorschau aus bereits vorhandener `F.Fab`-Rechteckgeometrie, aber kein echtes Modell;
- `Fehlt`: keine 3D-Modell- und keine verwertbare F.Fab-Geometrie;
- `Nicht zugeordnet`: kein Footprint zugeordnet.

Der Generator lautet:

```text
python -m tools.generate_3d_previews
python -m tools.generate_3d_previews --check
```

Ausgabe:

```text
docs/site/3d-previews/
```

Es werden keine fehlenden Produktgehäuse, STEP-Modelle oder Herstellerdaten erfunden. Die vollständige technische Beschreibung steht unter:

```text
docs/03_Developer/Z_COCKPIT_3D_VORSCHAUEN.md
```

## Direkte KiCad-Editoraufrufe

Die statische HTML-Datei führt keine Programme unmittelbar aus. Sie erzeugt ausschließlich Links mit dem lokalen URI-Schema `kicad-z:`. Der Windows-Starter registriert dieses Schema unter `HKCU`, ohne Administratorrechte.

Der Handler akzeptiert nur validierte technische Repository-IDs. Beliebige Dateipfade und frei übergebene Shell-Befehle werden nicht akzeptiert.

Für Footprints wird der feste Repositorypfad

```text
footprints/<Footprint>.pretty/<Footprint>.kicad_mod
```

gebildet und mit dem KiCad Footprint Editor geöffnet.

Für Symbole wird `Bibliothek:Symbol` gegen die vorhandene `.kicad_sym`-Datei geprüft. Da KiCad derzeit keinen stabilen öffentlichen CLI-Aufruf zur direkten Auswahl genau dieser Symbol-ID anbietet, wird die geprüfte Referenz in die Zwischenablage gelegt und der Symbol Editor über den KiCad-Manager geöffnet.

Technische Details:

```text
docs/03_Developer/Z_COCKPIT_KICAD_EDITORAUFRUFE.md
```

## Hersteller

Die Herstellerseite aggregiert Hersteller, Serien, Gerätefamilien, Quellenstatus und technische Geräte-IDs read-only aus dem Gerätekatalog. `Generic` wird in der Oberfläche als `Herstellerneutral` dargestellt.

## Qualität

Die Qualitätsseite verbindet:

- ProjectOS-Projektkonsistenz aus `tools.project_validator`;
- Bibliotheksgesundheit aus der Quality Engine.

Der Projektvalidator liefert weiterhin die stabilen Prüfungen `PRJ-001` bis `PRJ-010`. Die Aktualität der 3D-Vorschauen wird zusätzlich als eigener CI-/Release-Generatorcheck geprüft, ohne die bestehenden stabilen PRJ-IDs umzunummerieren.

## Diagnose

Die Diagnoseansicht bündelt repositoryweite Befunde aus Projektvalidator und Projektanalyse. Fehler und Warnungen können gefiltert werden; der rechte Bereich zeigt Prüfcode, Referenz, Details und vorhandene Reparaturempfehlung.

## Benutzer

Die Benutzerseite ist eine read-only Sicht auf den bestehenden `ProjectOSUserManagementState`.

Angezeigt werden Benutzername und technische `user_id`, Lifecycle-Status, Profil- und Projektrollen, effektive Rechte, Rechteherkunft, Risikoklassen, Widerrufe und Lifecycle-Ereignisse.

Technische Details:

```text
docs/03_Developer/Z_COCKPIT_BENUTZERVERWALTUNG.md
```

## Berechtigungen

Die Berechtigungsseite trennt zwei Sicherheitsquellen strikt.

Aus `ProjectOSUserManagementState` werden vorhandene Rechtezuweisungen mit den Quellen Rolle, direkte Zuweisung, Delegation, DENY, Ausnahme, Whitelist und Blacklist ausgewertet. Sichtbar sind Benutzer, Berechtigung, Zuweisungs-ID, Quelle, Wirkung, Scope, Risikoklasse, Gültigkeit, Widerrufsstatus sowie die effektive Autorisierungsentscheidung. Ein wirksames DENY/Blacklist bleibt vorrangig.

Die getrennte Repositoryquelle für Entwicklerfreigaben bleibt:

```text
config/authorized_developers.json
```

Das statische Cockpit schreibt keine Berechtigungen. ProjectOS-Änderungen müssen über `ProjectOSUserManagementChangeService` und die fail-closed `ProjectOSUserManagementCommandAuthorization` laufen.

Technische Details:

```text
docs/03_Developer/Z_COCKPIT_BERECHTIGUNGEN.md
```

## Fehler melden

Der Bereich `Fehler melden` erzeugt einen strukturierten Markdown-Bericht und bereitet bei zulässigem Repositoryzustand ein GitHub-Issue vor.

Der Benutzer erfasst Kategorie, Kurztitel, optionale technische Referenz, Beschreibung und Reproduktionsschritte sowie erwartetes und tatsächliches Verhalten. Optional werden Projekt-/ProjectOS-Stand, Diagnose, Sicherheitsstatus und Repositoryprüfung ergänzt.

Die Seite selbst führt keinen Netzwerkzugriff aus. Der lokale Bericht kann unabhängig vom Repositorystatus kopiert oder als `z-cockpit-fehlerbericht.md` gespeichert werden. Das GitHub-Issue wird nicht automatisch angelegt oder abgesendet.

Nicht automatisch aufgenommen werden Benutzer-/Berechtigungsbestände, authentifizierte GitHub-Benutzernamen, Tokens, Passwörter, Schlüssel, Zugangsdaten oder ungeprüfte Dateiinhalte.

Technische Details:

```text
docs/03_Developer/Z_COCKPIT_FEHLERMELDUNG.md
```

## Sicherheit

Die Sicherheitsseite zeigt Repository-, Versions-, Originalitäts-, Entwickler-Whitelist-, CODEOWNERS- und Ruleset-Status. Ein vorhandener Ruleset-Entwurf bedeutet weiterhin nicht, dass der serverseitige Ruleset aktiviert ist.

## Dokumentation

Der Dokumentationsbrowser indexiert vorhandene Markdown-Dateien aus dem Repository. Die Markdown-Dateien selbst bleiben Single Source of Truth.

## Einstellungen

Projektwerte werden read-only aus Repositoryquellen angezeigt. Unter `Pfade` ist auch `3dmodels/Z_3DModell.3dshapes/` sichtbar. Lokale Oberflächenoptionen wie Theme, Tabellendichte und letzte Seite werden ausschließlich im Browser unter `z-cockpit.settings.v1` gespeichert.

## Prüfung

Die Tests prüfen unter anderem:

- zentrale Seitenregistrierung und eindeutige Seiten-IDs;
- Gerätekatalog- und Bibliotheksintegration;
- Symbol-, Footprint- und 3D-Vorschauzustände;
- Trennung von echtem 3D-Modell und technischem Hüllkörper;
- sichere Auflösung von `KICAD_Z_3DMODEL_DIR`-Referenzen;
- lokale KiCad-Editorlinks in Geräte- und Bibliotheksinspektor;
- HKCU-only Registrierung des `kicad-z:`-Protokolls;
- Repository-ID-Validierung und feste Pfadauflösung des lokalen Handlers;
- Herstelleraggregation;
- Projektvalidator/Qualität;
- Diagnoseansicht;
- Benutzeraggregation, Rollen, Lifecycle und effektive Rechte;
- ProjectOS-Whitelist/Blacklist/Ausnahmen und Widerrufe;
- getrennte Repository-Entwickler-Whitelist;
- Fehlerbericht, Datenschutzgrenze und GitHub-Gate;
- GitHub Issue Form;
- HTML-Escaping;
- Dokumentationsbrowser;
- lokale Einstellungen;
- einheitliche Seitenköpfe;
- Entwicklungsnavigator und Projektstatus.

GitHub Actions prüft die generierten 3D-Vorschauen, erzeugt das Cockpit in der vollständigen ProjectOS-Prüfkette und führt zusätzlich den Projektvalidator aus. Die Windows-spezifische Protokoll- und Handlerlogik wird durch plattformunabhängige Struktur-/Sicherheitsprüfungen abgedeckt.

## Aktueller Entwicklungsstand

Abgeschlossen sind insbesondere:

1. Benutzerverwaltung;
2. Whitelist- und Berechtigungsverwaltung;
3. Issue- und Fehlermeldungsworkflow;
4. 3D-Vorschauen und Modellabdeckung;
5. direkte KiCad-Editoraufrufe.

Im zentralen `project_state.yaml` ist derzeit keine normale `planned`- oder `in_progress`-Aufgabe offen. Der Entwicklungsnavigator meldet entsprechend `Keine ausführbare Aufgabe offen.`

Separat offen bleiben weiterhin:

- Persistenzanbindung der Laufzeit-Wissensgraphdiagnosen;
- serverseitige GitHub-Ruleset-Aktivierung nach separater Freigabe.
