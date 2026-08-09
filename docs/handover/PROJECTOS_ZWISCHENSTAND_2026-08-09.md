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

## Benutzerverwaltungs-Command-/Change-Service – aktueller Stand

`ProjectOSUserManagementChangeService` übernimmt Änderungen atomar: Für jede Operation wird zuerst ein vollständig validierter neuer `ProjectOSUserManagementState` aufgebaut und erst danach in den Manager übernommen. Erfolgreiche Änderungen markieren den Dirty-State; fehlgeschlagene Änderungen lassen State, Dirty-State und Hook unverändert.

Neben den objektbasierten Add-Methoden existieren jetzt enge fachliche Commands:

- `command_assign_permission(...)`;
- `command_assign_project_role(...)`;
- `command_activate_project_role(...)`;
- `command_deactivate_project_role(...)`;
- `command_request_approval(...)`;
- `command_record_approval(...)`;
- `command_complete_post_review(...)`.

Die Commands bauen die Domainobjekte selbst aus Fachparametern. Kritische Referenzen werden aus dem bestehenden Zustand abgeleitet:

- Projektrollen verwenden immer die aktuelle `project_id` des Managers;
- Aktivierungen übernehmen `user_id` und `scope` aus der referenzierten Projektrolle;
- Rückgaben übernehmen `user_id` und `scope` aus der referenzierten Aktivierung;
- Freigaben und Nachprüfungen verlangen eine bekannte `action_id` und bekannte Benutzer;
- unbekannte `user_id`, `role_assignment_id`, `activation_id` oder `action_id` werden vor Commit abgewiesen.

Damit kann ein Aufrufer widersprüchliche Kombinationen nicht mehr frei zusammensetzen. Die Benutzergewichtung bleibt weiterhin rein sichtbar und ohne automatische Autorisierungswirkung.

Der optionale `on_change`-Hook bleibt transportneutral. Er feuert ausschließlich nach erfolgreichem Commit und ist die vorbereitete Anschlussstelle für Audit-/Bus-Korrelation; der Change-Service erzeugt noch keine zweite fachliche Wahrheit.

Commits dieses Blocks:

- `382ce198` feat(projectos): atomaren Benutzerverwaltungs-Change-Service einführen
- `7dd862b0` test(projectos): atomare Benutzerverwaltungsänderungen absichern
- `a53a01c6` feat(projectos): fachliche Benutzerverwaltungs-Commands ergänzen
- `ff49e192` test(projectos): fachliche Benutzerverwaltungs-Commands absichern

## Tests / letzter bestätigter Stand

Die vollständige `ProjectOS complete test suite`, Run #235, ist für Commit `ff49e192f84d2064fe71b41c66f91bcd9da36a65` erfolgreich.

PR #159 bleibt der integrierte ProjectOS-Umsetzungsbranch.

## Unmittelbar nächster Umsetzungsschritt

Als Nächstes den neutralen `on_change`-Hook an die bestehende ProjectOS-Audit-/Bus-/Korrelationsschicht anbinden:

1. Change-Event um `actor_user_id`, `correlation_id`, `causation_id` und fachliche Referenz erweitern, ohne Domainwahrheit zu duplizieren;
2. erfolgreiche Commands als korrelierte Bus-/Audit-Nachweise emittieren;
3. fehlgeschlagene Commands dürfen keinerlei Bus-/Audit-Ereignis erzeugen;
4. Aktivierungs-/Rückgabe-/Freigabe-Commands müssen bestehende `action_id`/`activation_id`/`role_assignment_id` als Referenzen tragen;
5. direkte `set_user_management()`-Nutzung außerhalb von Load/Recover/Discard und Tests weiter zurückdrängen;
6. anschließend Undo/Redo-/Command-Historienstrategie für Benutzerverwaltung prüfen.

## Starttext für einen neuen Chat

> Wir setzen die Entwicklung von `kicad-din-electrical / ProjectOS` fort. Lies zuerst `docs/handover/PROJECTOS_ZWISCHENSTAND_2026-08-09.md` auf Branch `test/load-failure-preserves-state` und prüfe PR #159. Der letzte vollständig grüne Stand ist ProjectOS complete test suite Run #235. Bundle v4, Persistenz-/Migrationsstatus und Benutzerverwaltungs-Konsistenzdiagnosen sind integriert. `ProjectOSUserManagementChangeService` besitzt jetzt fachliche Commands für Rechte, Projektrollen, Aktivierung, Rückgabe, Freigabe und Nachprüfung; Projekt, Benutzer und Scope werden aus dem bestehenden State abgeleitet und jede Änderung ist atomar. Fahre mit der Audit-/Bus-/Korrelationsanbindung des Change-Hooks fort. Alles auf Deutsch. Architekturregeln, Benutzergewichtung, DENY-Vorrang, Rechteherkunft und Korrelationskette nicht verlieren.
