# Arbeitsstand – Qualitätshandbuch und Bibliothekspaket-Freigabe

Stand: 10. August 2026

## Ziel

Der erste offene Punkt der langfristigen Projekt-Roadmap nach dem abgeschlossenen Z_Cockpit-/ProjectOS-Ausbau war das vollständige Qualitätshandbuch für Bibliothekspakete. Dieser Punkt ist in diesem Arbeitsstand umgesetzt.

## Verbindliche Hauptquelle

```text
docs/00_Project/LIBRARY_GUIDELINES.md
```

Das Handbuch verbindet die vorhandenen KiCad-/`Z_`-Regeln, Symbolrichtlinie, Gerätekatalogstruktur, Footprint Policy, 3D-Policy, Paketfortschrittsdaten und CI-Prüfungen zu einem einheitlichen Freigabeprozess.

## Wesentliche Festlegungen

- KiCad bleibt technischer Standard; projektspezifische Ergänzungen werden als `Z_`-Regeln/-Metadaten sichtbar geführt.
- Neue Geräte werden als Bibliothekspakete statt als isolierte Symbolgrafiken entwickelt.
- `Z_Footprint_Policy` ist die kanonische Eigenschaft mit `required`, `optional` oder `none`.
- Neue/fachlich überarbeitete Gerätekatalogeinträge verwenden gemeinsam `name_de`, `name_en` und `abbreviation`.
- Hersteller-, Produkt-, Datenblatt- und 3D-Daten werden nicht erfunden.
- Hüllkörper aus `F.Fab` bleiben technische Vorschauen und zählen nicht als reale 3D-Modelle.
- Qualitätsstatus der Rule Engine und Paket-Reifegrad bleiben getrennt.

## Reifegrade

### Entwurf

Paket befindet sich im Aufbau; fehlende Bestandteile und `needs_rework` sind sichtbar zulässig.

### Geprüft

Erforderlich sind mindestens:

```text
symbol
device_data
documentation
tests
```

Zusätzlich muss ein belegbarer Referenzsatz vorhanden sein und `quality_status` darf nicht `needs_rework` sein. Ein Praxisbeispiel darf noch fehlen.

### Praxisgetestet

Alle Bedingungen von `Geprüft` plus dokumentiertes Beispielprojekt/praktischer Nachweis.

## Technische Durchsetzung

`tools/generate_package_progress.py` validiert diese Mindestbedingungen jetzt direkt. Dadurch kann die Paketübersicht keinen fachlich widersprüchlichen Reifegrad mehr akzeptieren.

`tools/validate_libraries.py` liest für die Footprint Policy jetzt zuerst das kanonische Feld `Z_Footprint_Policy`. Das historische Feld `Footprint Policy` bleibt als Legacy-Lesepfad erhalten. Fehlt bei Altbestand beides, bleibt der bisherige Kompatibilitätsdefault `optional` bestehen; neue/überarbeitete Symbole müssen laut Handbuch die `Z_`-Eigenschaft explizit setzen.

## Tests

Erweitert wurden:

```text
tests/test_validate_libraries.py
tests/test_package_progress.py
```

Neu:

```text
tests/test_library_guidelines.py
```

Der neue Test sichert die verbindlichen Handbuchabschnitte, Reifegradbedingungen, den Roadmap-Abschluss und den zentralen Projektstatus ab.

## Projektstatus

`project_state.yaml` enthält im Meilenstein `qualitaet` jetzt:

```text
qualitaetshandbuch = done
```

In `docs/01_Roadmap/PROJECT_ROADMAP.md` ist der Punkt zum vollständigen Qualitätshandbuch auf `[x]` gesetzt.

## Verifikation

PR #203 wurde auf dem vollständigen Implementierungsstand mit **CI #574** erfolgreich geprüft:

- 832 Tests erfolgreich;
- Python-Syntaxprüfung erfolgreich;
- Quality-Engine Release-Profil erfolgreich;
- KiCad-Bibliotheksvalidator: 0 Fehler, 55 nicht blockierende Hinweise;
- Gerätekatalog: 183 Dateien, 19 Familien, 0 Fehler;
- 181 generierte Gerätevarianten aktuell;
- Symbol- und 3D-Vorschauen aktuell;
- ProjectOS-Projektvalidator: 10/10 Prüfungen bestanden, 4 Meilensteine und 32 Aufgaben;
- Z_Cockpit erfolgreich erzeugt.

Nach diesem Dokumentationscommit muss der finale PR-Head nochmals vollständig grün sein.

## Bewusst unverändert

- keine MCB-Symbolgeometrie geändert;
- keine RCD-Symbolgeometrie geändert;
- keine Footprintgeometrie geändert;
- keine Gerätevarianten fachlich verändert;
- GitHub-Ruleset nicht aktiviert; dieser bleibt separat blockiert.

## Nächster normaler Roadmap-Punkt

Nach dem Qualitätshandbuch ist in Phase B der erste noch offene Punkt:

```text
weitere verständliche Screenshots ergänzen
```

Danach folgt:

```text
Beispielprojekte Schritt für Schritt dokumentieren
```

Die Freigabe/Änderung des GitHub-Rulesets bleibt davon unabhängig und erfordert weiterhin eine separate ausdrückliche Entscheidung.
