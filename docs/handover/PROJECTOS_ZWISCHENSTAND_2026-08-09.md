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

## Benutzerverwaltungs-Command-/Change-Service – zuletzt umgesetzt

Neu vorhanden ist `ProjectOSUserManagementChangeService`.

Der Service ersetzt direkte fachliche Komplettänderungen schrittweise durch atomare Operationen. Für jede Änderung wird zuerst ein vollständig validierter neuer `ProjectOSUserManagementState` aufgebaut. Erst nach erfolgreicher Validierung wird der Zustand über den Manager übernommen. Dadurch entstehen keine teilweisen Benutzerverwaltungszustände.

Bereits vorhandene Operationen:

- `create_user(...)`;
- `change_user_weight(...)`;
- `assign_permission(...)`;
- `assign_project_role(...)`;
- `activate_project_role(...)`;
- `deactivate_project_role(...)`;
- `request_approval(...)`;
- `record_approval(...)`;
- `complete_post_review(...)`.

Der optionale `on_change`-Hook erzeugt nach erfolgreicher Änderung ein transportneutrales Change-Event mit `operation`, `project_id` und Dirty-State. Er ist ausdrücklich als spätere Audit-/Bus-Anbindungsstelle vorgesehen; der Change-Service erzeugt derzeit selbst noch keine zweite Audit- oder Buswahrheit.

Abgesicherte Regeln:

- erfolgreiche Änderung setzt den Manager über den bestehenden Snapshot automatisch auf Dirty;
- nach explizitem Speichern ist der Dirty-State wieder sauber;
- Änderung der Benutzergewichtung bleibt ohne Autorisierungswirkung (`weight_affects_authorization=false`);
- unbekannte Benutzerreferenzen werden vor Zustandsübernahme abgewiesen;
- doppelte Benutzer-ID wird vor Zustandsübernahme abgewiesen;
- bei fehlgeschlagener Änderung bleiben vollständiger `user_management`-Zustand und Dirty-State unverändert;
- der Change-Hook wird bei fehlgeschlagenen Änderungen nicht aufgerufen;
- erfolgreiche Änderungen erzeugen genau ein transportneutrales Hook-Ereignis.

Commits dieses Blocks:

- `382ce198` feat(projectos): atomaren Benutzerverwaltungs-Change-Service einführen
- `7dd862b0` test(projectos): atomare Benutzerverwaltungsänderungen absichern

## Tests / letzter bestätigter Stand

Die vollständige `ProjectOS complete test suite`, Run #232, ist für Commit `7dd862b0e435404af47e1c9470b9925487ee09c7` erfolgreich.

PR #159 bleibt der integrierte ProjectOS-Umsetzungsbranch.

## Unmittelbar nächster Umsetzungsschritt

Als Nächstes den Change-Service von objektbasierten Add-Operationen auf engere fachliche Commands erweitern:

1. Projektrolle direkt aus `user_id`, Rolle, Scope, Gültigkeit und Zuweisungsherkunft erzeugen;
2. Aktivierung direkt aus `role_assignment_id`, Grund, Zeitraum, Scope und Trigger erzeugen;
3. Beendigung/Rückgabe direkt aus `activation_id`, Grund, Endzeitpunkt und Trigger erzeugen;
4. Freigabeanforderung/-entscheidung und Nachprüfung über konkrete Command-Parameter erzeugen;
5. neutralen Change-Hook anschließend an bestehende ProjectOS-Audit-/Bus-Korrelation anbinden, ohne doppelte fachliche Wahrheit;
6. direkte `set_user_management()`-Nutzung außerhalb von Load/Recover/Discard/Tests schrittweise zurückdrängen.

## Starttext für einen neuen Chat

> Wir setzen die Entwicklung von `kicad-din-electrical / ProjectOS` fort. Lies zuerst `docs/handover/PROJECTOS_ZWISCHENSTAND_2026-08-09.md` auf Branch `test/load-failure-preserves-state` und prüfe PR #159. Der letzte vollständig grüne Stand ist ProjectOS complete test suite Run #232. Bundle v4, Persistenz-/Migrationsstatus und Benutzerverwaltungs-Konsistenzdiagnosen sind integriert. Neu ist `ProjectOSUserManagementChangeService`: Änderungen werden atomar über einen vollständig validierten neuen `ProjectOSUserManagementState` übernommen, markieren Dirty-State und besitzen einen transportneutralen Change-Hook für spätere Audit-/Bus-Anbindung. Fahre mit engeren fachlichen Commands für Rolle, Aktivierung, Rückgabe, Freigabe und Nachprüfung fort. Alles auf Deutsch. Architekturregeln, Benutzergewichtung, DENY-Vorrang, Rechteherkunft und Korrelationskette nicht verlieren.
