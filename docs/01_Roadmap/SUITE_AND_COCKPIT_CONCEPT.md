# KiCad DIN Electrical Suite und Z_Cockpit

Dieses Dokument hält die langfristige Produkt- und Werkzeugidee verbindlich fest. Es dient als Orientierung für Architekturentscheidungen, Roadmap, Issues und spätere Implementierung.

## Leitbild

Das Repository entwickelt sich von einer einzelnen Bibliothek zu einer zusammenhängenden Arbeitsumgebung für Elektroplanung mit KiCad.

Dabei gelten weiterhin die verbindlichen Grundsätze:

- KiCad ist der Standard.
- Eigene Erweiterungen werden konsequent mit `Z_` gekennzeichnet.
- Deutsch ist die Primärsprache für Benutzeroberflächen, Dokumentation, Berichte und sichtbare Bezeichnungen.
- Internationale Fachkürzel dürfen als stabile technische IDs erhalten bleiben.
- Bibliothekspakete werden datengetrieben, reproduzierbar und prüfbar aufgebaut.

## Drei Hauptbereiche

### 1. Infrastruktur

Dieser Bereich stellt die Entwicklungs- und Installationsgrundlage bereit.

Dazu gehören insbesondere:

- `run_tests.bat`
- Python- und `.venv`-Einrichtung
- KiCad-Erkennung
- Benutzerordner und `KICAD_Z_*`-Variablen
- automatische Bibliotheksregistrierung
- CI
- Generatoren
- Qualitäts- und Kompatibilitätsprüfungen
- Release- und Installationsabläufe

### 2. Fachbibliothek

Hier entstehen die eigentlichen Gerätefamilien als vollständige Bibliothekspakete.

Jede Gerätefamilie soll nach Möglichkeit enthalten:

- dokumentierten Goldstandard
- Master-Symbol
- Varianten
- Footprintentscheidung
- Gerätekatalogdaten
- zweisprachige Metadaten
- Vorschauen
- Beispiel- oder Referenzprojekt
- automatisierte Tests
- Qualitätsstatus

Die zuerst priorisierte Familie ist der Leitungsschutzschalter mit den sichtbaren deutschen Symbolnamen:

- `LS_1P`
- `LS_1P_N`
- `LS_2P`
- `LS_3P`
- `LS_3P_N`
- `LS_4P`

Die bestehende technische Bibliothekskennung `Z_MCB` bleibt zunächst aus Kompatibilitätsgründen erhalten.

### 3. Werkzeuge

Dieser Bereich fasst die projektinternen Hilfsprogramme zusammen.

Geplante Werkzeuge:

- `Z_Cockpit`
- `Z_Bibliotheks-Viewer`
- `Z_Validator`
- `Z_Generator`
- `Z_Bibliotheksmanager`
- `Z_Projektprüfung`
- später optional ein KiCad-Plugin

## Z_Cockpit

`Z_Cockpit` ist als zentraler Einstiegspunkt und nicht nur als Viewer gedacht.

Es soll langfristig folgende Bereiche zusammenführen:

- Projektstatus
- Bibliotheken
- Goldstandards
- Generatoren
- Qualität
- Tests
- Dokumentation
- Werkzeuge
- Einstellungen

### Projektstatus

Das Cockpit soll sichtbar machen:

- Anzahl vorhandener und vollständiger Symbole
- Footprintabdeckung
- 3D-Modellabdeckung
- Dokumentationsstand
- Test- und CI-Status
- Status der Goldstandards
- fehlende Datenblätter
- fehlende oder veraltete Zuordnungen
- nächste offene Arbeitspakete

Ziel ist, dass der nächste Arbeitsschritt nach einer Pause ohne erneute Bestandsaufnahme erkennbar ist.

### Bibliotheks-Viewer

Die erste praktisch nutzbare Ausbaustufe des Cockpits ist ein Bibliotheks-Viewer.

Version 1 soll mindestens bieten:

- Familiennavigation
- Symbolvorschau
- Suche
- deutsche Anzeigenamen
- technische IDs
- Qualitätsstatus
- Symbol-, Footprint- und Katalogzuordnung
- Anzeige der Dokumentation
- Familienansicht mit mehreren Polvarianten

Spätere Erweiterungen:

- Symbolvergleich zwischen Versionen
- Vergleichsansicht mehrerer Familienvarianten
- 3D-Vorschau
- direkter Aufruf eines Referenzprojekts
- Qualitätsprüfung aus der Oberfläche

### Herstellervergleich

Herstellerdarstellungen dürfen als fachliche Referenz ausgewertet werden, werden aber nicht blind kopiert.

Für den Goldstandard wird dokumentiert:

- welche Herstellerunterlagen betrachtet wurden
- welche grafischen Gemeinsamkeiten erkennbar sind
- welche Darstellung norm- und KiCad-konform übernommen wird
- welche herstellerspezifischen Details bewusst nicht übernommen werden

Der daraus abgeleitete Projektstandard bleibt herstellerneutral.

## LS-Master und grafischer Goldstandard

Vor dem Ausbau der vollständigen LS-Familie wird ein Master-Symbol festgelegt.

Der LS-Master muss folgende drei Säulen erfüllen:

1. normgerecht nach den herangezogenen IEC-/DIN-Grundlagen
2. KiCad-konform hinsichtlich Raster, Pins, Texte, Dateiformat und ERC
3. praxisgerecht und für deutschsprachige Elektroplaner unmittelbar erkennbar

Zu dokumentieren und zu testen sind mindestens:

- vertikale Ausrichtung
- Anschluss 1 oben und Anschluss 2 unten
- 100-mil-Anschlussraster
- 100-mil-Pinlänge
- 10-mil-Standardlinienbreite
- 50-mil-Standardtextgröße
- einheitlicher Kontaktwinkel
- einheitliche Auslöserdarstellung
- identische Proportionen bei allen Polvarianten
- mechanische Kopplung bei mehrpoligen Varianten
- passive Pin-Typen, solange fachlich nichts anderes begründet ist
- ERC-Verhalten
- `Z_`-Namensregel
- deutsche sichtbare Bezeichnung `LS`

## Entwicklungsstufen

### Stufe 1 – Dokumentation und Viewer

- Suite-Architektur dokumentieren
- LS-Goldstandard dokumentieren
- vorhandene SVG-/HTML-Daten für einen Viewer wiederverwenden
- Familien- und Qualitätsübersicht erzeugen

### Stufe 2 – Manager

- Bibliotheken und `KICAD_Z_*` prüfen
- Installationsstatus anzeigen
- fehlende Registrierungen melden
- Aktualisierung und Reparatur anstoßen

### Stufe 3 – Assistent

- Gerätevarianten datengetrieben erzeugen
- Katalog, Dokumentation und Tests ergänzen
- Projektprüfungen durchführen
- optional als KiCad-Plugin integrieren

## Technische Strategie

Die erste Version des Cockpits soll als eigenständiges Python-Werkzeug entstehen. Das erleichtert Entwicklung, Tests und Unterstützung mehrerer KiCad-Versionen.

Eine Plugin-Integration wird erst verfolgt, wenn Datenmodell, Viewer und Qualitätsfunktionen stabil sind.

## Abgrenzung

Das Cockpit ersetzt GitHub-Issues, Pull Requests und CI nicht. Es stellt den fachlichen Projekt- und Bibliotheksstatus übersichtlich dar und verlinkt auf die vorhandenen Quellen.

Es soll keine unkontrollierte zweite Aufgabenverwaltung entstehen. Offene Arbeiten bleiben in GitHub nachvollziehbar; das Cockpit kann daraus später eine lesbare Statusansicht erzeugen.

## Nächste konkrete Schritte

1. LS-Master-Goldstandard gegen bestehende `ZSYM-*`-Regeln abgleichen.
2. Das bisherige Platzhaltersymbol `Z_MCB:MCB` durch eine fachlich erkennbare LS-Darstellung ergänzen.
3. Deutsche sichtbare Symbolnamen und kompatible technische IDs festlegen.
4. Varianten 1P, 1P+N, 2P, 3P, 3P+N und 4P datengetrieben vorbereiten.
5. Eine erste statische Viewer-Seite aus Katalog-, Qualitäts- und Vorschaudaten erzeugen.
6. Danach einen kleinen Verteilerplan als Praxistest erstellen.

## Entscheidungsstatus

Dieses Konzept ist als verbindliche Zielrichtung beschlossen. Einzelne technische Details dürfen in späteren Issues und Pull Requests präzisiert werden, ohne die drei Hauptbereiche oder die Grundsätze aufzuheben.
