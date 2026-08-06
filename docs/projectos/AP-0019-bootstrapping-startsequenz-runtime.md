# AP-0019 – Bootstrapping, Startsequenz und Runtime-Komposition

**Status:** Abgeschlossen  
**Version:** 1.0  
**Sprint:** 002 – Core Object Model  
**Abhängigkeiten:** AP-0013 bis AP-0018, ADR-0001 bis ADR-0006

## 1. Ziel

Dieses Arbeitspaket definiert den verbindlichen Startprozess von ProjectOS und die Zusammensetzung der Laufzeitumgebung.

Ziele:

- deterministische Startsequenz,
- klare Trennung von Bootstrapping, Domäne, Anwendung und Infrastruktur,
- vollständige Validierung vor Betriebsbereitschaft,
- sichere Modul- und Plugin-Aktivierung,
- reproduzierbarer Offline-Betrieb,
- kontrollierter Start, Neustart und Abbruch,
- aussagekräftige Health- und Diagnosezustände.

## 2. Grundsätze

- Die Runtime wird ausschließlich über registrierte Module zusammengesetzt.
- Keine Domäne darf sich selbst global registrieren.
- Abhängigkeiten werden explizit deklariert und zentral aufgelöst.
- Der Systemstart gilt erst nach erfolgreicher Validierung als abgeschlossen.
- Kritische Fehler führen zu einem kontrollierten Abbruch.
- Optionale Komponenten dürfen isoliert deaktiviert werden.
- Start und Simulation verwenden dieselben fachlichen Komponenten, aber getrennte Adapter.

## 3. Startphasen

ProjectOS verwendet folgende verbindliche Reihenfolge:

1. Prozessumgebung prüfen
2. Basisdiagnose initialisieren
3. Startparameter einlesen
4. Konfigurationsquellen laden
5. Konfiguration validieren und Snapshot bilden
6. Registries laden und referenziell prüfen
7. Kernmodule registrieren
8. Infrastrukturadapter registrieren
9. Plugins entdecken und prüfen
10. Dependency Graph aufbauen
11. Abhängigkeiten validieren
12. Persistenz öffnen
13. Schema- und Migrationsstand prüfen
14. erforderliche Migrationen ausführen
15. Repositories und Unit of Work initialisieren
16. Event Bus, Outbox und Audit initialisieren
17. Command-, Query- und Prozesspipeline initialisieren
18. Domänenmodule starten
19. Hintergrunddienste starten
20. Health Checks ausführen
21. Runtime Snapshot erzeugen
22. Betriebsbereitschaft veröffentlichen

## 4. Bootstrapper

Zentrale Schnittstelle:

```text
ProjectOSBootstrapper
```

Operationen:

```text
build(startup_request)
start(runtime)
stop(runtime)
restart(runtime)
```

Der Bootstrapper enthält keine Fachlogik. Er koordiniert ausschließlich Aufbau, Prüfung, Start und kontrolliertes Herunterfahren.

## 5. Startanforderung

Objekt:

```text
StartupRequest
```

Pflichtfelder:

```text
startup_id
started_at
execution_mode
configuration_sources
project_reference
requested_modules
safe_mode
simulation_mode
correlation_id
```

Ausführungsmodi:

```text
DESKTOP
CLI
SERVICE
TEST
SIMULATION
MIGRATION
DIAGNOSTIC
```

## 6. Runtime-Komposition

Objekt:

```text
RuntimeComposition
```

Enthält:

- Konfigurations-Snapshot,
- Registry-Snapshot,
- Service-Container,
- aktive Module,
- aktive Plugins,
- Persistenzadapter,
- Event-Infrastruktur,
- Anwendungs-Pipelines,
- Hintergrunddienste,
- Health-Registry,
- Runtime-Metadaten.

Nach erfolgreichem Aufbau ist die Komposition unveränderlich. Änderungen erfordern einen kontrollierten Neuaufbau oder Neustart.

## 7. Modulvertrag

Schnittstelle:

```text
ProjectOSModule
```

Operationen:

```text
describe()
register_services(context)
validate(context)
start(context)
stop(context)
health(context)
```

Jedes Modul deklariert:

- Modulkennung,
- Version,
- verantwortliche Domäne,
- benötigte Module,
- optionale Abhängigkeiten,
- bereitgestellte Dienste,
- benötigte Konfiguration,
- Startpriorität,
- Kritikalität,
- Simulationsfähigkeit.

## 8. Dependency Injection

ProjectOS verwendet Constructor Injection als Standard.

Nicht zulässig:

- globaler Service Locator in Domänenlogik,
- versteckte Singleton-Zugriffe,
- direkte Erzeugung konkreter Infrastrukturadapter in Domänenobjekten,
- zyklische Modulabhängigkeiten.

Lebensdauern:

```text
SINGLETON
RUNTIME
REQUEST
TRANSIENT
```

Domänenobjekte sind grundsätzlich nicht als globale Singletons zu registrieren.

## 9. Abhängigkeitsgraph

Vor dem Start wird ein gerichteter Abhängigkeitsgraph erzeugt.

Geprüft werden:

- fehlende Pflichtabhängigkeiten,
- Versionsinkompatibilitäten,
- Zyklen,
- doppelte Dienstregistrierungen,
- widersprüchliche Lebensdauern,
- nicht erlaubte Schichtabhängigkeiten,
- Plugin-Konflikte.

Der Start wird bei kritischen Fehlern abgebrochen.

## 10. Kritikalität

Module werden klassifiziert als:

```text
CORE_REQUIRED
DOMAIN_REQUIRED
OPTIONAL
DEVELOPMENT_ONLY
SIMULATION_ONLY
```

Ausfallregeln:

- `CORE_REQUIRED`: Startabbruch,
- `DOMAIN_REQUIRED`: betroffene Domäne bleibt deaktiviert,
- `OPTIONAL`: Warnung und isolierte Deaktivierung,
- `DEVELOPMENT_ONLY`: im Produktivbetrieb ignorieren,
- `SIMULATION_ONLY`: nur im Simulationsmodus aktivieren.

## 11. Safe Mode

Der abgesicherte Modus startet ausschließlich:

- Core Runtime,
- Konfigurationsdiagnose,
- Registry-Diagnose,
- Persistenzdiagnose im Lesemodus,
- Migrationsprüfung ohne automatische Ausführung,
- Audit- und Fehleranzeige,
- administrative Reparaturwerkzeuge.

Nicht vertrauenswürdige Plugins und externe Adapter bleiben deaktiviert.

## 12. Startzustände

```text
CREATED
CONFIGURING
VALIDATING
COMPOSING
MIGRATING
STARTING
READY
DEGRADED
FAILED
STOPPING
STOPPED
```

Jeder Zustandswechsel wird protokolliert. Sicherheits- und migrationsrelevante Übergänge werden auditiert.

## 13. Health Checks

Schnittstelle:

```text
HealthCheck
```

Ergebnis:

```text
HealthResult
```

Statuswerte:

```text
HEALTHY
DEGRADED
UNHEALTHY
UNKNOWN
```

Prüfbereiche:

- Konfiguration,
- Registries,
- Persistenz,
- Migrationen,
- Outbox,
- Dead-Letter-Ablage,
- Audit-Integrität,
- Module,
- Plugins,
- Hintergrunddienste,
- freier Speicherplatz,
- Projektzugriff.

## 14. Betriebsbereitschaft

ProjectOS ist nur dann `READY`, wenn:

- alle Kernmodule gestartet sind,
- Konfiguration und Registries gültig sind,
- Persistenz und Migrationen erfolgreich sind,
- kritische Health Checks bestanden wurden,
- keine blockierende Dead-Letter- oder Audit-Störung vorliegt.

Bei nicht kritischen Einschränkungen wird `DEGRADED` verwendet.

## 15. Hintergrunddienste

Beispiele:

- Outbox-Verarbeitung,
- Retry-Scheduler,
- Dead-Letter-Überwachung,
- periodische Integritätsprüfung,
- Sicherungsplanung,
- Plugin-Überwachung,
- lokale Indexaktualisierung.

Jeder Dienst besitzt:

- eindeutige Kennung,
- Start- und Stop-Vertrag,
- Abbruchtoken,
- Health Check,
- Fehlerstrategie,
- konfigurierbare Intervalle,
- Simulationsverhalten.

## 16. Kontrolliertes Herunterfahren

Reihenfolge:

1. neue Befehle blockieren,
2. laufende Anwendungsfälle abschließen oder abbrechen,
3. Hintergrunddienste stoppen,
4. Outbox-Status sichern,
5. Module in umgekehrter Startreihenfolge stoppen,
6. Persistenzverbindungen schließen,
7. Runtime Snapshot und Abschlussdiagnose schreiben,
8. Status `STOPPED` setzen.

Ein erzwungener Abbruch muss beim nächsten Start erkannt werden.

## 17. Runtime Snapshot

Objekt:

```text
RuntimeSnapshot
```

Enthält mindestens:

- Runtime-Kennung,
- Startzeit,
- Projektversion,
- Konfigurationsversion,
- Registry-Version,
- Datenbankschema-Version,
- aktive Module und Versionen,
- aktive Plugins und Vertrauensstatus,
- Health-Zustand,
- Ausführungsmodus,
- Host-Informationen ohne sensible Daten,
- Korrelationskennung.

Der Snapshot unterstützt Diagnose, Reproduzierbarkeit und Simulation.

## 18. Fehlerkennungen

```text
ERR-BOOT-0001  Konfiguration konnte nicht geladen werden
ERR-BOOT-0002  Registry-Validierung fehlgeschlagen
ERR-BOOT-0003  Zyklische Modulabhängigkeit
ERR-BOOT-0004  Pflichtmodul fehlt
ERR-BOOT-0005  Dienstregistrierung widersprüchlich
ERR-BOOT-0006  Persistenz konnte nicht geöffnet werden
ERR-BOOT-0007  Migration fehlgeschlagen
ERR-BOOT-0008  Kernmodul konnte nicht gestartet werden
ERR-BOOT-0009  Health Check blockiert Betriebsbereitschaft
ERR-BOOT-0010  Herunterfahren unvollständig
```

## 19. Testanforderungen

- deterministische Startreihenfolge,
- Erkennung fehlender und zyklischer Abhängigkeiten,
- korrektes Verhalten aller Kritikalitätsstufen,
- Safe-Mode-Start ohne Plugins,
- Startabbruch bei ungültiger Konfiguration,
- Migrationsfehler mit Rollback,
- Health-Status `READY`, `DEGRADED` und `FAILED`,
- kontrolliertes Herunterfahren,
- Wiederanlauf nach erzwungenem Abbruch,
- reproduzierbarer Simulationsstart,
- keine externen Nebenwirkungen im Test- und Simulationsmodus.

## 20. Verzeichnisstruktur

```text
src/core/runtime/
├── bootstrap/
├── composition/
├── modules/
├── dependency_injection/
├── health/
├── hosted_services/
├── diagnostics/
└── shutdown/

config/runtime/
tests/unit/core/runtime/
tests/integration/runtime/
tests/simulation/runtime/
docs/architektur/runtime/
```

## 21. Architekturentscheidungen

1. Die Runtime wird zentral und deterministisch zusammengesetzt.
2. Module registrieren sich nicht selbst global.
3. Constructor Injection ist der Standard.
4. Die fertige Runtime-Komposition ist unveränderlich.
5. Der Start erfolgt erst nach vollständiger Validierung.
6. Plugins werden vor Aktivierung geprüft und isoliert behandelt.
7. Safe Mode bleibt ohne externe Plugins funktionsfähig.
8. Betriebsbereitschaft und allgemeiner Prozessstart sind getrennte Zustände.
9. Simulation verwendet dieselbe Komposition mit alternativen Adaptern.
10. Herunterfahren erfolgt in umgekehrter Abhängigkeitsreihenfolge.

## 22. Definition of Done

AP-0019 gilt als abgeschlossen, wenn Startphasen, Modulvertrag, Dependency Injection, Abhängigkeitsgraph, Health Checks, Safe Mode, Runtime Snapshot und kontrolliertes Herunterfahren verbindlich definiert sind.

## 23. Commit-Vorschlag

```text
feat(runtime): AP-0019 Bootstrapping und Runtime-Komposition definieren
```

## 24. Nächster Schritt

AP-0020 – Sprint-002-Abschluss, Architektur- und Konsistenzprüfung.
