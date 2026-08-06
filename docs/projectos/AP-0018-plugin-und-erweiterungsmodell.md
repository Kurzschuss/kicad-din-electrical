# AP-0018 – Plugin- und Erweiterungsmodell

**Status:** Abgeschlossen  
**Version:** 1.0  
**Sprint:** 002 – Core Object Model  
**Abhängigkeiten:** AP-0012 bis AP-0017, ADR-0001 bis ADR-0005

## 1. Ziel

Dieses Arbeitspaket definiert ein kontrolliertes, versioniertes und offlinefähiges Erweiterungsmodell für ProjectOS.

Plugins dürfen ProjectOS erweitern, ohne Kernmodule direkt zu verändern oder Architekturgrenzen zu umgehen.

## 2. Grundsätze

- Plugins sind optionale Erweiterungen, keine Voraussetzung für den Kernbetrieb.
- Der Kern bleibt auch ohne installierte Plugins lauffähig.
- Plugins greifen ausschließlich über dokumentierte Erweiterungspunkte zu.
- Direkte Änderungen an fremden Aggregaten oder internen Persistenzstrukturen sind unzulässig.
- Jede Erweiterung besitzt eine eindeutige Kennung und Version.
- Laden, Aktivieren, Deaktivieren und Aktualisieren sind nachvollziehbar und auditierbar.
- Der vollständige Betrieb bleibt offline möglich.

## 3. Plugin-Arten

ProjectOS unterscheidet:

- Domänen-Plugins
- Adapter-Plugins
- Import-/Export-Plugins
- Validierungs-Plugins
- Simulations-Plugins
- Darstellungs-Plugins
- Werkzeug-Plugins

Sicherheits-, Berechtigungs- und Persistenzkern dürfen nicht durch frei ladbare Plugins ersetzt werden.

## 4. Plugin-Kennung

Schema:

```text
PLG-<HERAUSGEBER>-<NAME>
```

Beispiel:

```text
PLG-PROJECTOS-KICAD-EXPORT
```

Die Kennung ist dauerhaft, eindeutig und wird nicht wiederverwendet.

## 5. Plugin-Manifest

Jedes Plugin enthält ein Manifest mit mindestens:

```yaml
plugin:
  id: PLG-PROJECTOS-KICAD-EXPORT
  name: KiCad-Export
  version: 1.0.0
  api_version: 1.0
  publisher: ProjectOS
  entry_point: projectos_kicad_export
  capabilities:
    - export.kicad
  permissions:
    - PERM-PROJECT-READ
  dependencies:
    - id: projectos-core
      version: ">=1.0.0 <2.0.0"
  offline_supported: true
  signature_required: true
```

## 6. Erweiterungspunkte

Verbindliche Erweiterungspunkte:

- DomainModule
- ValidationRuleProvider
- SimulationProvider
- ImportProvider
- ExportProvider
- PresentationExtension
- CommandRegistrationProvider
- QueryRegistrationProvider
- EventHandlerProvider
- DocumentationProvider

Jeder Erweiterungspunkt besitzt einen versionierten Vertrag.

## 7. Plugin-Lebenszyklus

```text
ENTDECKT → GEPRÜFT → REGISTRIERT → AKTIVIERT → DEAKTIVIERT → ENTFERNT
```

Fehlerhafte oder inkompatible Plugins erhalten den Status `QUARANTÄNE`.

## 8. Ladeprozess

1. Plugin-Verzeichnisse ermitteln
2. Manifest lesen
3. Manifest-Schema validieren
4. Kennung und Version prüfen
5. Signatur und Integrität prüfen
6. Abhängigkeiten auflösen
7. Berechtigungsanforderungen prüfen
8. Erweiterungspunkte registrieren
9. Konflikte erkennen
10. Plugin aktivieren
11. Ergebnis protokollieren und auditieren

Ein Fehler in einem optionalen Plugin darf den Kernstart nur dann verhindern, wenn das Plugin ausdrücklich als projektkritisch markiert ist.

## 9. Abhängigkeiten

- Abhängigkeiten werden ausschließlich über Plugin-Kennungen und Versionsbereiche beschrieben.
- Zyklische Abhängigkeiten sind unzulässig.
- Fehlende Pflichtabhängigkeiten verhindern die Aktivierung.
- Optionale Abhängigkeiten werden ausdrücklich gekennzeichnet.
- Abhängigkeiten dürfen nicht während des Starts aus dem Internet nachgeladen werden.

## 10. Konfliktregeln

Konflikte entstehen unter anderem bei:

- doppelten Plugin-Kennungen,
- mehrfach registrierten eindeutigen Erweiterungspunkten,
- widersprüchlichen Versionsanforderungen,
- nicht erlaubten Berechtigungen,
- Überschreiben geschützter Registry-Einträge.

Konflikte werden vor der Aktivierung vollständig ausgewertet.

## 11. Sicherheit

- Plugins gelten grundsätzlich als nicht vertrauenswürdig.
- Berechtigungen folgen dem Minimalprinzip.
- Dateisystem-, Netzwerk- und Prozesszugriffe werden über kontrollierte Schnittstellen bereitgestellt.
- Geheimnisse werden nur über Secret-Provider übergeben.
- Dynamisch geladener Code muss aus registrierten Quellen stammen.
- Manipulierte oder unbekannte Pakete werden nicht aktiviert.
- Kritische Plugin-Aktionen sind auditpflichtig.

## 12. Vertrauensstufen

Vorgesehene Stufen:

- CORE
- VERIFIED
- TRUSTED
- LOCAL
- UNTRUSTED
- BLOCKED

Die Vertrauensstufe allein ersetzt keine Berechtigungsprüfung.

## 13. Sandbox und Isolation

Plugins sollen, soweit technisch möglich, isoliert ausgeführt werden.

Mögliche Isolationsstufen:

- In-Process mit eingeschränkten Schnittstellen
- separater Prozess
- simulierter Adapter
- vollständig deaktiviert

Plugins mit externen oder erhöhten Rechten sollen bevorzugt außerhalb des Kernprozesses laufen.

## 14. Plugin-Konfiguration

Plugin-Konfiguration liegt unter:

```text
config/plugins/<plugin-id>/
```

Sie wird mit dem zentralen Konfigurationssystem aus AP-0017 validiert.

Plugins dürfen keine eigenen parallelen Konfigurationsmechanismen als autoritative Quelle einführen.

## 15. Plugin-Registry

Vorgesehene Datei:

```text
config/registries/plugins.yaml
```

Beispiel:

```yaml
plugins:
  - id: PLG-PROJECTOS-KICAD-EXPORT
    enabled: true
    required: false
    trust_level: VERIFIED
    source: local
    allowed_capabilities:
      - export.kicad
```

## 16. Aktualisierung und Migration

- Plugin-Aktualisierungen werden versioniert durchgeführt.
- Inkompatible Änderungen benötigen eine neue Hauptversion.
- Plugin-eigene Datenmigrationen verwenden `RM-*`-Kennungen.
- Vor risikobehafteten Migrationen wird eine Sicherung erstellt.
- Downgrades sind nur zulässig, wenn eine geprüfte Rückwärtsmigration existiert.
- Kernmigrationen dürfen nicht durch Plugins verändert werden.

## 17. Deaktivierung und Entfernung

Vor der Deaktivierung wird geprüft:

- ob aktive Projekte das Plugin benötigen,
- ob offene Prozesse oder Outbox-Einträge bestehen,
- ob Plugin-Daten erhalten werden müssen,
- ob Kompensationsschritte erforderlich sind.

Die Entfernung löscht nicht automatisch fachlich relevante Daten.

## 18. Simulation

Jedes Plugin mit Nebenwirkungen muss einen Simulationsmodus oder einen simulierten Ersatzadapter bereitstellen.

Im Simulationsmodus sind produktive externe Änderungen untersagt.

## 19. Fehlerkennungen

```text
ERR-PLG-0001  Plugin-Manifest ungültig
ERR-PLG-0002  Plugin-Kennung doppelt
ERR-PLG-0003  Plugin-Version inkompatibel
ERR-PLG-0004  Pflichtabhängigkeit fehlt
ERR-PLG-0005  Abhängigkeitszyklus erkannt
ERR-PLG-0006  Signatur oder Integrität ungültig
ERR-PLG-0007  Berechtigung nicht zulässig
ERR-PLG-0008  Erweiterungspunkt nicht unterstützt
ERR-PLG-0009  Plugin-Aktivierung fehlgeschlagen
ERR-PLG-0010  Plugin befindet sich in Quarantäne
```

## 20. Basisschnittstellen

```text
Plugin
PluginManifest
PluginContext
PluginLoader
PluginRegistry
PluginDependencyResolver
PluginIntegrityVerifier
PluginLifecycleManager
ExtensionPoint<T>
```

## 21. Verzeichnisstruktur

```text
src/core/plugins/
├── contracts/
├── loading/
├── registry/
├── security/
├── lifecycle/
└── isolation/

plugins/
├── bundled/
├── local/
└── quarantine/

config/plugins/
config/registries/plugins.yaml
```

## 22. Testanforderungen

Mindestens zu testen sind:

- gültige und ungültige Manifeste,
- Versionskompatibilität,
- fehlende und zyklische Abhängigkeiten,
- doppelte Registrierungen,
- Signatur- und Integritätsfehler,
- Berechtigungsbeschränkungen,
- Aktivierung und Deaktivierung,
- Quarantäne,
- Wiederanlauf nach Plugin-Fehlern,
- Offline-Betrieb,
- Simulationsmodus,
- Plugin-Datenmigrationen.

## 23. Verbindliche Entscheidungen

1. Plugins sind optional und dürfen den Kern nicht ersetzen.
2. Erweiterungen erfolgen ausschließlich über versionierte Erweiterungspunkte.
3. Jedes Plugin besitzt Manifest, Kennung, Version und Berechtigungsbedarf.
4. Plugin-Abhängigkeiten werden vor Aktivierung vollständig geprüft.
5. Plugins gelten standardmäßig als nicht vertrauenswürdig.
6. Kritische Rechte werden nicht automatisch gewährt.
7. Plugin-Konfiguration und Registrierung nutzen die zentrale ProjectOS-Infrastruktur.
8. Plugin-Migrationen sind versioniert, idempotent und nachvollziehbar.
9. Externe Nebenwirkungen müssen simulierbar sein.
10. Der Kernbetrieb bleibt offline und ohne Plugins möglich.

## 24. Definition of Done

AP-0018 ist abgeschlossen, wenn Plugin-Arten, Manifest, Kennungen, Erweiterungspunkte, Ladeprozess, Abhängigkeiten, Konfliktregeln, Sicherheit, Isolation, Migration, Simulation und Tests verbindlich definiert sind.

## 25. Commit-Vorschlag

```text
feat(plugins): AP-0018 Plugin- und Erweiterungsmodell definieren
```

## 26. Nächster Schritt

AP-0019 – Bootstrapping, Startsequenz und Runtime-Komposition.
