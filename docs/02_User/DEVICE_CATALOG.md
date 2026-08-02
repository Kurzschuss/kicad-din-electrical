# Technischen Gerätekatalog verwenden

Der technische Gerätekatalog zeigt die im Projekt hinterlegten Geräte zusammen mit ihren elektrischen Kenndaten. Er kann direkt im Browser geöffnet werden und benötigt weder eine zusätzliche Installation noch einen Webserver.

## Seite öffnen

1. Das Projekt lokal herunterladen oder mit GitHub Desktop klonen.
2. Im Projektordner den Unterordner `docs/site/` öffnen.
3. Die Datei `devices.html` doppelt anklicken.
4. Die Seite öffnet sich im Standardbrowser.

Pfad innerhalb des Projekts:

```text
docs/site/devices.html
```

## Angezeigte Informationen

Je nach vorhandenen Gerätedaten zeigt die Tabelle unter anderem:

- Geräte-ID
- Funktionsgruppe und Gerätefamilie
- Hersteller
- Serie
- Artikelnummer
- Polzahl
- Nennstrom
- Auslösekennlinie
- Ausschaltvermögen
- Breite in Teilungseinheiten
- zugeordnetes KiCad-Symbol
- Footprint-Richtlinie
- Quellenstatus

Ein Gedankenstrich bedeutet, dass der betreffende optionale Wert für dieses Gerät noch nicht hinterlegt wurde.

## Geräte suchen

Im Suchfeld kann nach verschiedenen Angaben gesucht werden, zum Beispiel:

```text
B16
```

```text
Leitungsschutzschalter
```

```text
Z_MCB:MCB
```

Die Trefferanzahl oberhalb der Tabelle wird automatisch aktualisiert.

## Filter verwenden

Zusätzlich zur Volltextsuche stehen Filter zur Verfügung:

- Funktionsgruppe
- Gerätefamilie
- Quellenstatus

Mehrere Filter können gleichzeitig verwendet werden. Ein Gerät wird nur angezeigt, wenn es zu allen gewählten Filtern und zum eingegebenen Suchtext passt.

## Quellenstatus verstehen

Der Quellenstatus zeigt, wie belastbar ein Datensatz ist:

- `template` – herstellerneutrales Beispiel zur Demonstration der Datenstruktur
- `unverified` – noch nicht vollständig anhand belastbarer Herstellerunterlagen geprüft
- `verified` – anhand einer dokumentierten Quelle geprüft

Ein Eintrag mit `template` ist keine Produktempfehlung und keine bestätigte Herstellerangabe.

## Bedeutung der Footprint-Richtlinie

- `optional` – ein Footprint darf vorhanden sein, ist aber nicht zwingend erforderlich
- `required` – ein gültiger Footprint muss zugeordnet sein
- `none` – für dieses Symbol beziehungsweise Gerät ist ausdrücklich kein Footprint vorgesehen

Gerade bei Stromlauf-, Übersichts- und Installationsplänen ist es normal, dass manche Symbole keinen Footprint benötigen.

## Zur Bibliotheksübersicht zurückkehren

Oben auf der Seite befindet sich der Link **Zur Bibliotheksübersicht**. Er führt zurück zu:

```text
docs/site/index.html
```

Dort befinden sich die Übersichten zu Symbolbibliotheken, Footprintbibliotheken und den vorhandenen Gerätedatensätzen.

## Seite aktualisieren

Die HTML-Datei wird automatisch aus dem Gerätekatalog erzeugt. Entwickler können sie im Projektstamm mit folgendem Befehl neu erstellen:

```text
python -m tools.generate_device_catalog_html
```

Die GitHub-Actions-Prüfung stellt sicher, dass die gespeicherte Seite zu den aktuellen Gerätedaten passt.
