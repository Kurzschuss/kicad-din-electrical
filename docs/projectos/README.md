# ProjectOS

ProjectOS ist die verbindliche Grundlage für die Weiterentwicklung von `kicad-din-electrical`.

## Status

- Architecture Freeze 1.0: beschlossen
- Sprint 001 – ProjectOS Foundation: abgeschlossen
- Sprint 002 – Core Object Model: abgeschlossen
- weitere ProjectOS-Implementierungsbausteine und Z_Cockpit-Kernseiten: umgesetzt
- Z_Cockpit-Benutzerverwaltung: umgesetzt
- Z_Cockpit-Whitelist-/Berechtigungsverwaltung: umgesetzt
- Z_Cockpit-Issue-/Fehlermeldungsworkflow: umgesetzt
- Z_Cockpit-3D-Vorschauen und Modellabdeckung: umgesetzt
- direkte KiCad-Editoraufrufe aus dem Z_Cockpit: umgesetzt
- Dokumentationsstand aktualisiert am 10. August 2026

## Verbindliche Architekturprinzipien

- Single Source of Truth
- Domain Ownership
- Object First
- Offline First
- Simulation First
- Documentation First
- Configuration before Code
- Drei Perspektiven: Entwickler, Engineering, Projektleiter

## Benutzer und Berechtigungen

Rollen, Berechtigungen, Ausnahmerechte, Whitelist, Blacklist und Benutzer-Lifecycle besitzen technische ProjectOS-Grundlagen. Das Z_Cockpit bindet diese vorhandenen Modelle read-only an, ohne eine parallele Datenquelle einzuführen.

Die Benutzerseite zeigt Benutzer-ID, Anzeigename, Lifecycle-Status, Rollen, effektive Rechte und Rechteherkunft. Die Berechtigungsseite ergänzt die einzelnen Rechtezuweisungen mit Quelle, Wirkung, Scope, Risikoklasse, Gültigkeit, Widerrufsstatus und effektiver Entscheidung.

ProjectOS-Benutzer-Whitelist und Repository-Entwickler-Whitelist bleiben strikt getrennt. Die Repositoryquelle ist weiterhin:

```text
config/authorized_developers.json
```

Ohne ProjectOS-Projektbundle werden keine Benutzer oder ProjectOS-Rechte erfunden. Ein vorhandenes v4-Bundle kann explizit angebunden werden:

```text
python -m tools.generate_z_cockpit --project-bundle <projektdatei>
```

ProjectOS-Rechteänderungen müssen über die vorhandenen Change-/Command-/Autorisierungsservices laufen. Die statische Cockpit-Datei besitzt keine eigene Schreiblogik.

Technische Dokumentation:

- `docs/03_Developer/Z_COCKPIT_BENUTZERVERWALTUNG.md`;
- `docs/03_Developer/Z_COCKPIT_BERECHTIGUNGEN.md`.

## Issue- und Fehlermeldungsworkflow

Der Bereich `Fehler melden` erzeugt einen reproduzierbaren Markdown-Bericht aus Benutzerangaben und vorhandenen Projekt-, Diagnose-, Sicherheits- und Repository-Prüfdaten.

Die Repositoryprüfung wird über den vorhandenen Prüfer erzeugt:

```text
python -m tools.check_repository_version
```

Das Cockpit liest das Ergebnis aus `build/VERSIONSPRUEFUNG.json`. Ein gesperrter oder nicht prüfbarer Repositoryzustand blockiert nur die GitHub-Vorbereitung; der lokale Bericht bleibt verfügbar.

Vor einer GitHub-Vorbereitung muss der Benutzer die sichtbare Berichtsvorschau ausdrücklich prüfen. Benutzer-/Berechtigungsbestände, authentifizierter GitHub-Benutzer, Tokens, Schlüssel, Passwörter und ungeprüfte Dateiinhalte werden nicht automatisch in den Bericht aufgenommen.

Die GitHub-Vorbereitung kopiert nur den sichtbaren Bericht und öffnet die Issue Form unter `.github/ISSUE_TEMPLATE/bug_report.yml`. Das Issue wird nicht automatisch abgesendet.

Technische Dokumentation:

- `docs/03_Developer/Z_COCKPIT_FEHLERMELDUNG.md`;
- `docs/projectos/Z_COCKPIT_AUSBAU_BENUTZER_WHITELIST_ISSUES.md`.

## 3D-Vorschauen und Modellabdeckung

ProjectOS unterstützt native 3D-Artefakte bereits als optionale KiCad-Quellen (`.step`, `.stp`, `.wrl`). Das Z_Cockpit bindet diesen Bestand sichtbar an.

Single Source of Truth bleiben die KiCad-Footprints und ihre `model`-Referenzen sowie Repositorydateien unter:

```text
3dmodels/Z_3DModell.3dshapes/
```

Der Vorschaupfad unterscheidet strikt zwischen echtem Modell, fehlender Modellreferenzdatei, technischem Hüllkörper aus vorhandener `F.Fab`-Kontur und vollständig fehlender 3D-/Hüllgeometrie. Ein F.Fab-Hüllkörper wird niemals als echtes 3D-Modell gezählt. Der Generator erzeugt keine vermuteten Produktgehäuse und lädt keine Herstellerdateien nach.

Generator und Prüfung:

```text
python -m tools.generate_3d_previews
python -m tools.generate_3d_previews --check
```

Technische Dokumentation:

- `docs/03_Developer/Z_COCKPIT_3D_VORSCHAUEN.md`;
- `docs/handover/ARBEITSSTAND_2026-08-10_Z_COCKPIT_AUSBAU.md`.

## Direkte KiCad-Editoraufrufe

Das Z_Cockpit stellt im vorhandenen Geräte- und Bibliotheksinspektor lokale Aktionen für Symbol und Footprint bereit. Die statische HTML-Datei führt dabei keine Prozesse selbst aus.

Unter Windows registriert `tools/windows/open_z_cockpit.bat` das lokale URI-Schema `kicad-z:` ausschließlich im aktuellen Benutzerprofil. Der Handler akzeptiert nur validierte Repository-IDs und konstruiert alle Dateipfade selbst aus festen Repositorypfaden; frei übergebene lokale Pfade oder Shell-Befehle sind nicht zulässig.

Zugeordnete `.kicad_mod`-Dateien werden direkt mit dem KiCad Footprint Editor geöffnet. Für Symbole wird die vorhandene `Bibliothek:Symbol`-Referenz geprüft, in die Zwischenablage gelegt und der KiCad Symbol Editor über den Manager geöffnet, weil keine instabile interne Schnittstelle für eine erzwungene Symbolselektion verwendet wird.

Technische Dokumentation:

- `docs/03_Developer/Z_COCKPIT_KICAD_EDITORAUFRUFE.md`;
- `tools/windows/register_z_kicad_protocol.ps1`;
- `tools/windows/open_kicad_from_cockpit.ps1`.

## Improvement-System

Das Improvement-System umfasst Dublettenerkennung, Gewichtung, Priorisierung und GitHub-Anbindung.

## Erste fachliche Domänen

Die Domain Validation beginnt mit:

- MCB
- RCCB

## Arbeitsweise

Dieser Bereich dient als Entwicklungsprotokoll. Neue Änderungen sollen direkt repositoryfähig dokumentiert werden. Architekturänderungen erfolgen nur über ADRs oder dokumentierte Repository-Migrationen.

## Dokumente

- [Sprint 001 – ProjectOS Foundation](sprint-001-projectos-foundation.md)
- [Sprint 002 – Core Object Model](sprint-002-core-object-model.md)
- [AP-0016 – Persistenzmodell, Offline-Datenspeicher und Migrationen](AP-0016-persistenz-offline-speicher-migrationen.md)
- [Z_Cockpit – Benutzer, Whitelist und Fehlermeldungen](Z_COCKPIT_AUSBAU_BENUTZER_WHITELIST_ISSUES.md)
- [Maschinenlesbarer Arbeitsstand](arbeitsstand.yaml)
- [Architekturentscheidungen](../adr/)

## Nächster Schritt

Benutzerverwaltung, Whitelist/Berechtigungen, Issue/Fehlermeldung, 3D-Vorschauen und direkte KiCad-Editoraufrufe sind abgeschlossen. Im zentralen Projektmodell gibt es aktuell keine normale ausführbare `planned`- oder `in_progress`-Aufgabe.

Als technischer Folgepunkt bleibt die Persistenzanbindung der Laufzeitdiagnosen. Der GitHub-Ruleset bleibt separat blockiert und benötigt eine eigene Freigabe.
