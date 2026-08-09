# ProjectOS – Zwischenstand / Chat-Übergabe

Stand: 2026-08-09
Repository: Kurzschuss/kicad-din-electrical
Arbeitsbranch: `test/load-failure-preserves-state`
Pull Request: #159 – `Test: fehlgeschlagenes Projektladen hält Managerzustand stabil`

## Architekturgrundlagen

Architecture Freeze 1.0 bleibt maßgeblich. ProjectOS ist die Grundlage des Projekts. Weiterhin gelten Single Source of Truth, Domain Ownership, Object First, Offline First, Simulation First, Documentation First und Configuration before Code. Die drei Perspektiven Entwickler, Engineering und Projektleiter bleiben erhalten.

## Benutzerverwaltung und Autorisierung

Vorhanden sind Benutzerprofile mit Benutzergewichtung 0–1000, typisierte Rechteherkünfte, Scope, Risikoklasse, Gültigkeit, Delegation und read-only Rechte-Simulation. `DENY` hat Vorrang vor `ALLOW`. Benutzergewichtung ist sichtbar, ersetzt aber keine Freigabe und überstimmt kein `DENY`.

Die Projektfunktionen `project_lead`, `deputy`, `trusted_person` und `successor` sind eigene projektbezogene Beziehungen. Zuweisung, Aktivierung, Freigabe und Beendigung sind strikt getrennt. Kritische Aktivierungen und Rückgaben arbeiten fail-closed über Vier-Augen-Freigaben. Notfälle dürfen vorläufig wirken, bleiben nachprüfungspflichtig und werden korreliert auf Bus/Audit nachgewiesen.

## Freigabe-/Nachprüfungskette und Wissensherkunft

Die Kette wird durch `project_id`, `correlation_id` und `causation_id` durchgängig geführt: `approval_requested` → optional `approval_decided` → `approval_effectiveness_evaluated` → bei Nachprüfung `post_review_completed` oder `post_review_escalated`.

Negative Nachprüfung schreibt die historische Notfallwirkung nicht rückwirkend um; `historical_emergency_effect_preserved=true` bleibt erhalten. Freigabe-/Nachprüfungs-Traces werden ohne zweite Wahrheit als referenzierte Wissensnachweise materialisiert. `knowledge_origin` erklärt `truth_source`, `action_id`, `review_id`, `message_id`, `correlation_id` und kann direkt zum `approval_trace` navigieren.

## Persistenz und Bundle v4

`ProjectOSUserManagementState` mit `USER_MANAGEMENT_PERSISTENCE_VERSION = 1` persistiert ausschließlich fachliche Benutzer-, Rechte-, Rollen-, Aktivierungs-, Beendigungs-, Freigabe- und Nachprüfungsdaten. Reproduzierbare Evaluator-, Simulations-, Z_Cockpit-, Navigation-, Trace- und materialisierte Wissensdaten werden nicht persistiert.

Bundle v4 speichert `session`, `sync_log`, stabile `project_id` und `user_management`. v2/v3 bleiben lesbar und werden erst beim expliziten Speichern auf v4 migriert. Save-As, Recovery, Dirty-State und transaktionssichere Fehlerfälle sind inklusive Benutzerverwaltung abgesichert.

## Z_Cockpit Persistenz/Migration und Konsistenz

`ZCockpitUserManagementPersistenceView` zeigt tatsächliche gespeicherte Bundle-Version, Migrationsbedarf, Persistenzversion des Benutzerblocks, Objektzähler und bewusst nicht persistierte Ableitungen. Der Status ist in Projektleiterübersicht, Attention und Navigation integriert. `USER_MANAGEMENT_BUNDLE_MIGRATION_PENDING` erscheint gelb und führt zum read-only Ziel `user_management_persistence`.

`ZCockpitUserManagementConsistencyView` prüft read-only die semantischen Lifecycle-Ketten Benutzer→Recht/Rolle→Aktivierung→Beendigung sowie Freigabeanforderung→Freigabe→Nachprüfung. Rote Fehler und gelbe Hinweise sind in Projektleiterübersicht, Aufmerksamkeit und Navigation eingebunden.

## Benutzerverwaltungs-Command-/Change-Service

`ProjectOSUserManagementChangeService` übernimmt Änderungen atomar: Für jede Operation wird zuerst ein vollständig validierter neuer `ProjectOSUserManagementState` aufgebaut und erst danach in den Manager übernommen. Erfolgreiche Änderungen markieren den Dirty-State; fehlgeschlagene Änderungen lassen State, Dirty-State und Hook unverändert.

Enge fachliche Commands existieren für Rechte, Projektrollen, Aktivierung, Rückgabe, Freigabeanforderung, Freigabeentscheidung und Nachprüfung. Projekt, Benutzer und Scope werden aus dem bestehenden Zustand abgeleitet; unbekannte Referenzen werden vor Commit abgewiesen.

## Audit-/Bus-/Korrelationsanbindung – zuletzt umgesetzt

Neu vorhanden sind `ProjectOSUserManagementChangeTrace` und `ProjectOSUserManagementChangeTraceEmitter`.

Der Emitter wird als `on_change`-Hook des Change-Service verwendet. Er erzeugt keine Mutation und keine zweite fachliche Wahrheit, sondern beschreibt ausschließlich bereits erfolgreich übernommene Änderungen als ProjectOS-Busnachricht und Audit-Eintrag.

Regeln:

- jede erfolgreiche Benutzerverwaltungsänderung erzeugt genau einen Bus-Nachweis und genau einen Audit-Eintrag;
- alle Änderungen eines Emitter-Vorgangs tragen dieselbe `correlation_id`;
- Folgeschritte bilden eine echte `causation_id`-Kette über die vorherige `message_id`;
- der Nachweis führt `operation`, `actor_user_id`, fachliche `reference`, Dirty-State und das bereits persistierte Domainobjekt;
- Projektrollen verwenden `assigned_by_user_id` als Akteur, sofern vorhanden;
- Aktivierungen/Rückgaben verwenden `triggered_by_user_id`, sofern vorhanden;
- Freigabeanforderung, Freigabeentscheidung und Nachprüfung verwenden jeweils Anforderer, Freigeber bzw. Prüfer als Akteur;
- Delegationen verwenden `delegated_by_user_id`, sofern vorhanden;
- bei fehlgeschlagenen Commands wird der Hook nicht aufgerufen und es entsteht weder Bus- noch Audit-Nachweis;
- der Emitter hält einen read-only vorherigen Snapshot, um die tatsächlich geänderte Fachreferenz aus dem Delta zu bestimmen; dadurch wird z. B. eine Gewichtsänderung eines nicht-letzten Benutzers korrekt zugeordnet.

Commits dieses Blocks:

- `f2592de3` feat(projectos): Benutzerverwaltungsänderungen an Audit und Bus anbinden
- `2f45cbe3` fix(projectos): Änderungsreferenz aus Snapshot-Differenz bestimmen
- `40d332d0` test(projectos): korrelierte Benutzerverwaltungsänderungen absichern

## Tests / letzter bestätigter Stand

Die vollständige `ProjectOS complete test suite`, Run #239, ist für Commit `40d332d0229fe178ca7411f517b5e4a18f21f157` erfolgreich.

PR #159 bleibt der integrierte ProjectOS-Umsetzungsbranch.

## Unmittelbar nächster Umsetzungsschritt

Als Nächstes die Audit-/Bus-Anbindung in die Command-Nutzung selbst weiter härten:

1. expliziten Command-Kontext mit Akteur/Korrelation für Fälle ergänzen, in denen der Akteur nicht aus dem Domainobjekt ableitbar ist (z. B. direkte Rechtezuweisung oder Benutzergewichtung durch Administrator);
2. direkte `set_user_management()`-Nutzung außerhalb von Load/Recover/Discard und Tests weiter zurückdrängen;
3. Benutzerverwaltungs-Command-Historie und Undo/Redo-Strategie definieren, ohne Audit-Historie rückwirkend zu löschen;
4. Undo/Redo als neue fachliche Änderung mit eigener Korrelation/Auditspur modellieren;
5. danach Command-Rechte selbst über den vorhandenen Autorisierungs-/Vier-Augen-Vertrag absichern.

## Starttext für einen neuen Chat

> Wir setzen die Entwicklung von `kicad-din-electrical / ProjectOS` fort. Lies zuerst `docs/handover/PROJECTOS_ZWISCHENSTAND_2026-08-09.md` auf Branch `test/load-failure-preserves-state` und prüfe PR #159. Der letzte vollständig grüne Stand ist ProjectOS complete test suite Run #239. `ProjectOSUserManagementChangeService` besitzt atomare fachliche Commands. Neu ist `ProjectOSUserManagementChangeTraceEmitter`: erfolgreiche Benutzerverwaltungsänderungen erzeugen korrelierte Bus-/Audit-Nachweise mit Fachreferenz, Akteur und Kausalkette; fehlgeschlagene Commands erzeugen nichts. Fahre mit explizitem Command-Kontext für nicht eindeutig ableitbare Akteure und anschließend Undo/Redo-/Command-Historienstrategie fort. Alles auf Deutsch. Architekturregeln, Benutzergewichtung, DENY-Vorrang, Rechteherkunft und Korrelationskette nicht verlieren.
