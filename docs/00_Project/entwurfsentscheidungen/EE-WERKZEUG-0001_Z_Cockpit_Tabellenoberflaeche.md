# EE-WERKZEUG-0001 – Tabellenoberfläche für Z_Cockpit

## Status

Akzeptiert

## Datum

2026-08-04

## Kontext

`Z_Cockpit` soll als zentrale Arbeitsoberfläche der KiCad DIN Electrical Suite dienen. Die Bedienung muss für Anwender technischer Verwaltungs-, Tabellen- und CAD-Programme vertraut sein. Eine reine Kachel- oder Suchoberfläche erschwert die systematische Auswahl technischer Geräteparameter.

## Entscheidung

`Z_Cockpit` verwendet primär eine tabellenbasierte Oberfläche mit Auswahllisten und folgenden Bereichen:

1. Baumansicht der Gerätefamilien links.
2. Filterzeile mit Auswahllisten oberhalb der Gerätetabelle.
3. Sortierbare Gerätetabelle in der Mitte.
4. Eigenschaften des ausgewählten Geräts rechts oder unterhalb der Tabelle.
5. Registerkarten für Symbol-, Footprint- und 3D-Vorschau.
6. Statusleiste für KiCad-, Bibliotheks- und Qualitätszustand.

Die sichtbare Sprache ist Deutsch. Etablierte technische Kennungen wie `MCB`, `RCD` oder Bibliotheksnamen wie `Z_MCB` dürfen intern bestehen bleiben.

## Verbindliche Filter

Die erste Ausbaustufe enthält Auswahllisten für:

- Gerätefamilie
- Hersteller
- Polzahl
- Charakteristik
- Nennstrom
- Qualitätsstatus

Zusätzlich werden Schnellfilter vorgesehen:

- alle Geräte
- nur unvollständige Geräte
- nur Goldstandards
- ohne Footprint
- ohne 3D-Modell
- ohne Dokumentation
- ohne Tests

## Verbindliche Tabellenspalten

Mindestens:

- sichtbarer deutscher Gerätename
- technische ID
- Gerätefamilie
- Hersteller
- Polzahl
- Charakteristik
- Nennstrom
- Symbolstatus
- Footprintstatus
- 3D-Status
- Goldstandard
- Qualitätsstatus

## Bedienregeln

- Spalten sind per Klick sortierbar.
- Filter können kombiniert werden.
- Auswahl eines Datensatzes aktualisiert Eigenschaften und Vorschauen.
- Doppelklick öffnet später die passende Detailansicht.
- Kontextmenüs dürfen erst ergänzt werden, wenn die Grundbedienung stabil ist.
- Die Tabelle ist die primäre Arbeitsansicht; eine freie Textsuche ist ergänzend, nicht führend.

## Technische Umsetzung

Version 0.1 wird als statische HTML-Ansicht entwickelt, um Datenmodell, Spalten und Bedienfluss früh zu prüfen.

Spätere Desktop-Versionen sollen bevorzugt mit Python und Qt/PySide umgesetzt werden. Eine mögliche KiCad-Plugin-Integration folgt erst nach einer stabilen eigenständigen Anwendung.

## Folgen

### Vorteile

- vertraute Bedienung für technische Anwender
- systematische Auswahl ohne Tippfehler
- gute Vergleichbarkeit vieler Geräte
- Qualitätslücken werden direkt sichtbar
- gleiche Bedienlogik für Geräte, Goldstandards, Tests und Werkzeuge

### Nachteile

- auf kleinen Bildschirmen ist horizontales Scrollen erforderlich
- Filter- und Datenmodell müssen sorgfältig vereinheitlicht werden
- Vorschauen benötigen später zusätzliche Renderer

## Abgrenzung

Die Oberfläche ersetzt weder GitHub-Issues noch CI. Sie stellt vorhandene Projekt- und Qualitätsdaten dar und startet später bestehende Werkzeuge.
