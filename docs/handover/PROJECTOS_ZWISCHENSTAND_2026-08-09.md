# ProjectOS – Zwischenstand / Chat-Übergabe

Stand: 2026-08-09
Repository: Kurzschuss/kicad-din-electrical
Arbeitsbranch: `test/load-failure-preserves-state`
Pull Request: #159 – `Test: fehlgeschlagenes Projektladen hält Managerzustand stabil`

## Zweck dieses Dokuments

Dieses Dokument ist der belastbare Übergabepunkt für einen neuen Chat. Es hält den zuletzt umgesetzten technischen Stand, die Architekturregeln und den unmittelbar nächsten Arbeitsschritt fest.

## Architekturgrundlagen

Architecture Freeze 1.0 bleibt maßgeblich. ProjectOS ist die Grundlage des Projekts. Weiterhin gelten insbesondere: Single Source of Truth, Domain Ownership, Object First, Offline First, Simulation First, Documentation First und Configuration before Code. Die drei Perspektiven Entwickler, Engineering und Projektleiter bleiben erhalten.

Die geplante Benutzerverwaltung bleibt Bestandteil der Gesamtarchitektur: Rollen, Berechtigungen, Ausnahmerechte, Whitelist/Blacklist, Projektleiter, Stellvertretung, Vertrauensperson, Nachfolger, Benutzergewichtung sowie eine Rechte-Simulation. Z_Cockpit soll effektive Rechte und deren Herkunft darstellen können, darunter Rolle, direkte Zuweisung, Delegation, DENY, Ausnahme, Risikoklasse, Ablauf und Gültigkeitsbereich.

## Persistenz und Recovery

Der Persistenz-/Recovery-Pfad wurde stark abgesichert:

- fehlgeschlagene Loads dürfen keinen Teilzustand übernehmen;
- kaputtes JSON, inkompatible Bundle-Version und semantisch ungültige Projektdaten lassen den Managerzustand unverändert;
- atomarer Save-Pfad;
- vorheriger gültiger Stand kann als Recovery erhalten bleiben;
- Recovery ist ausschließlich explizit und kein stilles Fallback;
- Recovery wird strukturell und semantisch validiert;
- Recovery-Status ist read-only auswertbar;
- GUI-/Z_Cockpit-Adapter liefert deutsche Recovery-Zustände;
- Recovery-Metadaten enthalten Herkunft, Zeitpunkt und Versionsbezug;
- nach Recovery bleibt das Projekt bis zum erneuten erfolgreichen Speichern dirty.

## Stabile Projektidentität

Neue Projektbundles verwenden Bundle-Version 3 und enthalten eine kanonische `project_id` als UUID.

Regeln:

- `project_id` ist unabhängig vom Dateipfad;
- Save-As erhält dieselbe Projektidentität;
- `new_project()` erzeugt eine neue Projektidentität;
- Save, Load und Recovery erhalten die ID;
- Bundle v2 bleibt lesbar;
- beim Laden eines v2-Bundles wird eine neue UUID im Manager erzeugt und die Migration als pending/dirty markiert;
- keine Hintergrundänderung der alten Datei;
- erst ein expliziter erfolgreicher Save migriert dauerhaft auf Bundle v3.

## Projektkorrelation, Bus und Audit

Es existiert ein gemeinsamer read-only Projektkontext mit `project_id`, Projektpfad, Migrationsstatus und Recovery-Herkunft.

Der transportneutrale ProjectOS-Nachrichtenumschlag enthält unter anderem:

- `schema_version`
- `message_id`
- `message_type`
- `name`
- `project_id`
- `correlation_id`
- `causation_id`
- `timestamp`
- `payload`

Der Umschlag ist brokerneutral.

Das Synchronisationsaudit führt inzwischen:

- `project_id`
- optional `correlation_id`
- optional `causation_id`

Damit kann Z_Cockpit zwischen projektbezogenen, vorgangsbezogenen und konkret ursachenbezogenen Nachweisen unterscheiden. Alte Auditdaten ohne diese Felder bleiben kompatibel und werden nicht künstlich korreliert.

## Projektgedächtnis

Erster Runtime-Baustein ist vorhanden:

- `ProjectOSKnowledgeElement`
- `ProjectOSProjectMemory`
- `ProjectOSKnowledgeRelation`

Wissenselemente können `project_id`, `correlation_id` und `causation_id` tragen. Eine Nachricht wird ausdrücklich nicht automatisch zu Wissen; Wissen muss explizit angelegt werden.

Typisierte Wissensbeziehungen umfassen unter anderem:

- `justifies`
- `contradicts`
- `confirms`
- `refutes`
- `supersedes`
- `complements`
- `depends_on`
- `implemented_by`
- `tested_by`
- `causes`
- `affects`
- `derived_from`
- `documented_in`
- `published_in`
- `learned_from`

Der Graph validiert vorhandene Knoten, Projektzugehörigkeit, Beziehungstypen, eindeutige IDs und verbietet Selbstbeziehungen.

## Wissenspfade und Herkunft

Der Wissensgraph kann explizit gespeicherte Pfade zwischen Wissenselementen ermitteln und Herkunftswurzeln eines Zielknotens bestimmen. Fehlende Zwischenschritte werden nicht erfunden.

Z_Cockpit kann dadurch Fragen unterstützen wie:

- Warum existiert diese Implementierung?
- Welche Anforderung führte dazu?
- Welche Entscheidung liegt dazwischen?
- Welcher Test bestätigt sie?
- Welche Erkenntnis entstand daraus?

## Widerspruch und Ablösung

Der Wissensstatus trennt:

- `declared_status` – explizit gespeicherter Status;
- `graph_status` – read-only aus expliziten Beziehungen abgeleitete Sicht.

Graphzustände umfassen derzeit insbesondere `unchallenged`, `conflicted` und `superseded`.

Mehrstufige `supersedes`-Ketten werden verfolgt. Ein eindeutiger Endnachfolger kann als aktueller expliziter Nachfolger ausgewiesen werden. Mehrdeutige Endnachfolger und Zyklen werden als Ablösekonflikt erkannt; es wird kein aktueller Stand erfunden.

## Z_Cockpit-Korrelationssicht

Die read-only Projektkorrelationssicht führt zusammen:

- Projektkontext
- Bus-/Nachrichtenkorrelation
- Audit
- Projektgedächtnis
- Wissensbeziehungen und Wissenspfade
- Herkunftserklärungen
- Recovery

Ein `correlation_id`-Filter bleibt strikt. Projektweite oder fremde Elemente werden nicht künstlich einem Vorgang zugeschrieben.

## Wissensgraph-Konsistenzdiagnose – zuletzt umgesetzt

Zuletzt wurde eine read-only Konsistenzdiagnose für den Wissensgraphen ergänzt und in Z_Cockpit eingebunden.

Sie erkennt unter anderem:

- `ISOLATED_KNOWLEDGE`
- `DUPLICATE_SEMANTIC_RELATION`
- `SUPERSESSION_CONFLICT`
- `UNRESOLVED_CAUSATION`
- `UNRESOLVED_CORRELATION`

Die Diagnose liefert `available`, `is_consistent`, `issue_count` und konkrete `issues`. Sie respektiert den Projekt-/Korrelationsscope und verändert keine Daten.

Die vollständige `ProjectOS complete test suite`, Run #110, war für diesen Stand erfolgreich.

## Unmittelbar nächster Umsetzungsschritt

Als Nächstes soll die Wissensgraph-Diagnose klassifiziert und priorisiert werden:

1. Schweregrad pro Diagnose (`info`, `warning`, `error` bzw. final festzulegender Vertrag).
2. Betroffene Wissensknoten/Beziehungen eindeutig referenzieren.
3. Empfohlene Prüfaktion als read-only Handlungshinweis bereitstellen.
4. Aggregierten Diagnosezustand für Z_Cockpit ableiten.
5. Z_Cockpit-Ampellogik darauf aufbauen.
6. Regressionstests und vollständige CI.

Dabei darf die Diagnose weiterhin keine automatische Reparatur und keine fachliche Wahrheit erzeugen.

## Wichtige Fortsetzungspunkte nach der Diagnose

Nach Diagnoseklassifizierung/-priorisierung weiterführen:

- Z_Cockpit als zentrale Nachweis- und Projektleitersicht ausbauen;
- Benutzerverwaltung und Rechteherkunft inklusive Benutzergewichtung und Rechte-Simulation weiter umsetzen;
- Projektgedächtnis persistent machen, sobald der Persistenzvertrag dafür sauber definiert ist;
- Bus-/Audit-/Memory-Korrelation konsequent über `project_id`, `correlation_id` und `causation_id` beibehalten;
- Dokumentation parallel zur Implementierung pflegen.

## Starttext für einen neuen Chat

> Wir setzen die Entwicklung von `kicad-din-electrical / ProjectOS` fort. Lies zuerst `docs/handover/PROJECTOS_ZWISCHENSTAND_2026-08-09.md` auf Branch `test/load-failure-preserves-state` und prüfe PR #159. Der letzte vollständig grüne Stand ist ProjectOS complete test suite Run #110. Fahre danach mit der Diagnoseklassifizierung und Priorisierung des Wissensgraphen für Z_Cockpit fort. Alles auf Deutsch. Bestehende Architekturregeln und den dokumentierten Benutzerverwaltungs-/Rechtesimulationsumfang nicht verlieren.
