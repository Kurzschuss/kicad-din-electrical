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

## Bundle v4 – zuletzt umgesetzt

Neu vorhanden ist `projectos_project_bundle_v4.py` mit `CURRENT_PROJECTOS_BUNDLE_VERSION = 4`.

Regeln:

- v4 speichert `session`, `sync_log`, stabile `project_id` und `user_management`;
- der vorhandene v2/v3-Bundle-Code bleibt unverändert und wird als bewährte Legacy-Schicht weiterverwendet;
- v2/v3 bleiben lesbar und werden beim Laden als migrationspflichtig markiert;
- v3 behält seine vorhandene `project_id`; Benutzerverwaltung startet leer;
- v2 erhält wie bisher erst im Manager eine neue stabile `project_id`;
- beim nächsten expliziten Speichern wird auf v4 geschrieben; es gibt keinen Hintergrundschreibzugriff;
- ein `user_management`-Block eines fremden Projekts wird abgewiesen;
- Recovery kann v4 inklusive Benutzerverwaltung lesen und validieren.

Der `DinEditorProjectManager` verwendet jetzt die v4-Schicht. `user_management` ist Teil des Manager-Snapshots und damit des Dirty-State. `set_user_management()` akzeptiert ausschließlich Zustand derselben `project_id`. Save, Load, Recover, Discard und New Project führen den Benutzerverwaltungszustand konsistent mit.

Commits dieses Blocks:

- `e74f149f` feat(projectos): Bundle v4 mit Benutzerverwaltung ergänzen
- `7843a06f` feat(projectos): Projektmanager auf Bundle v4 umstellen
- `f3676ef0` test(projectos): Bundle v4 und Benutzerverwaltung absichern

## Tests / letzter bestätigter Stand

Die bestehende vollständige Suite blieb nach der Manager-Umstellung grün (Run #209). Die ergänzten v4-Regressionen sind ebenfalls grün: `ProjectOS complete test suite`, Run #210, für Commit `f3676ef0a8ed669d5dfbccd6dc4ae9cd483ae7b4`.

Abgesichert sind insbesondere v4-Roundtrip, Projektgrenze des Benutzerblocks, Dirty-State durch Benutzerverwaltungsänderung und explizite v3→v4-Migration.

PR #159 bleibt der integrierte ProjectOS-Umsetzungsbranch.

## Unmittelbar nächster Umsetzungsschritt

Als Nächstes Bundle v4 vollständig bis Save-As und Recovery absichern:

1. Save-As mit vollständigem `user_management` und unveränderter `project_id` testen;
2. v4-Recovery muss Benutzerverwaltung exakt wiederherstellen;
3. fehlerhafte Benutzerverwaltungsreferenzen in v4 müssen beim Load/Recovery transaktionssicher abgewiesen werden;
4. fehlgeschlagenes v4-Laden darf Managerzustand einschließlich `user_management` nicht verändern;
5. Recovery-Metadaten um v4-/Benutzerverwaltungsinformationen konsistent vervollständigen;
6. danach Z_Cockpit um einen read-only Persistenz-/Migrationsstatus für Benutzerverwaltung ergänzen.

## Starttext für einen neuen Chat

> Wir setzen die Entwicklung von `kicad-din-electrical / ProjectOS` fort. Lies zuerst `docs/handover/PROJECTOS_ZWISCHENSTAND_2026-08-09.md` auf Branch `test/load-failure-preserves-state` und prüfe PR #159. Der letzte vollständig grüne Stand ist ProjectOS complete test suite Run #210. Bundle v4 ist eingeführt: `user_management` wird versioniert persistiert, v2/v3 bleiben lesbar und werden erst beim expliziten Speichern auf v4 migriert. Der Projektmanager führt Benutzerverwaltung jetzt durch Save/Load/Recover/Discard/New Project und berücksichtigt sie im Dirty-State. Fahre mit Save-As-, Recovery- und transaktionssicheren Fehlerfällen für Bundle v4 fort. Alles auf Deutsch. Architekturregeln, Benutzergewichtung, DENY-Vorrang, Rechteherkunft und Korrelationskette nicht verlieren.
