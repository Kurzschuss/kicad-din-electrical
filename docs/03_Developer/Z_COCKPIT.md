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

Der Modulaufruf ist verbindlich, weil der Generator gemeinsame Funktionen aus dem Python-Paket `tools` verwendet.

## Unter Windows öffnen

```text
tools\windows\open_z_cockpit.bat
```

Der Starter verwendet bevorzugt `.venv\Scripts\python.exe`. Ist noch keine virtuelle Umgebung vorhanden, wird das Python aus `PATH` verwendet.

Nach erfolgreicher Erzeugung öffnet der Starter `docs/site/z-cockpit.html` im Standardbrowser.

## Modulare Seitenarchitektur

Die zentrale Seitendefinition liegt unter:

```text
tools/z_cockpit/pages.py
```

Jede Seite besitzt:

- eine stabile technische Seiten-ID,
- eine deutsche Bezeichnung,
- eine deutsche Kurzbeschreibung,
- einen Status, ob die Seite bereits umgesetzt ist.

Registriert sind:

- Start,
- Geräte,
- Bibliotheken,
- Hersteller,
- Qualität,
- Diagnose,
- Sicherheit,
- Dokumentation,
- Einstellungen.

Die Seitenregistrierung ist die verbindliche Grundlage für Navigation, Tests und spätere Erweiterungen. Neue Bereiche werden dort ergänzt, statt unabhängige Einzeloberflächen anzulegen.

## Prüfung

Die automatisierten Tests prüfen unter anderem:

- Übernahme der echten Kataloggeräte,
- deutsche Standardanzeige,
- Filterfelder für Familie, Hersteller, Polzahl, Charakteristik und Nennstrom,
- technische Geräte-ID und Symbolzuordnung,
- eindeutige Seiten-IDs,
- deutsche Seitenbezeichnungen,
- registrierte Kernbereiche des Cockpits.

GitHub Actions erzeugt die Cockpit-Datei bei jedem vollständigen CI-Lauf und prüft, ob eine nicht leere HTML-Ausgabe entstanden ist.

## Aktueller Entwicklungsstand

Die erste Version ist eine statische, lokal ausführbare HTML-Anwendung. Bereits vorhanden sind:

- tabellenbasierte Geräteansicht,
- Filter und Auswahllisten,
- Eigenschaftsbereich,
- zentrale Seitenregistrierung.

Noch nicht vollständig angebunden sind:

- Startseite mit echtem Projektstatus,
- echte Symbolvorschauen,
- Footprintvorschauen,
- 3D-Vorschauen,
- detaillierter Qualitätsstatus,
- Diagnose- und Sicherheitsseiten,
- direkte KiCad-Editoraufrufe.

Diese Funktionen werden schrittweise ergänzt. Die tabellenbasierte Bedienung, die deutschen Auswahllisten und die zentrale Seitenregistrierung bleiben dabei verbindliche Grundlagen.
