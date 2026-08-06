# AP-0017 – Konfigurationssystem und Registry

**Status:** Abgeschlossen  
**Version:** 1.0  
**Sprint:** 002 – Core Object Model  
**Abhängigkeiten:** AP-0005, AP-0013, AP-0014, AP-0015, AP-0016, ADR-0001 bis ADR-0004

## 1. Ziel

Dieses Arbeitspaket definiert das zentrale Konfigurationssystem und die Registry-Infrastruktur von ProjectOS.

Ziele:

- zentrale und validierbare Konfiguration,
- eindeutige Registries für Domänen, Befehle, Abfragen, Ereignisse, Handler, Rollen und Berechtigungen,
- vollständiger Offline-Betrieb,
- sichere Überschreibungs- und Prioritätsregeln,
- reproduzierbare Startzustände,
- nachvollziehbare Konfigurationsänderungen.

## 2. Grundsätze

- Konfiguration vor Code.
- Jede Konfigurationsinformation besitzt genau eine autoritative Quelle.
- Unbekannte oder widersprüchliche Einträge verhindern den Systemstart.
- Domänenspezifische Konfiguration bleibt Eigentum der jeweiligen Domäne.
- Laufzeitwerte dürfen Architekturentscheidungen und fachliche Invarianten nicht umgehen.
- Geheimnisse werden nicht in normalen YAML-Dateien gespeichert.

## 3. Konfigurationsebenen

ProjectOS verwendet folgende Priorität, von niedrig nach hoch:

1. integrierte Standardwerte,
2. systemweite Konfiguration,
3. projektbezogene Konfiguration,
4. benutzerbezogene Darstellungseinstellungen,
5. Startparameter und ausdrücklich erlaubte Laufzeitüberschreibungen.

Höhere Ebenen dürfen nur Schlüssel überschreiben, die dafür freigegeben sind.

## 4. Verzeichnisstruktur

```text
config/
├── system/
├── domains/
├── application/
├── events/
├── registries/
├── security/
├── simulation/
├── schemas/
└── environments/
```

## 5. Konfigurationsvertrag

Jede Konfigurationsdatei enthält mindestens:

- Schema-Version,
- verantwortliche Domäne,
- Geltungsbereich,
- Änderungsstatus,
- fachliche oder technische Kennung,
- strukturierte Nutzdaten.

Beispiel:

```yaml
schema_version: "1.0"
domain: CORE
scope: system
configuration_id: CFG-CORE-0001
settings:
  locale: de-DE
  offline_mode: true
```

## 6. Schema-Validierung

Alle Konfigurationen werden vor Verwendung geprüft auf:

- gültige YAML-Syntax,
- bekannte Schema-Version,
- Pflichtfelder,
- Datentypen,
- zulässige Wertebereiche,
- unbekannte Schlüssel,
- doppelte Kennungen,
- referenzielle Integrität,
- unzulässige Überschreibungen.

Ein Fehler erzeugt ein strukturiertes Fehlerobjekt und verhindert bei verpflichtender Konfiguration den Start.

## 7. Registry-Konzept

Eine Registry ist ein versioniertes, maschinenlesbares Verzeichnis zulässiger Typen und Zuordnungen.

Verbindliche Registries:

- Domain Registry,
- Command Registry,
- Query Registry,
- Event Registry,
- Handler Registry,
- Role Registry,
- Permission Registry,
- Validation Rule Registry,
- Migration Registry,
- Plugin Registry.

## 8. Domain Registry

Die Domain Registry ist die Single Source of Truth für Bounded Contexts.

Pflichtfelder:

- `domain_id`,
- Name,
- Version,
- verantwortlicher Bereich,
- Status,
- Abhängigkeiten,
- Konfigurationspfade,
- unterstützte Objektarten.

## 9. Command-, Query- und Event-Registries

Diese Registries verknüpfen stabile technische Typen mit:

- Version,
- zuständiger Domäne,
- Behandler,
- Berechtigung,
- Transaktionsbedarf,
- Auditpflicht,
- Idempotenz,
- Simulationsfähigkeit.

Für jeden Typ darf pro Version genau ein primärer Behandler registriert sein.

## 10. Rollen- und Berechtigungsregister

Rollen und Berechtigungen werden nicht frei im Code definiert.

Die Registry enthält:

- stabile Kennung,
- Anzeigename,
- Beschreibung,
- Geltungsbereich,
- Abhängigkeiten,
- Ausschlüsse,
- Freigabestatus.

Whitelist, Blacklist und Ausnahmerechte referenzieren ausschließlich registrierte Berechtigungen.

## 11. Registry-Ladevorgang

Die Startreihenfolge lautet:

```text
Schemas laden
→ Kernkonfiguration laden
→ Domain Registry laden
→ abhängige Registries laden
→ Referenzen validieren
→ Konflikte prüfen
→ unveränderlichen Registry-Snapshot erzeugen
→ Runtime starten
```

## 12. Registry-Snapshot

Nach erfolgreicher Initialisierung wird ein unveränderlicher Snapshot erzeugt.

Er enthält:

- Snapshot-Kennung,
- Erzeugungszeit,
- Konfigurationshash,
- geladene Registry-Versionen,
- aktive Domänen,
- Warnungen,
- Quellreferenzen.

Jeder Build-, Simulations- und Validierungslauf verweist auf den verwendeten Snapshot.

## 13. Hot Reload

Hot Reload ist nur für ausdrücklich freigegebene, nicht sicherheitskritische Einstellungen zulässig.

Nicht zur Laufzeit änderbar sind insbesondere:

- Domänengrenzen,
- Ereignisverträge,
- Command- und Query-Zuordnungen,
- Rollen- und Berechtigungsstruktur,
- Migrationsdefinitionen,
- Persistenzschema.

Änderungen an diesen Bereichen benötigen einen kontrollierten Neustart.

## 14. Konfliktregeln

Konflikte werden nicht stillschweigend aufgelöst.

Ein Konflikt liegt unter anderem vor bei:

- doppelter Kennung,
- mehreren primären Handlern,
- unbekannter Domäne,
- zyklischer Abhängigkeit,
- inkompatibler Version,
- Überschreibung eines gesperrten Schlüssels,
- fehlender Berechtigung für eine registrierte Aktion.

## 15. Offline-Betrieb

Alle Schemas und Registries müssen lokal verfügbar sein.

Externe Quellen dürfen:

- niemals Voraussetzung für den Start sein,
- nur kontrolliert importiert werden,
- lokale Snapshots nicht unbemerkt überschreiben,
- ausschließlich über Adapter angebunden werden.

## 16. Audit und Sicherheit

Auditpflichtig sind:

- Änderungen an Rollen und Berechtigungen,
- Aktivierung oder Deaktivierung einer Domäne,
- Änderung sicherheitsrelevanter Konfiguration,
- Import externer Registry-Daten,
- manuelle Konfliktauflösung,
- Hot-Reload sicherheitsrelevanter Einstellungen.

Geheime Werte werden über eine gesonderte Secret-Provider-Schnittstelle bezogen.

## 17. Basisschnittstellen

```text
ConfigurationProvider
ConfigurationLoader
ConfigurationValidator
ConfigurationSnapshot
Registry<T>
RegistryEntry
RegistrySnapshot
RegistryValidator
SecretProvider
```

Wichtige Operationen:

```text
load()
validate()
get(key)
resolve(id, version)
list_active()
create_snapshot()
```

## 18. Fehlerkennungen

```text
ERR-CFG-0001  Konfigurationssyntax ungültig
ERR-CFG-0002  Schema-Version unbekannt
ERR-CFG-0003  Pflichtfeld fehlt
ERR-CFG-0004  Unbekannter Schlüssel
ERR-CFG-0005  Unzulässige Überschreibung
ERR-REG-0001  Registry-Eintrag doppelt
ERR-REG-0002  Referenz unbekannt
ERR-REG-0003  Mehrere primäre Handler
ERR-REG-0004  Zyklische Abhängigkeit
ERR-REG-0005  Inkompatible Version
```

## 19. Testanforderungen

- gültige Konfiguration wird geladen,
- ungültige Konfiguration verhindert den Start,
- Prioritätsregeln werden korrekt angewendet,
- gesperrte Schlüssel können nicht überschrieben werden,
- doppelte Registry-Einträge werden erkannt,
- zyklische Abhängigkeiten werden erkannt,
- Snapshots sind reproduzierbar,
- Offline-Start funktioniert ohne externe Quelle,
- Hot Reload ändert nur freigegebene Werte,
- sicherheitsrelevante Änderungen werden auditiert.

## 20. Vorgesehene Repository-Struktur

```text
src/core/configuration/
src/core/registry/
src/core/security/secrets/
config/registries/
config/schemas/
tests/unit/core/configuration/
tests/unit/core/registry/
tests/integration/configuration/
docs/architektur/konfiguration/
```

## 21. Architekturentscheidung

Für dieses Arbeitspaket wird vorgesehen:

`ADR-0005 – Zentrales Konfigurationssystem und versionierte Registries`

Verbindliche Entscheidungen:

1. YAML bleibt das primäre menschenlesbare Konfigurationsformat.
2. Schemas und Registries werden lokal versioniert.
3. Nach dem Start arbeitet die Runtime mit unveränderlichen Snapshots.
4. Konflikte führen zu einem klaren Fehler statt zu stillschweigender Auflösung.
5. Hot Reload ist nur für ausdrücklich freigegebene Werte zulässig.
6. Geheimnisse werden nicht in normalen Konfigurationsdateien gespeichert.

## 22. Definition of Done

AP-0017 ist abgeschlossen, wenn:

- Konfigurationsebenen und Prioritäten definiert sind,
- Schema-Validierung festgelegt ist,
- alle Kernregistries beschrieben sind,
- Registry-Snapshots definiert sind,
- Konflikt- und Hot-Reload-Regeln dokumentiert sind,
- Offline-, Audit-, Sicherheits- und Testanforderungen vorliegen,
- ADR-0005 angelegt ist.

Alle Kriterien sind mit diesem Dokument erfüllt.

## 23. Commit-Vorschlag

```text
feat(configuration): AP-0017 Konfigurationssystem und Registries definieren
```

## 24. Nächster Schritt

AP-0018 – Plugin- und Erweiterungsmodell.
