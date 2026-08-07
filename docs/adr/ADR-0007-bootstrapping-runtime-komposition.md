# ADR-0007 – Bootstrapping und Runtime-Komposition

**Status:** Angenommen  
**Datum:** 2026-08-06

## Kontext

ProjectOS benötigt eine deterministische, testbare und offlinefähige Startsequenz. Module, Adapter und Plugins dürfen nicht unkontrolliert globale Zustände verändern oder Abhängigkeiten verstecken.

## Entscheidung

ProjectOS verwendet einen zentralen Bootstrapper und eine explizite Runtime-Komposition.

Verbindlich sind:

- zentrale Modulregistrierung,
- Constructor Injection,
- unveränderliche Runtime-Komposition nach erfolgreichem Aufbau,
- vollständige Konfigurations-, Registry-, Abhängigkeits- und Migrationsprüfung vor Betriebsbereitschaft,
- modulbezogene Kritikalitätsstufen,
- Safe Mode ohne externe Plugins,
- Health Checks als Voraussetzung für `READY`,
- kontrolliertes Herunterfahren in umgekehrter Startreihenfolge,
- alternative Adapter für Test und Simulation bei gleicher fachlicher Komposition.

## Konsequenzen

### Positiv

- reproduzierbarer Systemstart,
- klare Abhängigkeitsstruktur,
- bessere Testbarkeit,
- isolierbare Fehler,
- sicherer Plugin-Betrieb,
- nachvollziehbare Diagnosezustände.

### Negativ

- zusätzlicher Aufwand für Modulmetadaten und Registrierungen,
- Änderungen an Runtime-Abhängigkeiten können einen Neustart erfordern,
- strengere Startvalidierung kann frühe Entwicklungsstände blockieren.

## Verworfene Alternativen

### Selbstregistrierende Module

Verworfen wegen versteckter globaler Zustände und nicht deterministischer Reihenfolge.

### Globaler Service Locator

Verworfen wegen schlechter Testbarkeit und unsichtbarer Abhängigkeiten.

### Teilweiser Start ohne zentrale Validierung

Verworfen, weil inkonsistente Runtime-Zustände und spätere schwer nachvollziehbare Fehler drohen.

## Bezug

- AP-0017 – Konfigurationssystem und Registry
- AP-0018 – Plugin- und Erweiterungsmodell
- AP-0019 – Bootstrapping, Startsequenz und Runtime-Komposition
