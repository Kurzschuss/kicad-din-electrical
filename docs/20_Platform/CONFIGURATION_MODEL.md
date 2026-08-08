# Konfigurationsmodell

**Dokument-ID:** PLT-0019  
**Titel:** Fachliches Modell für versionierbare und validierbare Konfiguration  
**Version:** 0.1.0  
**Status:** Entwurf  
**Stabilitätsklasse:** B  
**Autoritätsebene:** Plattformmodell  
**Erstellt:** 8. August 2026  
**Zuletzt geändert:** 8. August 2026

---

## 1. Zweck

Dieses Dokument definiert Konfiguration als eigenständiges Plattformkonzept von ProjectOS.

Konfiguration beschreibt kontrollierbare, referenzierbare, validierbare und soweit erforderlich versionierbare Zustände, die Verhalten oder Betriebsweise von Plattform, Projekt, Workspace, Organisation, Domäne, Plugin oder Dienst beeinflussen.

Konfiguration ist keine lose Sammlung beliebiger Einstellungen und keine versteckte Programmlogik.

## 2. Grundsatz

Für ProjectOS gilt:

> Konfiguration vor Code, soweit fachliche oder betriebliche Variabilität ohne Änderung des Programmkerns ausgedrückt werden kann.

Daraus folgt:

- konfigurierbare Unterschiede werden nicht unnötig hart codiert;
- Konfiguration besitzt ein Schema;
- Konfiguration besitzt einen Gültigkeitsbereich;
- Konfiguration ist validierbar;
- relevante Änderungen sind nachvollziehbar;
- sicherheitsrelevante Konfiguration ist autorisiert und auditierbar;
- Geheimnisse werden nicht als gewöhnliche Konfigurationswerte behandelt.

## 3. Architekturstellung

Das Konfigurationsmodell gehört zur Plattformebene.

Es baut insbesondere auf `PLATFORM_MODEL.md`, `PROJECT_MODEL.md`, `WORKSPACE_MODEL.md`, `ORGANIZATION_MODEL.md`, `AUTHORIZATION_MODEL.md`, `AUDIT_MODEL.md`, `MEMORY_MODEL.md`, `BUS_MODEL.md`, `SCHEMA_MODEL.md` und `RELATION_MODEL.md` auf.

Domänen und Plugins dürfen eigene Konfigurationsschemata bereitstellen, aber keine parallele inkompatible Konfigurationswahrheit einführen.

## 4. Konfigurationsobjekt

Ein Konfigurationsobjekt beschreibt mindestens:

- stabile Konfigurations-ID;
- Konfigurationstyp;
- Schemareferenz und Schemaversion;
- Version des Konfigurationsstands;
- Gültigkeitsbereich;
- Ziel oder Bezug;
- Lebenszyklusstatus;
- Werte bzw. referenzierte Werte;
- Herkunft;
- verantwortliche Instanz;
- Beginn und optionales Ende der Gültigkeit;
- Historien- und Auditbezüge;
- optionale Abhängigkeiten zu anderen Konfigurationsobjekten.

## 5. Gültigkeitsbereiche

Konfiguration kann insbesondere gelten für:

- Plattform;
- Organisation;
- Organisationseinheit;
- Projekt;
- Workspace;
- Benutzerpräferenz;
- Domäne;
- Objektklasse;
- einzelnes Objekt;
- Plugin;
- Dienst;
- Simulation;
- Sitzung, sofern ausdrücklich zulässig.

Der Gültigkeitsbereich muss explizit sein.

## 6. Konfiguration und Benutzerpräferenz

Persönliche Präferenzen und fachlich wirksame Konfiguration sind zu unterscheiden.

Beispiele persönlicher Präferenzen:

- Darstellung;
- Sortierung;
- zuletzt verwendete Ansichten;
- nicht-fachliche UI-Einstellungen.

Beispiele fachlich wirksamer Konfiguration:

- Validierungsregeln;
- aktivierte Domänen;
- Simulationsparameter;
- Freigaberichtlinien;
- Plugin-Aktivierung;
- technische Betriebsparameter mit fachlicher Wirkung.

Eine persönliche Präferenz darf fachliche Projektwahrheit nicht stillschweigend verändern.

## 7. Schema

Jede strukturierte Konfiguration benötigt ein bekanntes Schema.

Das Schema definiert mindestens:

- zulässige Felder;
- Datentypen;
- Pflichtwerte;
- Wertebereiche;
- Referenztypen;
- Standardwerte, soweit zulässig;
- Validierungsregeln;
- Kompatibilitätsregeln;
- Migrationsregeln, soweit erforderlich.

Unbekannte oder inkompatible Schemata dürfen nicht stillschweigend interpretiert werden.

## 8. Standardwerte

Standardwerte müssen explizit und reproduzierbar sein.

Es muss unterscheidbar bleiben zwischen:

- Wert ausdrücklich gesetzt;
- Wert aus Standard übernommen;
- Wert geerbt;
- Wert nicht gesetzt;
- Wert nicht verfügbar.

Ein impliziter technischer Default darf nicht unbemerkt zur fachlichen Wahrheit werden.

## 9. Vererbung

Konfiguration kann kontrollierte Vererbung unterstützen.

Beispiel:

```text
Plattformstandard
      ↓
Organisationskonfiguration
      ↓
Projektkonfiguration
      ↓
Domänenkonfiguration
```

Vererbung muss durch den jeweiligen Konfigurationstyp ausdrücklich erlaubt sein.

Die effektive Konfiguration muss auf ihre Quellen zurückführbar sein.

## 10. Überschreibung

Eine engere Konfiguration kann einen geerbten Wert nur dann überschreiben, wenn das Schema und die Richtlinie dies erlauben.

Für jeden effektiven Wert muss nachvollziehbar sein:

- welche Quelle ihn definiert;
- ob er geerbt oder überschrieben wurde;
- welche Regel die Überschreibung erlaubt;
- welche Version maßgeblich ist.

## 11. Effektive Konfiguration

Die effektive Konfiguration ist die aus allen zulässigen Quellen für einen konkreten Kontext resultierende Konfiguration.

Sie ist ein abgeleitetes Ergebnis und darf nicht mit einem einzelnen Konfigurationsobjekt gleichgesetzt werden.

Ein Read-Model oder Cache darf effektive Konfiguration vorberechnen, ist aber nicht die Source of Truth.

## 12. Versionierung

Relevante Konfigurationsstände müssen versionierbar sein.

Eine Änderung erzeugt einen neuen nachvollziehbaren Stand, wenn die Änderung fachliche, sicherheitsrelevante oder reproduzierbarkeitsrelevante Wirkung besitzt.

Historische Simulationen, Tests oder Releases sollen auf den damals verwendeten Konfigurationsstand referenzieren können.

## 13. Aktivierung

Konfiguration kann zwischen definiertem und aktiv wirksamem Zustand unterscheiden.

Konzeptionelle Zustände können sein:

- Entwurf;
- validiert;
- zur Freigabe vorgesehen;
- freigegeben;
- aktiv;
- pausiert;
- ersetzt;
- widerrufen;
- archiviert.

Nicht jeder Konfigurationstyp benötigt alle Zustände.

## 14. Validierung

Vor Aktivierung muss Konfiguration gegen das maßgebliche Schema und relevante Querschnittsregeln validiert werden.

Dabei können geprüft werden:

- Struktur;
- Wertebereiche;
- Referenzauflösung;
- Abhängigkeiten;
- Kompatibilität;
- Sicherheitsregeln;
- Domänenregeln;
- Offline-Zulässigkeit;
- Plugin-Verfügbarkeit.

Ein Validierungsfehler darf nicht stillschweigend zu einer Teilaktivierung führen.

## 15. Atomare Aktivierung

Mehrteilige Konfigurationsänderungen müssen atomar aktivierbar sein, wenn nur der vollständige Satz fachlich gültig ist.

Schlägt die Aktivierung fehl, bleibt der bisher gültige Konfigurationsstand maßgeblich.

Ein fehlgeschlagener Aktivierungsversuch darf nicht als erfolgreiche Konfigurationsänderung auditiert oder im Z_Cockpit als aktiv dargestellt werden.

## 16. Konfigurationssatz

Mehrere zusammengehörige Konfigurationsobjekte können zu einem Konfigurationssatz zusammengefasst werden.

Ein Konfigurationssatz kann beispielsweise enthalten:

- Projektgrundkonfiguration;
- Domänenaktivierungen;
- Plugin-Konfiguration;
- Simulationskonfiguration;
- Freigaberichtlinien.

Ein Satz muss als konsistente Einheit validierbar und referenzierbar sein.

## 17. Projektkonfiguration

Projektkonfiguration beeinflusst den fachlichen Projektbetrieb, ist aber nicht Teil der stabilen Projektidentität.

Ein Projekt kann auf einen oder mehrere Konfigurationsstände referenzieren.

Ein Wechsel der Projektkonfiguration verändert nicht die Projekt-ID.

## 18. Workspace-Konfiguration

Workspace-Konfiguration beschreibt arbeitskontextbezogene Einstellungen.

Sie darf projektfachliche Konfiguration nicht unkontrolliert überschreiben.

Lokale Workspace-Einstellungen müssen klar von projektweit gültigen Konfigurationsständen unterscheidbar sein.

## 19. Organisationskonfiguration

Organisationen können als Gültigkeitsbereich für Konfiguration und Richtlinien dienen.

Beispiele sind:

- Sicherheitsanforderungen;
- zulässige Plugins;
- Standard-Reviewverfahren;
- Authentifizierungsanforderungen;
- Offline-Regeln.

Die Autorisierung entscheidet, wer solche Konfiguration ändern darf.

## 20. Domänenkonfiguration

Domänen dürfen eigene Konfigurationstypen definieren.

Domänenkonfiguration bleibt Eigentum der jeweiligen Domäne und darf nicht im allgemeinen Plattformmodell hart codiert werden.

Die Plattform stellt Identität, Schema, Versionierung, Validierung, Speicherung, Audit und Auflösung bereit.

## 21. Plugin-Konfiguration

Plugins dürfen eigene Konfigurationsschemata bereitstellen.

Ein Plugin darf Konfigurationswerte nur innerhalb dokumentierter Verträge auswerten.

Plugin-Deaktivierung oder fehlende Plugin-Versionen müssen erkennbar machen, welche Konfiguration dadurch nicht mehr auswertbar ist.

## 22. Sicherheitsrelevante Konfiguration

Sicherheitsrelevante Konfiguration erfordert besondere Schutzmaßnahmen.

Dazu können gehören:

- Autorisierungsrichtlinien;
- Authentifizierungsanforderungen;
- Delegationsgrenzen;
- Auditregeln;
- Notfallverfahren;
- Plugin-Freigaben;
- externe Integrationen.

Änderungen müssen autorisiert, validiert und auditierbar sein und können Vier-Augen-Freigabe verlangen.

## 23. Geheimnisse

Geheimnisse sind von normaler Konfiguration zu trennen.

Beispiele:

- Kennwörter;
- API-Schlüssel;
- private Schlüssel;
- Tokens;
- Recovery-Geheimnisse.

Ein Konfigurationsobjekt darf höchstens eine sichere Referenz auf ein Geheimnis enthalten, nicht das Geheimnis ungeschützt als normalen Wert.

Z_Cockpit, Audit, Exporte und Logs dürfen Geheimnisse nicht offenlegen.

## 24. Offline-First

Für den vorgesehenen Offline-Betrieb müssen erforderliche Konfigurationsstände lokal verfügbar sein.

Erkennbar sein müssen:

- Konfigurationsversion;
- Schemaversion;
- Zeitpunkt der letzten Bestätigung;
- externe Abhängigkeiten;
- möglicherweise veraltete Werte;
- nicht verfügbare Referenzen.

Kritische Konfigurationsänderungen können online bestätigt werden müssen.

## 25. Synchronisation

Konfigurationssynchronisation muss Konflikte sichtbar behandeln.

Insbesondere dürfen konkurrierende Änderungen nicht nach dem Prinzip „letzter Schreibvorgang gewinnt“ stillschweigend fachliche Konfiguration überschreiben, wenn dadurch Informationen oder Freigaben verloren gehen.

Konflikte müssen validierbar, auflösbar und auditierbar sein.

## 26. Simulation

Konfigurationsänderungen sollen vor Aktivierung simuliert werden können, wenn sie relevante fachliche oder sicherheitsbezogene Auswirkungen besitzen.

Beispiele:

- Welche Validierungsregeln ändern sich?
- Welche Projekte oder Domänen sind betroffen?
- Welche Plugins werden aktiv oder inaktiv?
- Welche Benutzer verlieren oder erhalten durch Richtlinienänderung effektive Rechte?
- Welche Simulationsergebnisse ändern sich?
- Welche Offline-Funktionen werden eingeschränkt?

Eine Simulation verändert keine produktive Konfiguration.

## 27. Rechtesimulation

Wenn Konfiguration Autorisierungsrichtlinien beeinflusst, muss ihre hypothetische Änderung in der Z_Cockpit-Rechtesimulation berücksichtigt werden können.

Dabei bleibt die Konfigurationssimulation von der realen Autorisierungsentscheidung getrennt.

Ein simuliertes `ALLOW` besitzt keine produktive Wirkung.

## 28. Projektgedächtnis

Wesentliche Konfigurationsentscheidungen können im Projektgedächtnis mit ihrer Begründung verknüpft werden.

Beispielsweise soll nachvollziehbar sein können:

- warum ein bestimmter Standard geändert wurde;
- welche Anforderung die Änderung ausgelöst hat;
- welche Tests sie abgesichert haben;
- ab welchem Release sie galt.

Das Projektgedächtnis ersetzt nicht die eigentliche Konfiguration.

## 29. Bus

Konfigurationsänderungen können über den Bus Befehle und Ereignisse erzeugen.

Beispiele:

- `ConfigurationValidateRequested`;
- `ConfigurationActivationRequested`;
- `ConfigurationActivated`;
- `ConfigurationActivationFailed`;
- `ConfigurationSuperseded`.

Der Bus transportiert den Vorgang, ist aber nicht die Konfigurationsquelle der Wahrheit.

## 30. Audit

Mindestens folgende Vorgänge müssen auditierbar sein, soweit relevant:

- Konfiguration angelegt;
- Konfiguration geändert;
- Validierung durchgeführt;
- Freigabe erteilt oder abgelehnt;
- Konfiguration aktiviert;
- Aktivierung fehlgeschlagen;
- Konfiguration ersetzt oder widerrufen;
- Gültigkeitsbereich geändert;
- Vererbungs- oder Überschreibungsregel geändert;
- sicherheitsrelevante Konfiguration geändert;
- Geheimnisreferenz geändert.

Audit speichert keine Geheimnisse.

## 31. Z_Cockpit

Z_Cockpit soll Konfiguration transparent darstellen und autorisierte Änderungen auslösen können.

Mindestens sichtbar sein sollen:

- Konfigurations-ID;
- Typ;
- Version;
- Schemaversion;
- Status;
- Gültigkeitsbereich;
- Herkunft effektiver Werte;
- geerbte und überschriebene Werte;
- Validierungsstatus;
- Freigabestatus;
- Abhängigkeiten;
- Offline-/Synchronisationsstatus;
- Auditbezüge;
- Auswirkungen geplanter Änderungen.

Z_Cockpit ist nicht die Source of Truth.

## 32. Read-Model

Für UI, Reporting und Analyse dürfen nicht-autoritative Konfigurations-Read-Models verwendet werden.

Sie können insbesondere vorberechnen:

- effektive Werte;
- Vererbungsketten;
- Überschreibungen;
- Konflikte;
- ablaufende Konfiguration;
- inkompatible Schemata;
- betroffene Projekte oder Plugins.

Produktive Dienste müssen den autoritativen Konfigurationsstand verwenden.

## 33. Suche

Konfiguration soll innerhalb zulässiger Sichtbarkeitsgrenzen suchbar sein nach:

- Konfigurations-ID;
- Typ;
- Projekt;
- Organisation;
- Domäne;
- Plugin;
- Status;
- Schemaversion;
- Version;
- Gültigkeitsbereich;
- verantwortlicher Instanz.

Geheimniswerte sind nicht durch normale Suche offenzulegen.

## 34. Validierungsinvarianten

Eine Konfiguration ist mindestens darauf zu prüfen, dass:

1. Konfigurations-ID eindeutig ist;
2. Konfigurationstyp bekannt ist;
3. Schema und Schemaversion bekannt sind;
4. Gültigkeitsbereich zulässig ist;
5. Referenzen auflösbar oder ausdrücklich als nicht verfügbar markiert sind;
6. Werte das Schema erfüllen;
7. Vererbung und Überschreibung zulässig sind;
8. zeitliche Gültigkeit konsistent ist;
9. sicherheitsrelevante Änderungen autorisiert und auditierbar sind;
10. Geheimnisse nicht als ungeschützte normale Werte gespeichert werden.

## 35. Invarianten

1. Konfiguration und Code sind getrennt.
2. Konfiguration und Benutzerpräferenz sind unterscheidbar.
3. Konfiguration besitzt ein bekanntes Schema.
4. Fachlich relevante Konfiguration ist versionierbar.
5. Effektive Konfiguration ist auf ihre Quellen zurückführbar.
6. Vererbung ist nur zulässig, wenn sie ausdrücklich definiert ist.
7. Fehlgeschlagene Aktivierung verändert den vorher gültigen Stand nicht.
8. Geheimnisse sind keine normalen Konfigurationswerte.
9. Z_Cockpit ist nicht die Source of Truth.
10. Read-Models sind nicht autoritativ.
11. Simulation verändert keine produktive Konfiguration.
12. Autorisierungsrelevante Konfiguration umgeht nicht die Autorisierungsplattform.
13. Offline-Stände sind als solche nachvollziehbar.
14. Synchronisationskonflikte werden nicht stillschweigend überschrieben.
15. Historische Ergebnisse können auf den damals verwendeten Konfigurationsstand referenzieren.

## 36. Abgrenzung

Dieses Dokument definiert ausdrücklich nicht:

- konkrete Dateiformate wie YAML, JSON oder TOML;
- konkrete Datenbanktabellen;
- konkrete Secret-Store-Technologien;
- technische Synchronisationsprotokolle;
- vollständige Richtlinienmodelle;
- konkrete Plugin-Implementierung;
- konkrete GUI-Layouts;
- konkrete Defaultwerte einzelner Domänen.

## 37. Folgemodelle

Auf diesem Modell bauen insbesondere auf:

- `PLUGIN_MODEL.md`;
- `SEARCH_MODEL.md`;
- spätere Konfigurationsdienste;
- Richtlinienmodelle;
- Domänenkonfigurationen;
- Z_Cockpit-Konfigurationsansichten und Simulationen.

## 38. Abhängigkeiten

Dieses Dokument basiert insbesondere auf:

- `PLATFORM_MODEL.md`;
- `PROJECT_MODEL.md`;
- `WORKSPACE_MODEL.md`;
- `ORGANIZATION_MODEL.md`;
- `AUTHORIZATION_MODEL.md`;
- `AUDIT_MODEL.md`;
- `MEMORY_MODEL.md`;
- `BUS_MODEL.md`;
- `SCHEMA_MODEL.md`;
- `RELATION_MODEL.md`;
- `Z_COCKPIT_IDENTITY_INTEGRATION.md`;
- `Z_COCKPIT_AUTHORIZATION_SIMULATION.md`.

## 39. Ergebnis

ProjectOS besitzt ein eigenständiges Konfigurationsmodell für strukturierte, schema-basierte, versionierbare und nachvollziehbare Konfiguration. Vererbung, Überschreibung, Aktivierung, Offline-Betrieb, Synchronisation, Simulation, Audit, Geheimnisreferenzen und Z_Cockpit-Transparenz sind berücksichtigt, ohne Konfiguration mit Code, Benutzerpräferenzen oder Autorisierung zu vermischen.