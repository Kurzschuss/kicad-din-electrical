# ADR-0005 – Zentrales Konfigurationssystem und versionierte Registries

**Status:** Angenommen  
**Datum:** 2026-08-06

## Kontext

ProjectOS benötigt eine zentrale, offlinefähige und nachvollziehbare Konfigurationsquelle. Befehle, Abfragen, Ereignisse, Handler, Domänen, Rollen, Berechtigungen und Migrationen müssen eindeutig registriert werden.

## Entscheidung

1. YAML ist das primäre menschenlesbare Konfigurationsformat.
2. Konfigurationsdateien werden gegen lokal versionierte Schemas validiert.
3. Domänen, Commands, Queries, Events, Handler, Rollen, Berechtigungen, Validierungsregeln, Migrationen und Plugins besitzen eigene Registries.
4. Nach erfolgreichem Start arbeitet die Runtime mit unveränderlichen Registry- und Konfigurationssnapshots.
5. Doppelte Kennungen, unbekannte Referenzen, zyklische Abhängigkeiten und inkompatible Versionen verhindern den Start.
6. Hot Reload ist nur für ausdrücklich freigegebene, nicht sicherheitskritische Werte zulässig.
7. Geheimnisse werden ausschließlich über eine Secret-Provider-Schnittstelle bezogen.
8. Alle Schemas und Registries müssen für den Offline-Betrieb lokal verfügbar sein.

## Konsequenzen

- Der Systemstart wird deterministisch und reproduzierbar.
- Registry-Konflikte werden früh erkannt.
- Simulationen, Builds und Validierungen können auf einen eindeutigen Snapshot verweisen.
- Änderungen an Registry-Verträgen benötigen Versionierung und gegebenenfalls Migrationen.
- Sicherheitskritische Änderungen erfordern Neustart und Auditierung.

## Alternativen

### Freie Registrierung im Programmcode

Verworfen, weil Konfiguration, Dokumentation und Laufzeitverhalten auseinanderlaufen könnten.

### Externe Registry als Pflichtdienst

Verworfen, weil dies Offline First verletzen würde.

### Uneingeschränktes Hot Reload

Verworfen, weil dadurch Sicherheits-, Konsistenz- und Reproduzierbarkeitsrisiken entstehen.
