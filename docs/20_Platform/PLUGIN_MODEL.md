# Pluginmodell

**Dokument-ID:** PLT-0020  
**Titel:** Fachliches Modell für kontrollierte Erweiterbarkeit durch Plugins  
**Version:** 0.1.0  
**Status:** Entwurf  
**Stabilitätsklasse:** B  
**Autoritätsebene:** Plattformmodell  
**Erstellt:** 8. August 2026  
**Zuletzt geändert:** 8. August 2026

---

## 1. Zweck

Dieses Dokument definiert Plugins als kontrollierte Erweiterungsbausteine von ProjectOS.

Plugins dürfen neue Funktionen, Domänen, Adapter, Renderer, Integrationen oder Dienste ergänzen, ohne Core-Invarianten, Plattformverträge oder Domain Ownership zu umgehen.

## 2. Grundsatz

Für ProjectOS gilt:

> Erweiterbarkeit erfolgt über dokumentierte Verträge, nicht durch verdeckte Eingriffe in fremde Verantwortungsbereiche.

Plugins sind Gäste der Plattform und keine parallele Architektur.

## 3. Architekturstellung

Das Pluginmodell gehört zur Plattformebene.

Es baut insbesondere auf `PLATFORM_MODEL.md`, `CONFIGURATION_MODEL.md`, `AUTHORIZATION_MODEL.md`, `AUDIT_MODEL.md`, `BUS_MODEL.md`, `MEMORY_MODEL.md`, `SCHEMA_MODEL.md`, `RELATION_MODEL.md` und späteren Domänenverträgen auf.

Plugins dürfen Core nicht verändern.

## 4. Pluginobjekt

Ein Plugin besitzt mindestens:

- stabile Plugin-ID;
- Name;
- Version;
- Hersteller oder Quelle;
- Status;
- deklarierte Fähigkeiten;
- benötigte Plattformversion;
- benötigte Verträge und Abhängigkeiten;
- bereitgestellte Erweiterungspunkte;
- Konfigurationsschema;
- Berechtigungsanforderungen;
- Offline-Eigenschaften;
- Audit- und Herkunftsbezug.

## 5. Erweiterungspunkte

Die Plattform stellt ausdrücklich definierte Erweiterungspunkte bereit.

Beispiele:

- neue Domänenmodelle;
- neue Importe oder Exporte;
- neue Renderer;
- neue Simulationen;
- neue Validierungsbausteine;
- neue Suchadapter;
- neue externe Integrationen;
- neue Z_Cockpit-Ansichten;
- neue Bus-Consumer oder -Producer;
- neue Konfigurationsschemata.

Ein Plugin darf nur Erweiterungspunkte verwenden, die für seine Pluginart freigegeben sind.

## 6. Domain Ownership

Ein Plugin kann Eigentümer einer eigenen Domäne oder eines eigenen Erweiterungsbereichs sein.

Es darf jedoch keine fremde Domäne stillschweigend übernehmen oder deren Regeln überschreiben.

Domänenerweiterungen müssen über explizite Verträge, registrierte Erweiterungspunkte oder deklarierte Beziehungen erfolgen.

## 7. Core-Grenze

Plugins dürfen insbesondere nicht:

- Core-Invarianten verändern;
- Core-Schemata verdeckt überschreiben;
- stabile Identitäten umdeuten;
- Referenzregeln umgehen;
- Kernelkonzepte nachladen, die nicht Teil des freigegebenen Core sind.

Eine notwendige Core-Erweiterung erfordert weiterhin Governance und ADR.

## 8. Plattformgrenzen

Plugins dürfen Plattformdienste verwenden, aber nicht deren Zuständigkeit duplizieren.

Insbesondere dürfen Plugins keine eigene konkurrierende Wahrheit einführen für:

- Identität;
- Konten;
- Authentifizierung;
- Autorisierung;
- Rollen;
- Berechtigungen;
- Delegation;
- Organisation;
- Audit;
- Konfiguration;
- Projektgedächtnis.

## 9. Berechtigungen

Ein Plugin erhält keine impliziten Vollrechte.

Jeder sicherheitsrelevante Zugriff muss über die Autorisierungsplattform erfolgen.

Das Plugin muss deklarieren können:

- benötigte Berechtigungen;
- Gültigkeitsbereiche;
- optionale vs. zwingende Rechte;
- administrative Fähigkeiten;
- Zugriff auf personenbezogene oder vertrauliche Daten;
- Zugriff auf externe Systeme.

Fehlende Rechte dürfen nicht durch direkte Dateizugriffe oder versteckte Seiteneffekte umgangen werden.

## 10. Plugin-Berechtigungen und Benutzerrechte

Pluginberechtigungen und Benutzerberechtigungen bleiben getrennte Ebenen.

Eine Aktion darf nur ausgeführt werden, wenn sowohl Plugin als auch handelnder Akteur im relevanten Kontext dazu berechtigt sind, soweit die Operation einen Benutzerkontext besitzt.

Ein privilegiertes Plugin darf einem unberechtigten Benutzer keine zusätzlichen fachlichen Rechte verleihen.

## 11. Konfiguration

Plugins verwenden das kanonische Konfigurationsmodell.

Pluginkonfiguration muss:

- schema-basiert;
- validierbar;
- versionierbar;
- referenzierbar;
- mit Gültigkeitsbereich versehen;
- auditierbar, soweit relevant

sein.

Plugins dürfen keine versteckten Konfigurationsdateien als zweite Wahrheit verwenden, wenn die Werte fachlich relevant sind.

## 12. Geheimnisse

Geheimnisse wie API-Schlüssel, Tokens oder private Schlüssel werden nicht als normale Pluginkonfiguration gespeichert.

Plugins müssen Plattformmechanismen für geheime Werte verwenden, sobald diese definiert sind.

Z_Cockpit und Audit dürfen keine vollständigen Geheimnisse ausgeben.

## 13. Versionierung

Plugins besitzen eine eigene Version.

Zusätzlich müssen kompatible Versionen folgender Verträge eindeutig sein:

- Plattform;
- Schemata;
- Erweiterungspunkte;
- abhängige Plugins;
- Domänenverträge.

Nicht kompatible Plugins dürfen nicht stillschweigend aktiviert werden.

## 14. Abhängigkeiten

Pluginabhängigkeiten müssen explizit deklariert sein.

Abhängigkeiten können sein:

- zwingend;
- optional;
- alternative Provider;
- Versionsbereich;
- Capability-basierte Abhängigkeit.

Zyklische Abhängigkeiten sind zu erkennen und grundsätzlich zu vermeiden.

## 15. Fähigkeiten

Plugins deklarieren bereitgestellte Fähigkeiten statt impliziter Annahmen.

Beispiele:

- `domain.mcb.provider`;
- `simulation.electrical`;
- `export.pdf`;
- `integration.github`;
- `cockpit.view.security`.

Konkrete Namenskonventionen werden später festgelegt.

## 16. Lebenszyklus

Ein Plugin besitzt mindestens folgende konzeptionelle Zustände:

- entdeckt;
- geprüft;
- installiert;
- aktiviert;
- eingeschränkt;
- deaktiviert;
- inkompatibel;
- fehlerhaft;
- stillgelegt;
- entfernt.

Installation und Aktivierung sind getrennte Vorgänge.

## 17. Installation

Installation bedeutet, dass Pluginartefakte und Metadaten verfügbar gemacht werden.

Installation allein darf noch keine produktive Fachwirkung erzeugen.

Vor Aktivierung können erforderlich sein:

- Integritätsprüfung;
- Versionsprüfung;
- Abhängigkeitsprüfung;
- Berechtigungsprüfung;
- Konfigurationsvalidierung;
- Freigabe;
- Simulation der Auswirkungen.

## 18. Aktivierung

Ein Plugin wird erst nach erfolgreicher Validierung aktiviert.

Schlägt die Aktivierung fehl, muss der bisherige gültige Plattformzustand erhalten bleiben.

Eine teilweise aktivierte Plugininstallation darf nicht als vollständig erfolgreich gelten.

## 19. Deaktivierung

Plugins müssen kontrolliert deaktivierbar sein.

Dabei muss geklärt werden:

- welche laufenden Prozesse betroffen sind;
- welche registrierten Erweiterungspunkte entfernt werden;
- wie persistierte Pluginobjekte weiter referenzierbar bleiben;
- ob Read-Models oder Caches ungültig werden;
- welche Domänenfunktionen nicht mehr verfügbar sind.

Deaktivierung darf historische Daten nicht unkontrolliert zerstören.

## 20. Entfernung

Entfernung von Pluginartefakten ist von Stilllegung ihrer fachlichen Daten zu unterscheiden.

Objekte oder historische Referenzen eines entfernten Plugins müssen, soweit erforderlich, weiterhin erkennbar und nachvollziehbar bleiben.

Die Plattform darf unbekannte Pluginobjekte nicht stillschweigend als andere Objekte interpretieren.

## 21. Daten- und Objektbesitz

Ein Plugin muss erklären können, welche Daten und Objekttypen es besitzt.

Bei Deaktivierung oder Entfernung muss nachvollziehbar bleiben:

- wer Eigentümer der Daten ist;
- welche Daten ohne Plugin noch lesbar sind;
- welche Daten nur als opake Referenzen erhalten bleiben;
- welche Migration erforderlich ist.

## 22. Migration

Pluginupdates können Daten- oder Schemamigrationen erfordern.

Migrationen müssen:

- versioniert;
- validierbar;
- wiederholbar bzw. idempotent soweit möglich;
- auditierbar;
- fehlertransparent

sein.

Eine fehlgeschlagene Migration darf nicht als erfolgreiches Update gelten.

## 23. Offline-First

Plugins müssen ihren Offline-Betriebsmodus deklarieren können.

Mögliche Kategorien sind:

- vollständig offline-fähig;
- offline mit eingeschränktem Funktionsumfang;
- online erforderlich;
- offline nur lesend;
- offline mit späterer Synchronisation.

Ein nicht erreichbarer externer Dienst darf nicht automatisch als lokale Datenlöschung oder Pluginfehler interpretiert werden.

## 24. Bus

Plugins dürfen Nachrichten über den kanonischen Bus senden und empfangen.

Sie dürfen keine parallele nicht nachvollziehbare Kommunikationsschicht für fachlich relevante Vorgänge einführen.

Nachrichten müssen dieselben Regeln für Korrelation, Versionierung, Audit und Fehlerbehandlung erfüllen wie Plattformnachrichten.

## 25. Audit

Mindestens folgende Pluginvorgänge müssen auditierbar sein, soweit relevant:

- Plugin installiert;
- Plugin aktiviert;
- Plugin deaktiviert;
- Plugin aktualisiert;
- Plugin entfernt;
- Berechtigungsumfang geändert;
- Konfiguration geändert;
- Migration ausgeführt;
- kritischer Pluginfehler;
- sicherheitsrelevante Pluginaktion;
- Pluginintegrität oder Herkunft neu bewertet.

## 26. Herkunft und Integrität

Die Plattform muss Pluginherkunft und Integritätsinformationen nachvollziehbar halten können.

Dazu können gehören:

- Hersteller;
- Quelle;
- Paketkennung;
- Prüfsumme;
- Signaturstatus;
- Vertrauens- oder Freigabestatus;
- Installationsquelle.

Die konkrete kryptografische Umsetzung wird später festgelegt.

## 27. Vertrauensstatus

Ein Plugin kann einen technischen Vertrauensstatus besitzen.

Dieser ist strikt von der Benutzergewichtung aus `USER_WEIGHT_MODEL.md` getrennt.

Ein technisch vertrauenswürdiges Plugin besitzt dennoch nur die explizit erlaubten Rechte.

## 28. Fehlerisolierung

Ein fehlerhaftes Plugin soll die übrige Plattform nicht unnötig beeinträchtigen.

Die Architektur muss Zustände wie `eingeschränkt`, `fehlerhaft` oder `deaktiviert` ausdrücken können.

Fehler müssen sichtbar und nachvollziehbar sein; stillschweigendes Weiterarbeiten mit unvollständiger Fachwirkung ist zu vermeiden.

## 29. Z_Cockpit

Z_Cockpit soll Plugins transparent darstellen und autorisierte Verwaltungsaktionen auslösen können.

Mindestens vorgesehen sind:

- Plugin-ID, Name und Version;
- Hersteller und Herkunft;
- Status;
- Fähigkeiten;
- Abhängigkeiten;
- Kompatibilität;
- Berechtigungsanforderungen;
- Konfigurationsstatus;
- Offline-Fähigkeit;
- Auditbezüge;
- Fehler und Warnungen;
- verfügbare Updates, sofern bekannt.

Z_Cockpit ist nicht die Source of Truth des Pluginzustands.

## 30. Plugin-Simulation

Vor Installation, Aktivierung oder Update soll eine Auswirkungsanalyse möglich sein.

Simulierbar sind insbesondere:

- neue benötigte Berechtigungen;
- geänderte Pluginfähigkeiten;
- Konfigurationsänderungen;
- Schemaänderungen;
- abhängige Plugins;
- betroffene Domänen;
- betroffene Projekte;
- Offline-Auswirkungen;
- Migrationsbedarf;
- Konflikte mit installierten Erweiterungen.

Eine Simulation aktiviert oder verändert kein Plugin produktiv.

## 31. Rechtesimulation

Ändert ein Plugin Rollen-, Berechtigungs-, Richtlinien- oder Organisationsanforderungen, müssen diese Auswirkungen in der Z_Cockpit-Rechtesimulation sichtbar gemacht werden können.

Ein Plugin darf keine verborgenen Autorisierungswirkungen besitzen, die außerhalb des kanonischen Autorisierungsmodells liegen.

## 32. Tests

Plugins müssen abhängig von ihrer Art testbar sein.

Mindestens vorgesehen sind:

- Manifestvalidierung;
- Kompatibilitätstest;
- Konfigurationsvalidierung;
- Berechtigungstest;
- Aktivierungs-/Deaktivierungstest;
- Fehlertest;
- Offline-Test, sofern unterstützt;
- Migrationsprüfung;
- Erweiterungspunktvertrag;
- keine Umgehung von Autorisierung und Audit.

Domänenplugins benötigen zusätzlich fachliche Domänentests.

## 33. Suche

Installierte oder verfügbare Plugininformationen sollen innerhalb ihrer Sichtbarkeitsgrenzen auffindbar sein.

Suchkriterien können sein:

- Plugin-ID;
- Name;
- Hersteller;
- Capability;
- Version;
- Status;
- Domäne;
- Abhängigkeit;
- Kompatibilitätsstatus.

## 34. Projektgedächtnis

Relevante Pluginentscheidungen, Migrationen, Inkompatibilitäten und Erkenntnisse können im Projektgedächtnis referenziert werden.

Das Pluginmodell selbst ist jedoch nicht das Projektgedächtnis.

## 35. Invarianten

1. Plugins erweitern ProjectOS nur über definierte Verträge.
2. Plugins verändern Core nicht.
3. Plugins umgehen Domain Ownership nicht.
4. Plugins umgehen Autorisierung nicht.
5. Plugins umgehen Audit nicht.
6. Plugins führen keine konkurrierende Identitäts- oder Berechtigungswahrheit ein.
7. Pluginkonfiguration verwendet das kanonische Konfigurationsmodell.
8. Geheimnisse sind keine normalen Pluginwerte.
9. Installation und Aktivierung sind getrennt.
10. Fehlgeschlagene Aktivierung verändert nicht den gültigen Plattformzustand.
11. Deaktivierung oder Entfernung zerstört historische Referenzen nicht unkontrolliert.
12. Abhängigkeiten und Versionen sind explizit.
13. Z_Cockpit ist nicht die Source of Truth.
14. Simulation besitzt keine produktive Wirkung.
15. Benutzergewichtung und Pluginvertrauen sind getrennte Konzepte.

## 36. Abgrenzung

Dieses Dokument definiert ausdrücklich nicht:

- konkretes Paketformat;
- konkrete Programmierschnittstelle;
- konkrete Plugin-Sprache;
- Prozess- oder Sandboxtechnik;
- konkrete Signaturalgorithmen;
- Plugin-Marktplatz;
- konkrete Update-Infrastruktur;
- konkrete GUI-Layouts;
- konkrete Netzwerkprotokolle.

## 37. Folgemodelle

Auf diesem Modell bauen insbesondere auf:

- Pluginservice und Pluginregistry;
- Capability-Registry;
- spätere Sicherheits- und Isolationmodelle;
- Z_Cockpit-Pluginverwaltung;
- Plugin-Auswirkungsanalyse;
- Domänenplugin-Verträge.

## 38. Abhängigkeiten

Dieses Dokument basiert insbesondere auf:

- `PLATFORM_MODEL.md`;
- `CONFIGURATION_MODEL.md`;
- `AUTHORIZATION_MODEL.md`;
- `AUDIT_MODEL.md`;
- `BUS_MODEL.md`;
- `MEMORY_MODEL.md`;
- `USER_WEIGHT_MODEL.md`;
- `SCHEMA_MODEL.md`;
- `RELATION_MODEL.md`;
- `Z_COCKPIT_IDENTITY_INTEGRATION.md`;
- `Z_COCKPIT_AUTHORIZATION_SIMULATION.md`.

## 39. Ergebnis

ProjectOS besitzt ein eigenständiges Pluginmodell für kontrollierte Erweiterbarkeit. Plugins können neue Fähigkeiten, Domänen und Integrationen bereitstellen, ohne Core-, Plattform-, Domain-Ownership-, Autorisierungs- oder Auditgrenzen zu umgehen. Installation, Aktivierung, Abhängigkeiten, Versionierung, Konfiguration, Migration, Offline-Betrieb, Z_Cockpit und Simulation sind ausdrücklich berücksichtigt.