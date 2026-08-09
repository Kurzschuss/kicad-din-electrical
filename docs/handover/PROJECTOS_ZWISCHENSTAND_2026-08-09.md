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

## Z_Cockpit-Persistenz-/Migrationsstatus

`ZCockpitUserManagementPersistenceView` trennt Runtime-Fähigkeit und tatsächlich gespeicherten Dateistand. Angezeigt werden `current_bundle_version`, `persisted_bundle_version`, `bundle_v4_persisted`, `migration_pending`, `migration_target_version`, `user_management_persistence_version`, persistierte Objektzähler und `derived_not_persisted`.

## Z_Cockpit-Integration des Persistenzstatus – zuletzt umgesetzt

Der Persistenz-/Migrationsstatus ist jetzt in Projektleiter-Gesamtübersicht, Aufmerksamkeitsblock und Navigation eingebunden.

Regeln:

- `ZCockpitProjectLeadOverview` führt den vollständigen Persistenzstatus unter `persistence`;
- die Summary zeigt gespeicherte Bundle-Version, Migrationsbedarf und Anzahl persistierter Benutzerverwaltungsobjekte;
- ausstehende Migration setzt die Projektleiterampel mindestens auf Gelb und erzeugt einen expliziten Aufmerksamkeitshinweis;
- `ZCockpitAttentionView` erzeugt `USER_MANAGEMENT_BUNDLE_MIGRATION_PENDING` mit Priorität 20;
- der Attention-Item führt direkt zum neuen Navigationsziel `user_management_persistence`;
- `ZCockpitNavigationResolver` löst dieses Ziel read-only über `ZCockpitUserManagementPersistenceView` auf;
- ein bereits gespeichertes v4-Projekt erzeugt keinen Migrations-Attention-Item;
- die Sicht führt selbst keine Migration aus; v2/v3 werden weiterhin ausschließlich beim expliziten Speichern auf v4 migriert.

Commits dieses Blocks:

- `42f0ca00` feat(z-cockpit): Persistenzstatus in Projektleiterübersicht integrieren
- `25d367d7` feat(z-cockpit): Persistenzstatus als Navigationsziel ergänzen
- `5708cb53` feat(z-cockpit): Persistenzstatus über Navigation auflösen
- `149ec0bc` feat(z-cockpit): Bundle-Migration im Aufmerksamkeitsblock anzeigen
- `5556ebf8` test(z-cockpit): Persistenzstatus in Übersicht Aufmerksamkeit und Navigation absichern

## Tests / letzter bestätigter Stand

Die vollständige `ProjectOS complete test suite`, Run #221, ist für Commit `5556ebf87d5290b19afc28b563b1dfdb8994dae2` erfolgreich.

PR #159 bleibt der integrierte ProjectOS-Umsetzungsbranch.

## Unmittelbar nächster Umsetzungsschritt

Als Nächstes read-only Konsistenzdiagnosen für die Benutzerverwaltung ergänzen:

1. Referenzketten Benutzer→Recht/Rolle→Aktivierung→Beendigung sowie Anforderung→Freigabe→Nachprüfung diagnostisch erklären;
2. zwischen Fehler, Warnung und konsistentem Zustand unterscheiden;
3. beschädigte Persistenzdaten weiterhin beim Laden fail-closed abweisen, aber Runtime-/Bestandsprobleme ohne Dateiänderung sichtbar machen;
4. Diagnose als eigenes Z_Cockpit-Navigationsziel und Aufmerksamkeitsquelle integrieren;
5. danach Benutzerverwaltungsblock auf noch fehlende Änderungs-/Command-Services statt direkter State-Ersetzung prüfen.

## Starttext für einen neuen Chat

> Wir setzen die Entwicklung von `kicad-din-electrical / ProjectOS` fort. Lies zuerst `docs/handover/PROJECTOS_ZWISCHENSTAND_2026-08-09.md` auf Branch `test/load-failure-preserves-state` und prüfe PR #159. Der letzte vollständig grüne Stand ist ProjectOS complete test suite Run #221. Bundle v4 und `ProjectOSUserManagementState` sind persistenzseitig gehärtet. Der Benutzerverwaltungs-Persistenzstatus ist jetzt in Projektleiterübersicht, Aufmerksamkeitsblock und Navigation integriert; v2/v3→v4-Migration erscheint gelb und führt direkt zum read-only Detailstatus. Fahre mit read-only Konsistenzdiagnosen für Benutzer-/Rollen-/Aktivierungs-/Freigabereferenzen fort. Alles auf Deutsch. Architekturregeln, Benutzergewichtung, DENY-Vorrang, Rechteherkunft und Korrelationskette nicht verlieren.
