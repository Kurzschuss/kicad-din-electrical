# ADR-0006 – Plugin- und Erweiterungsmodell

**Status:** Angenommen  
**Datum:** 2026-08-06

## Kontext

ProjectOS soll durch zusätzliche Domänen, Adapter, Importe, Exporte, Validierungen, Simulationen und Darstellungen erweiterbar sein. Unkontrollierte dynamische Erweiterungen würden jedoch Architekturgrenzen, Sicherheit, Offline-Fähigkeit und Reproduzierbarkeit gefährden.

## Entscheidung

ProjectOS verwendet ein manifestbasiertes, versioniertes und registriertes Plugin-Modell.

Verbindlich sind:

- stabile Plugin-Kennungen,
- semantische Versionen,
- versionierte Erweiterungspunkte,
- zentrale Plugin-Registry,
- vollständige Abhängigkeits- und Konfliktprüfung vor Aktivierung,
- Berechtigungen nach Minimalprinzip,
- Integritäts- und Vertrauensprüfung,
- Quarantäne für fehlerhafte oder nicht vertrauenswürdige Plugins,
- Nutzung des zentralen Konfigurationssystems,
- versionierte und idempotente Plugin-Migrationen,
- Simulation externer Nebenwirkungen,
- vollständig funktionsfähiger Kern ohne Plugins.

Plugins dürfen geschützte Kernfunktionen, Sicherheitsentscheidungen, Audit-Integrität und autoritative Persistenzregeln nicht ersetzen.

## Konsequenzen

### Positiv

- kontrollierte Erweiterbarkeit,
- klare Kompatibilitätsgrenzen,
- bessere Testbarkeit,
- reproduzierbarer Offline-Betrieb,
- geringeres Risiko für Kern und Projektdaten.

### Negativ

- zusätzlicher Manifest- und Registry-Aufwand,
- strengere Plugin-Verträge,
- Isolation und Signaturprüfung erhöhen die technische Komplexität.

## Alternativen

### Freies dynamisches Laden

Verworfen, da Konflikte, Sicherheitsrisiken und nicht reproduzierbare Zustände entstehen können.

### Keine Plugins

Verworfen, da Domänen- und Adaptererweiterungen sonst Änderungen am Kern erzwingen würden.

### Vollständige Prozessisolation für alle Plugins

Für die erste Version nicht generell vorgeschrieben. Sie bleibt für Plugins mit erhöhten Rechten oder externen Nebenwirkungen bevorzugt.
