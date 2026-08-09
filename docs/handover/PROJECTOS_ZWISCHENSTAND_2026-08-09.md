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

## Z_Cockpit Persistenz/Migration

`ZCockpitUserManagementPersistenceView` zeigt tatsächliche gespeicherte Bundle-Version, Migrationsbedarf, Persistenzversion des Benutzerblocks, Objektzähler und bewusst nicht persistierte Ableitungen. Der Status ist in Projektleiterübersicht, Attention und Navigation integriert. `USER_MANAGEMENT_BUNDLE_MIGRATION_PENDING` erscheint gelb und führt zum read-only Ziel `user_management_persistence`.

## Benutzerverwaltungs-Konsistenzdiagnosen – zuletzt umgesetzt

Neu vorhanden ist `ZCockpitUserManagementConsistencyView`.

Die Diagnose prüft read-only die semantischen Lifecycle-Ketten:

- Benutzer → explizite Rechtezuweisung;
- Benutzer → Projektrolle → Aktivierung → Beendigung;
- Freigabeanforderung → Freigabe → Notfall-Nachprüfung.

Der Persistenzvertrag bleibt für grobe Referenzintegrität fail-closed zuständig. Die neue Z_Cockpit-Schicht erkennt zusätzlich formal vorhandene, aber semantisch widersprüchliche Verknüpfungen, unter anderem:

- Aktivierung und Projektrolle gehören zu unterschiedlichen Benutzern (`UM_ACTIVATION_USER_MISMATCH`);
- Aktivierung und Projektrolle haben abweichenden Scope (`UM_ACTIVATION_SCOPE_MISMATCH`);
- Beendigung und Aktivierung gehören zu unterschiedlichen Benutzern (`UM_DEACTIVATION_USER_MISMATCH`);
- Beendigung und Aktivierung haben abweichenden Scope (`UM_DEACTIVATION_SCOPE_MISMATCH`);
- Nachprüfung gehört zu einer Nicht-Notfall-Anforderung (`UM_POST_REVIEW_NON_EMERGENCY`);
- Anforderer prüft den eigenen Notfallvorgang (`UM_POST_REVIEW_SELF_REVIEW`);
- mehrere Nachprüfungen derselben Aktion sind mehrdeutig (`UM_POST_REVIEW_AMBIGUOUS`).

Fehler werden rot, Scope-Hinweise gelb und konsistenter Zustand grün bewertet. Die Diagnose verändert keine fachlichen oder persistierten Daten.

Die Diagnose ist vollständig integriert:

- `ZCockpitProjectLeadOverview` führt `user_management_consistency` und eigene Summary-Zähler;
- rote Konsistenzfehler setzen die Projektleiterampel auf Rot;
- `ZCockpitAttentionView` erzeugt aus jedem Diagnosepunkt einen priorisierten Arbeitspunkt;
- roter Fehler erhält Priorität 30, gelber Hinweis Priorität 20;
- neues Navigationsziel `user_management_consistency` öffnet die read-only Diagnose über den `ZCockpitNavigationResolver`.

Commits dieses Blocks:

- `9830876a` feat(z-cockpit): Benutzerverwaltungs-Konsistenzdiagnosen ergänzen
- `523b4815` test(z-cockpit): Benutzerverwaltungs-Konsistenzdiagnosen absichern
- `d1d65fc3` feat(z-cockpit): Benutzerkonsistenz in Projektleiterübersicht integrieren
- `8dd2095a` feat(z-cockpit): Benutzerkonsistenz als Navigationsziel ergänzen
- `a9e3406c` feat(z-cockpit): Benutzerkonsistenz über Navigation auflösen
- `60d38512` feat(z-cockpit): Benutzerkonsistenz im Aufmerksamkeitsblock anzeigen
- `ff7a9bf3` test(z-cockpit): Benutzerkonsistenz in Übersicht Aufmerksamkeit und Navigation absichern

## Tests / letzter bestätigter Stand

Die vollständige `ProjectOS complete test suite`, Run #229, ist für Commit `ff7a9bf384d4631a38509138ec43aa7d21283386` erfolgreich.

PR #159 bleibt der integrierte ProjectOS-Umsetzungsbranch.

## Unmittelbar nächster Umsetzungsschritt

Als Nächstes den Benutzerverwaltungsblock auf **Command-/Change-Service-Reife** prüfen. Der fachliche Zustand ist persistierbar, simulierbar und diagnostizierbar, wird derzeit aber noch über vollständige `ProjectOSUserManagementState`-Ersetzung in den Manager gesetzt. Nächste Schritte:

1. atomare Commands für Benutzer anlegen/ändern, Gewichtung setzen und Benutzer deaktivieren definieren;
2. Commands für Rechtezuweisung/-entzug, Projektrollen-Zuweisung, Aktivierung, Beendigung, Freigabe und Nachprüfung definieren;
3. jede Änderung über einen zentralen Change-Service mit Validierung, Dirty-State und Audit-/Bus-Hook führen;
4. keine direkte Mutation und keine zweite fachliche Wahrheit zulassen;
5. read-only Simulation weiterhin strikt vom tatsächlichen Command-Pfad trennen.

## Starttext für einen neuen Chat

> Wir setzen die Entwicklung von `kicad-din-electrical / ProjectOS` fort. Lies zuerst `docs/handover/PROJECTOS_ZWISCHENSTAND_2026-08-09.md` auf Branch `test/load-failure-preserves-state` und prüfe PR #159. Der letzte vollständig grüne Stand ist ProjectOS complete test suite Run #229. Bundle v4 und Benutzerverwaltung sind persistenzseitig gehärtet. Z_Cockpit besitzt Persistenz-/Migrationsstatus sowie read-only Benutzerverwaltungs-Konsistenzdiagnosen, integriert in Projektleiterübersicht, Aufmerksamkeit und Navigation. Fahre mit der Command-/Change-Service-Reife des Benutzerverwaltungsblocks fort; direkte State-Ersetzung soll durch atomare, validierte Änderungsoperationen ergänzt werden. Alles auf Deutsch. Architekturregeln, Benutzergewichtung, DENY-Vorrang, Rechteherkunft und Korrelationskette nicht verlieren.
