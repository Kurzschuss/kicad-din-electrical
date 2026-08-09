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

## Benutzerverwaltungs-Persistenzvertrag

`ProjectOSUserManagementState` mit `USER_MANAGEMENT_PERSISTENCE_VERSION = 1` ist vorhanden. Persistiert werden ausschließlich fachliche Zustände: Benutzerprofile, explizite Rechtezuweisungen, Projektrollen, Aktivierungen, Beendigungen/Rückgaben, Freigabeanforderungen, Freigabe-/Ablehnungsentscheidungen und Notfall-Nachprüfungen.

Nicht persistiert werden reproduzierbare Ableitungen: Autorisierungs-/Evaluator-Ergebnisse, Simulationen, Z_Cockpit-Sichten, Attention-Items, Breadcrumb-/Navigationskontexte, Approval-/Post-Review-Traces sowie materialisierte Freigabe-/Nachprüfungs-Wissensnachweise.

Der Vertrag validiert Projektgrenzen, eindeutige IDs und Referenzketten Rolle→Benutzer, Aktivierung→Rolle, Beendigung→Aktivierung, Freigabe→Anforderung und Nachprüfung→Anforderung fail-closed.

## Bundle v4

`projectos_project_bundle_v4.py` führt `CURRENT_PROJECTOS_BUNDLE_VERSION = 4`.

Regeln:

- v4 speichert `session`, `sync_log`, stabile `project_id` und `user_management`;
- v2/v3 bleiben lesbar und werden beim Laden als migrationspflichtig markiert;
- Migration auf v4 erfolgt ausschließlich beim expliziten Speichern;
- v3 behält seine vorhandene `project_id`, Benutzerverwaltung startet leer;
- v2 erhält wie bisher erst im Manager eine neue stabile `project_id`;
- fremde `user_management.project_id` wird fail-closed abgewiesen;
- `user_management` ist Bestandteil des Manager-Snapshots und Dirty-State;
- Save, Load, Save-As, Recover, Discard und New Project führen den Benutzerverwaltungszustand mit;
- Save-As bewahrt die stabile `project_id` und den vollständigen Benutzerzustand;
- Recovery stellt Benutzerverwaltung vollständig wieder her;
- beschädigte v4-Benutzerdaten verändern bei fehlgeschlagenem Load/Recover keinen bestehenden Managerzustand.

## Z_Cockpit-Persistenz-/Migrationsstatus – zuletzt umgesetzt

Neu vorhanden ist `ZCockpitUserManagementPersistenceView`.

Die Sicht trennt ausdrücklich zwischen Runtime-Fähigkeit und tatsächlich gespeichertem Dateistand:

- `current_bundle_version` zeigt die aktuell unterstützte Bundle-Version 4;
- `persisted_bundle_version` liest den tatsächlich gespeicherten Dateistand, sofern ein Projektpfad vorhanden ist;
- `bundle_v4_persisted` ist nur dann wahr, wenn die Datei tatsächlich als v4 gespeichert ist;
- ein neues, noch nie gespeichertes Projekt wird nicht fälschlich als bereits persistiertes v4-Projekt ausgewiesen;
- geladenes v2/v3 zeigt `migration_pending=true` und `migration_target_version=4`;
- `user_management_persistence_version` zeigt die Version des Benutzerverwaltungs-Persistenzvertrags;
- `persisted_counts` zählt Benutzer, Rechtezuweisungen, Projektrollen, Aktivierungen, Beendigungen, Freigabeanforderungen, Freigaben und Nachprüfungen;
- `persisted_object_count` liefert die Gesamtsumme dieser fachlichen Persistenzobjekte;
- `derived_not_persisted` zeigt transparent alle bewusst nicht gespeicherten reproduzierbaren Ableitungen.

Die Sicht ist vollständig read-only und verändert weder Manager-, Datei- noch Benutzerzustand.

Commits dieses Blocks:

- `cb9fde71` feat(z-cockpit): Benutzerverwaltungs-Persistenzstatus anzeigen
- `c2d855bf` test(z-cockpit): Persistenz- und Migrationsstatus absichern

## Tests / letzter bestätigter Stand

Die vollständige `ProjectOS complete test suite`, Run #215, ist für Commit `c2d855bf6c3136a87400b4db5dad72411eb6b424` erfolgreich.

PR #159 bleibt der integrierte ProjectOS-Umsetzungsbranch.

## Unmittelbar nächster Umsetzungsschritt

Als Nächstes den Persistenzstatus in die Projektleiter-Gesamtübersicht und den Aufmerksamkeitsblock einbinden:

1. ausstehende v2/v3→v4-Migration als gelben Hinweis anzeigen;
2. Recovery mit vorhandenem Benutzerverwaltungsblock sichtbar machen;
3. inkonsistente oder nicht lesbare Persistenzinformationen als Diagnosezustand behandeln, ohne Dateiänderung;
4. Persistenz-/Migrationsstatus als eigenes Navigationsziel ergänzen;
5. danach read-only Konsistenzdiagnosen für Benutzerverwaltungsreferenzen und Lifecycle-Ketten ergänzen.

## Starttext für einen neuen Chat

> Wir setzen die Entwicklung von `kicad-din-electrical / ProjectOS` fort. Lies zuerst `docs/handover/PROJECTOS_ZWISCHENSTAND_2026-08-09.md` auf Branch `test/load-failure-preserves-state` und prüfe PR #159. Der letzte vollständig grüne Stand ist ProjectOS complete test suite Run #215. Bundle v4 ist inklusive Benutzerverwaltung für Roundtrip, Dirty-State, Save-As, Recovery und transaktionssichere Fehlerfälle abgesichert. `ZCockpitUserManagementPersistenceView` zeigt jetzt tatsächliche gespeicherte Bundle-Version, Migrationsbedarf, Benutzerverwaltungs-Persistenzversion, Objektzähler und bewusst nicht persistierte Ableitungen. Fahre mit der Einbindung dieses Persistenzstatus in Projektleiterübersicht, Aufmerksamkeit und Navigation fort. Alles auf Deutsch. Architekturregeln, Benutzergewichtung, DENY-Vorrang, Rechteherkunft und Korrelationskette nicht verlieren.
