# Busmodell

**Dokument-ID:** PLT-0018  
**Titel:** Fachliches Modell für Plattformkommunikation, Ereignisse und Befehle  
**Version:** 0.1.0  
**Status:** Entwurf  
**Stabilitätsklasse:** B  
**Autoritätsebene:** Plattformmodell  
**Erstellt:** 8. August 2026  
**Zuletzt geändert:** 8. August 2026

---

## 1. Zweck

Dieses Dokument definiert den fachlichen Kommunikationsbus von ProjectOS.

Der Bus ermöglicht lose gekoppelte Kommunikation zwischen Plattformdiensten, Objekten und späteren Domänen, ohne die Architektur an eine konkrete technische Transportlösung zu binden.

Der Bus beschreibt fachliche Nachrichten, deren Bedeutung, Korrelation, Zustellungserwartung und Grenzen.

## 2. Grundsatz

Der ProjectOS-Bus ist kein Synonym für MQTT, Kafka, RabbitMQ, WebSocket, HTTP oder einen bestimmten EventStore.

Diese Technologien können später technische Implementierungsoptionen sein.

Das fachliche Modell bleibt unabhängig davon.

## 3. Architekturstellung

Das Busmodell gehört zur Plattformebene.

Es baut insbesondere auf `PLATFORM_MODEL.md`, `OBJECT_MODEL.md`, `RELATION_MODEL.md`, `AUDIT_MODEL.md`, `MEMORY_MODEL.md`, `AUTHORIZATION_MODEL.md` und späteren Domänenmodellen auf.

Core kennt keine konkrete Plattformkommunikation.

Domänen dürfen den Bus verwenden, aber keine parallelen inkompatiblen Kommunikationsmodelle einführen.

## 4. Nachrichtentypen

ProjectOS unterscheidet mindestens:

- Befehl;
- Ereignis;
- Anfrage;
- Antwort;
- Benachrichtigung;
- Fehlernachricht;
- Sicherheitsereignis;
- Systemzustandsmeldung.

Die Typen besitzen unterschiedliche Semantik und dürfen nicht beliebig vertauscht werden.

## 5. Befehl

Ein Befehl fordert eine konkrete Handlung an.

Beispiele:

- Projekt speichern;
- Rolle zuweisen;
- Delegation widerrufen;
- Simulation starten;
- Konfiguration aktivieren.

Ein Befehl beschreibt mindestens:

- Befehls-ID;
- Befehlstyp;
- auslösende Akteursidentität oder technische Quelle;
- Ziel oder Empfänger;
- fachlichen Kontext;
- Korrelations-ID;
- Zeitpunkt;
- optionalen Gültigkeits- oder Ablaufzeitraum;
- erforderliche Autorisierungsreferenzen oder Kontextinformationen.

Ein Befehl darf nicht als bereits eingetretenes Ereignis behandelt werden.

## 6. Ereignis

Ein Ereignis beschreibt eine fachlich eingetretene Tatsache.

Beispiele:

- Projekt gespeichert;
- Rolle zugewiesen;
- Benutzer gesperrt;
- Delegation abgelaufen;
- Simulation abgeschlossen;
- Audit-Eintrag erzeugt.

Ein Ereignis wird nicht verwendet, um eine gewünschte Handlung zu formulieren.

## 7. Anfrage und Antwort

Eine Anfrage verlangt Informationen oder eine fachliche Auswertung.

Beispiele:

- effektive Berechtigungen eines Benutzers ermitteln;
- Projektstatus abfragen;
- Gewichtungsstand ermitteln;
- Wissensbeziehungen suchen.

Eine Antwort referenziert die zugehörige Anfrage über Korrelation.

Anfrage/Antwort darf intern auch asynchron umgesetzt werden.

## 8. Benachrichtigung

Eine Benachrichtigung informiert über einen Sachverhalt, ohne selbst zwingend fachliche Autorität zu besitzen.

Beispiele:

- Hinweis auf ablaufende Delegation;
- Hinweis auf veraltete Offline-Daten;
- Hinweis auf ausstehende Freigabe.

Benachrichtigungen dürfen keine fachlichen Zustände ersetzen.

## 9. Sicherheitsereignis

Sicherheitsrelevante Ereignisse verwenden ein kanonisches Sicherheitsereignismodell.

Authentifizierung, Sitzung, Autorisierung und Audit dürfen keine getrennten konkurrierenden Security-Event-Strukturen erzeugen.

Das Busmodell transportiert solche Ereignisse, definiert aber nicht deren vollständige Sicherheitssemantik.

## 10. Nachrichtenidentität

Jede persistierte oder nachweisrelevante Nachricht besitzt eine eindeutige Nachrichten-ID.

Diese dient insbesondere zur:

- Korrelation;
- Deduplizierung;
- Auditierbarkeit;
- Fehleranalyse;
- Nachverfolgung verteilter Vorgänge.

Nachrichten-IDs dürfen nicht wiederverwendet werden.

## 11. Korrelation

Zusammengehörige Nachrichten verwenden eine Korrelations-ID.

Beispiel:

```text
Befehl
  ↓
Autorisierungsanfrage
  ↓
Autorisierungsergebnis
  ↓
Fachliche Änderung
  ↓
Ereignis
  ↓
Audit
```

Alle Teile desselben fachlichen Vorgangs können über eine gemeinsame Korrelations-ID nachvollziehbar verbunden werden.

## 12. Kausalität

Neben Korrelation muss bei Bedarf Kausalität erkennbar sein.

Eine Nachricht kann deshalb auf eine verursachende Nachricht referenzieren.

Damit kann unterschieden werden zwischen:

- gehört zum selben Vorgang;
- wurde unmittelbar durch diese Nachricht ausgelöst.

## 13. Zustellsemantik

Das fachliche Modell darf keine unrealistische Garantie wie „genau einmal in allen Situationen“ voraussetzen.

Es muss mit möglichen technischen Zuständen umgehen können wie:

- Nachricht mehrfach zugestellt;
- Nachricht verspätet;
- Nachricht vorübergehend nicht zustellbar;
- Nachricht lokal gepuffert;
- Nachricht nach Wiederverbindung synchronisiert.

Verbraucher müssen dort, wo erforderlich, idempotent oder deduplizierbar entworfen werden.

## 14. Reihenfolge

Eine globale Reihenfolge aller Nachrichten wird nicht vorausgesetzt.

Wenn Reihenfolge fachlich relevant ist, muss sie innerhalb eines definierten Gültigkeitsbereichs explizit abgesichert werden.

Beispiele:

- Version eines Objekts;
- Ereignisse eines Aggregats;
- Delegationslebenszyklus;
- Projektrevision.

## 15. Idempotenz

Befehle und Nachrichten, die mehrfach verarbeitet werden können, müssen eine definierte Idempotenzstrategie unterstützen.

Eine doppelte Zustellung darf nicht unkontrolliert zu doppelten fachlichen Wirkungen führen.

Beispiel:

Eine bereits widerrufene Delegation darf durch erneute Zustellung desselben Widerrufsbefehls nicht einen zweiten unabhängigen Widerruf erzeugen.

## 16. Fehler

Fehler sind explizite Ergebnisse und dürfen nicht durch stilles Verwerfen von Nachrichten verborgen werden.

Fehler können insbesondere klassifiziert werden als:

- Validierungsfehler;
- Autorisierungsfehler;
- Ziel nicht vorhanden;
- Versionskonflikt;
- Abhängigkeit nicht verfügbar;
- technische Zustellung fehlgeschlagen;
- Verarbeitung fehlgeschlagen;
- Zeitüberschreitung;
- unauflösbarer Kontext.

## 17. Retry

Ein technischer Retry ist von einer fachlichen Wiederholung zu unterscheiden.

Nicht jeder fehlgeschlagene Befehl darf automatisch erneut ausgeführt werden.

Retries müssen berücksichtigen:

- Idempotenz;
- Ablaufzeit;
- Autorisierungsstand;
- Versionsstand;
- externe Seiteneffekte;
- fachliche Gültigkeit.

## 18. Dead-Letter- und Problemzustände

Nicht zustellbare oder dauerhaft fehlerhafte Nachrichten müssen sichtbar behandelt werden können.

Ein technischer Dead-Letter-Bereich ist nur eine mögliche Implementierung.

Fachlich erforderlich ist:

- Nachricht bleibt identifizierbar;
- Fehlergrund ist nachvollziehbar;
- erneute Verarbeitung ist kontrollierbar;
- Verwerfen ist auditierbar, wenn sicherheits- oder fachlich relevant.

## 19. Offline-First

Der Bus muss Offline-Betrieb unterstützen können.

Dazu gehören insbesondere:

- lokale Nachrichtenverarbeitung;
- lokale Pufferung;
- spätere Synchronisation;
- Erhalt ursprünglicher Zeit- und Akteursinformationen;
- sichtbarer Synchronisationsstatus;
- Konfliktbehandlung bei veraltetem Kontext.

Offline erzeugte Nachrichten dürfen beim Wiederverbinden nicht stillschweigend zu unkontrollierten Doppelwirkungen führen.

## 20. Autorisierung

Der Bus selbst ist keine Autorisierungsengine.

Schreibende oder sicherheitsrelevante Befehle müssen durch die zuständigen Plattformdienste vollständig autorisiert werden.

Eine Nachricht darf kein `ALLOW` allein deshalb erhalten, weil sie aus einem vermeintlich vertrauenswürdigen Kanal stammt.

Technische Herkunft ersetzt keine Akteursidentität und keine Berechtigungsprüfung.

## 21. Vertrauensgrenzen

Nachrichten können Vertrauensgrenzen überschreiten, beispielsweise:

- Prozessgrenze;
- Gerät;
- Workspace;
- Organisation;
- externe Integration;
- Plugin;
- Netzwerkgrenze.

An solchen Grenzen müssen Herkunft, Integrität und Autorisierung besonders geprüft werden.

## 22. Plugins

Plugins dürfen den Bus über dokumentierte Verträge verwenden.

Sie dürfen:

- definierte Ereignisse abonnieren;
- eigene dokumentierte Ereignistypen bereitstellen;
- Befehle über freigegebene Schnittstellen auslösen.

Sie dürfen nicht:

- Core- oder Plattforminvarianten umgehen;
- Sicherheitsprüfungen überspringen;
- fremde Ereignisse stillschweigend umdeuten;
- versteckte globale Seiteneffekte einführen.

## 23. Domänen

Domänen dürfen eigene fachliche Nachrichtentypen definieren.

Diese müssen:

- klar einer Domäne gehören;
- versioniert sein;
- ihren Gültigkeitsbereich kennen;
- mit Plattform- und Core-Grenzen vereinbar sein.

Domänenereignisse dürfen nicht ohne explizite Übersetzung als Plattformgrundereignisse ausgegeben werden.

## 24. Versionierung von Nachrichten

Nachrichtenschemata müssen versionierbar sein.

Änderungen müssen mindestens unterscheiden zwischen:

- rückwärtskompatibler Erweiterung;
- inkompatibler Änderung;
- veraltetem Nachrichtentyp;
- ersetztem Nachrichtentyp.

Empfänger müssen unbekannte oder nicht unterstützte Versionen sichtbar behandeln können.

## 25. Schema

Jeder stabile Nachrichtentyp besitzt ein definiertes Schema.

Das Schema beschreibt mindestens:

- Nachrichtentyp;
- Version;
- Pflichtfelder;
- optionale Felder;
- fachliche Bedeutung;
- Gültigkeitsbereich;
- Kompatibilitätsregeln.

## 26. Audit

Sicherheits-, freigabe- oder nachweisrelevante Nachrichten müssen mit dem kanonischen Auditmodell korrelierbar sein.

Nicht jede technische Nachricht muss als eigenständiger Audit-Eintrag gespeichert werden.

Audit und Bus erfüllen unterschiedliche Aufgaben:

- Bus transportiert Kommunikation;
- Audit dokumentiert nachweisrelevante Vorgänge.

## 27. Projektgedächtnis

Nachrichten sind nicht automatisch Projektwissen.

Ein wichtiges Ereignis kann jedoch zur Erzeugung oder Aktualisierung eines Wissenselements führen.

Beispiel:

```text
Test fehlgeschlagen
      ↓ Ereignis
Analyse durchgeführt
      ↓
Erkenntnis als Wissenselement
```

Der Bus ersetzt das Projektgedächtnis nicht.

## 28. Simulation

Simulationen dürfen denselben Busvertrag verwenden, müssen aber eindeutig als Simulation markiert werden.

Simulierte Ereignisse dürfen nicht als produktive Ereignisse verarbeitet werden.

Insbesondere gilt für Rechte- und Gewichtungssimulationen:

- eigener Simulationskontext;
- keine produktive Seiteneffektkette;
- keine produktiven Auditbehauptungen;
- klare Trennung in Z_Cockpit.

## 29. Z_Cockpit

Z_Cockpit darf Buszustände und relevante Vorgänge anzeigen, ist aber nicht der Bus selbst.

Darstellbar sind beispielsweise:

- laufende Vorgänge;
- Korrelationsketten;
- fehlgeschlagene Verarbeitungen;
- verzögerte Synchronisation;
- Nachrichtenfehler;
- relevante Sicherheitsereignisse;
- Simulationsvorgänge.

Z_Cockpit darf keine Nachrichten manipulieren, ohne über autorisierte Plattformbefehle zu gehen.

## 30. Beobachtbarkeit

Der Bus muss beobachtbar sein, ohne fachliche oder sicherheitsrelevante Daten unkontrolliert offenzulegen.

Mindestens sollen möglich sein:

- Zählung von Nachrichtentypen;
- Latenz;
- Fehlerquote;
- Retry-Zustände;
- Warteschlangen- oder Pufferzustände;
- Korrelation von Vorgängen.

Monitoringdaten sind nicht automatisch Auditdaten.

## 31. Datenschutz

Nachrichten dürfen nur die für ihren Zweck notwendigen Daten transportieren.

Es gilt Datenminimierung.

Geheimnisse, vollständige Tokens oder unnötige personenbezogene Inhalte dürfen nicht als gewöhnliche Busdaten verbreitet werden.

## 32. Invarianten

1. Der fachliche Bus ist unabhängig von einer konkreten Transporttechnologie.
2. Befehl und Ereignis sind getrennte Konzepte.
3. Ein Ereignis beschreibt eine eingetretene Tatsache.
4. Eine Benachrichtigung ersetzt keinen fachlichen Zustand.
5. Globale Reihenfolge wird nicht vorausgesetzt.
6. Mehrfachzustellung muss sicher behandelbar sein.
7. Der Bus autorisiert keine Handlung.
8. Technische Herkunft ersetzt keine Identitäts- oder Berechtigungsprüfung.
9. Offline-Synchronisation darf keine unkontrollierten Doppelwirkungen erzeugen.
10. Audit und Bus sind getrennte Verantwortlichkeiten.
11. Projektgedächtnis und Bus sind getrennt.
12. Simulationen dürfen keine produktiven Ereignisse erzeugen.
13. Z_Cockpit ist nicht die Source of Truth für Nachrichten oder Vorgänge.
14. Nachrichtenschemata sind versionierbar.
15. Fehler werden nicht stillschweigend verworfen.

## 33. Abgrenzung

Dieses Dokument definiert ausdrücklich nicht:

- MQTT-Topics;
- Kafka-Topics oder Partitionen;
- RabbitMQ-Queues;
- konkrete Broker;
- HTTP-Endpunkte;
- konkrete Serialisierungsformate;
- technische Retry-Algorithmen;
- konkrete Queue-Limits;
- konkrete Monitoringprodukte;
- konkrete Netzwerkprotokolle.

## 34. Folgemodelle

Auf diesem Modell bauen insbesondere auf:

- Event- und Command-Dienstverträge;
- `CONFIGURATION_MODEL.md`;
- `PLUGIN_MODEL.md`;
- `SEARCH_MODEL.md`;
- Sicherheitsereignismodelle;
- Z_Cockpit-Vorgangsansichten;
- spätere Domänenbusverträge.

## 35. Abhängigkeiten

Dieses Dokument basiert insbesondere auf:

- `PLATFORM_MODEL.md`;
- `PROJECT_MODEL.md`;
- `WORKSPACE_MODEL.md`;
- `IDENTITY_MODEL.md`;
- `AUTHORIZATION_MODEL.md`;
- `AUDIT_MODEL.md`;
- `MEMORY_MODEL.md`;
- `USER_WEIGHT_MODEL.md`;
- `RELATION_MODEL.md`;
- `Z_COCKPIT_IDENTITY_INTEGRATION.md`;
- `Z_COCKPIT_AUTHORIZATION_SIMULATION.md`.

## 36. Ergebnis

ProjectOS besitzt ein fachliches Busmodell für lose gekoppelte, versionierbare und nachvollziehbare Kommunikation. Befehle, Ereignisse, Anfragen, Antworten, Benachrichtigungen und Sicherheitsereignisse bleiben semantisch getrennt. Offline-Betrieb, Idempotenz, Korrelation, Fehlerbehandlung, Audit, Simulation, Plugins und Z_Cockpit sind berücksichtigt, ohne die Architektur an eine konkrete Transporttechnologie zu binden.