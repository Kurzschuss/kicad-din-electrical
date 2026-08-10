# Z_Cockpit erzeugen und testen

`Z_Cockpit` ist die zentrale lokale Projekt-, Bibliotheks-, Geräte-, Benutzer- und Diagnoseoberfläche der KiCad DIN Electrical Suite. Die erzeugte HTML-Datei ist ein Arbeitsartefakt und keine zweite fachliche Datenquelle.

## Erzeugen

```text
python -m tools.generate_z_cockpit
python -m tools.generate_z_cockpit --project-bundle <projektdatei>
```

Ausgabe:

```text
docs/site/z-cockpit.html
```

Ohne ProjectOS-Projektbundle werden keine realen Benutzer oder ProjectOS-Rechte erfunden.

## Unter Windows öffnen

```text
tools\windows\open_z_cockpit.bat
```

Der Starter registriert die lokalen URI-Protokolle unter HKCU, prüft den Repositoryzustand, erzeugt technische 3D-Vorschauen und lädt – falls vorhanden – das zuletzt aktive, weiterhin gültige ProjectOS-Projekt.

Wichtige lokale Protokolle:

```text
kicad-z:     geprüfte lokale KiCad-Editoraufrufe
projectos-z: ProjectOS-Projekt-, Governance- und Reportingaktionen
```

Die Browseroberfläche führt Programme nicht direkt aus. Lokale Handler validieren erlaubte Aktionen und Parameter erneut.

## Seiten

Die Navigation wird aus `tools/z_cockpit/pages.py` erzeugt. Umgesetzt sind Start, Projekt, Geräte, Bibliotheken, Hersteller, Qualität, Diagnose, Benutzer, Berechtigungen, Fehler melden, Sicherheit, Dokumentation und Einstellungen.

Seitentitel folgen dem einheitlichen Muster:

```text
Seitentitel (kurze Erklärung zum Menüpunkt)
```

## Datenquellen

Das Cockpit führt keine parallele fachliche Datenhaltung ein. Zentrale Quellen sind Gerätekatalog, KiCad-Bibliotheken, 3D-Modelle/-Vorschauen, `project_state.yaml`, ProjectOS-Projektvalidator/Diagnosen, Markdown-Dokumentation, optional `ProjectOSUserManagementState`, Repository-Entwickler-Whitelist und lokale Prüfergebnisse unter `build/`.

## Projektdatei

`Projekt` erzeugt ProjectOS-v4-Bundles über `DinEditorProjectManager`. Der Browser übergibt beim Erzeugen nur Projektname und Schutzklasse; den Zielpfad bestimmt der native Windows-Speicherdialog.

Schutzklassen:

- `private_team`: vertrauliches Teamprojekt, separater privater Projekt-Repository-Klon;
- `restricted_local`: vertraulich lokal außerhalb des allgemeinen Quell-Repositories;
- `repository_visible`: bewusst für alle Leser des betreffenden Repositories sichtbar.

ProjectOS-Dateirechte (`project.file.read/write/share/admin`) ersetzen niemals tatsächliche Datei-/GitHub-Leserechte. Eine einzelne Datei kann innerhalb desselben GitHub-Repositories nicht vor ausgewählten Repository-Lesern verborgen werden.

Details: `docs/03_Developer/Z_COCKPIT_PROJEKTDATEI.md`.

## Geräte, Bibliotheken und 3D

Geräte- und Bibliotheksansicht behalten den festen rechten Inspektor und getrennte Scrollbereiche. Symbol-, Footprint- und 3D-Vorschauen werden aus vorhandenen Repositorydaten erzeugt. Eine technische `F.Fab`-Hüllkörpervorschau zählt nicht als echtes 3D-Modell.

Lokale KiCad-Aktionen verwenden ausschließlich validierte Repository-IDs über `kicad-z:`. Beliebige Browserpfade oder Shell-Befehle werden nicht übernommen.

Details:

```text
docs/03_Developer/Z_COCKPIT_3D_VORSCHAUEN.md
docs/03_Developer/Z_COCKPIT_KICAD_EDITORAUFRUFE.md
```

## Diagnose

Repositorydiagnose und persistierte Laufzeit-Wissensgraphdaten werden read-only zusammengeführt. Persistiert werden fachliche Laufzeitquellen, nicht abgeleitete Ampeln oder Reparaturempfehlungen. Details: `docs/03_Developer/Z_COCKPIT_LAUFZEITDIAGNOSEN.md`.

## Benutzer und aktive Identität

Die Benutzerseite zeigt stabile ID, Bezeichnung, Lifecycle, Gewichtung, Rollen, GitHub-Zuordnung sowie effektive Rechte. Benutzerverwaltungs-Persistenz ist Version 5; ältere v1–v4 bleiben lesbar, während das äußere Projektbundle v4 bleibt.

Der obere Bereich zeigt weiterhin die lokal gewählte `Aktive ProjectOS-Identität` und den Simulationsmodus. Diese Auswahl ist **keine Authentifizierung**. Der Testuser bleibt rein lokal und besitzt keine persistierten Rechte.

Für reale schreibende Aktionen wird stattdessen der tatsächlich mit GitHub CLI (`gh`) authentifizierte Benutzer ermittelt und über `github_login` einem eindeutigen ProjectOS-Profil zugeordnet.

Vertrauenswürdiger Schreibpfad:

```text
Z_Cockpit
 -> projectos-z://governance
 -> Windows-Handler
 -> tools/projectos_governance_cli.py
 -> tools/projectos_governance.py
 -> ProjectOS-Autorisierung / Change-Service
 -> ProjectOS-Projektdatei
```

Verwaltbar sind Benutzeranlage, Bezeichnung, Gewichtung, GitHub-Zuordnung sowie White-/Blacklist-Zugriffsregeln. Details: `docs/03_Developer/Z_COCKPIT_BENUTZERVERWALTUNG.md`.

## Berechtigungen, White-/Blacklist und Zugriffsbereiche

Die effektive Entscheidung verwendet weiterhin den vorhandenen `ProjectOSAuthorizationEvaluator`. Whitelist entspricht `allow`, Blacklist `deny`; ein wirksames DENY bleibt vorrangig.

Governance-Rechte:

```text
project.file.read
project.file.write
project.file.share
project.file.admin
project.user.manage
project.permission.manage
cockpit.view
cockpit.edit
github.issue.prepare
github.issue.auto_submit
```

Neben `project` existieren `page:*`-Scopes für die einzelnen Cockpit-Bereiche. Die Benutzeransicht stellt `Sehen / Bearbeiten` je Bereich als ProjectOS-Policy dar.

Wichtig: Ein statisches HTML kann bereits geladene Daten nicht sicher vor einem Benutzer verbergen, der HTML oder Projektbundle bereits lesen darf. Vertraulichkeit benötigt zusätzlich den tatsächlichen privaten Datei-/Repositoryzugriff.

Die Repository-Entwickler-Whitelist `config/authorized_developers.json` bleibt strikt von ProjectOS-Whitelist/Blacklist getrennt.

Details: `docs/03_Developer/Z_COCKPIT_BERECHTIGUNGEN.md`.

## Fehler melden und GitHub-Automatik

Der strukturierte lokale Markdown-Bericht und die manuelle GitHub-Issue-Vorbereitung bleiben bestehen. Zusätzlich kann ein Benutzer mit effektivem `github.issue.auto_submit` nach Bestätigung der sichtbaren Vorschau automatisch melden.

Unmittelbar vor jedem automatischen GitHub-Schreibzugriff werden erneut geprüft:

- offizielles Repository / kein Fork;
- aktuelle, freigegebene Version;
- `gh`-Authentifizierung;
- eindeutige GitHub→ProjectOS-Benutzerzuordnung;
- Benutzer-Lifecycle und effektives `github.issue.auto_submit`;
- kein Simulationsmodus;
- Secret-Heuristik für offensichtliche Tokens/Passwörter/Private Keys.

### Dubletten

ProjectOS bildet einen SHA-256-Fingerprint aus Kategorie, technischer Referenz und normalisiertem Kurztitel. Vor Neuanlage wird zuerst nach diesem Marker und danach konservativ nach bereits manuell vorhandenen Issues mit exakt gleichem Titel und technischer Referenz gesucht.

Eine Dublette erzeugt kein zweites Issue. Stattdessen wird das vorhandene Issue gekennzeichnet kommentiert; ursprünglicher und weitere Reporter sowie die Anzahl der Meldungen bleiben nachvollziehbar. Letztes lokales Ergebnis: `build/Z_ISSUE_REPORTING_RESULT.json`.

Der authentifizierte GitHub-Benutzer wird für die Rechteprüfung benötigt, aber nicht automatisch in den normalen Fehlerberichtskontext eingebettet.

Details: `docs/03_Developer/Z_COCKPIT_FEHLERMELDUNG.md`.

## Sicherheit

Die Sicherheitsseite zeigt Repository-, Versions-, Originalitäts-, Entwickler-Whitelist-, CODEOWNERS- und Ruleset-Status. Ein vorhandener Ruleset-Entwurf bedeutet nicht, dass der serverseitige Ruleset aktiviert ist.

Der Ruleset bleibt bis zu einer separaten ausdrücklichen Freigabe `blocked`.

## Dokumentation und Einstellungen

Der Dokumentationsbrowser indexiert vorhandene Markdown-Dateien; diese bleiben Single Source of Truth. Lokale Oberflächenoptionen wie Theme, Tabellendichte und letzte Seite liegen ausschließlich unter `z-cockpit.settings.v1` im Browser.

## Prüfung

Die Test- und CI-Kette deckt unter anderem Seitenregistrierung, Projektbundle, Benutzer-/Lifecycle-Persistenz, Simulation, GitHub-Zuordnung, Governance-Autorisierung, White-/Blacklist und DENY-Priorität, Repository-/Fork-/Versionsgate, Secret-Scan, Dublettenhistorie, Symbol-/Footprint-/3D-Generatoren, Projektvalidator und Z_Cockpit-Erzeugung ab.

## Aktueller Entwicklungsstand

Abgeschlossen sind Benutzerverwaltung, White-/Blacklist/Berechtigungen, Issue-/Fehlermeldung, Zugriff-/Reporting-Governance, 3D-Vorschauen, direkte KiCad-Editoraufrufe und Persistenz der Laufzeitdiagnosen. Im zentralen `project_state.yaml` ist keine normale `planned`- oder `in_progress`-Aufgabe offen.

Separat offen bleibt ausschließlich die serverseitige GitHub-Ruleset-Aktivierung nach separater Freigabe.
