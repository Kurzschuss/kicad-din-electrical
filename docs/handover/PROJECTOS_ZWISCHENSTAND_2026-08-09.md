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

## Bundle v4 – aktueller Stand

`projectos_project_bundle_v4.py` führt `CURRENT_PROJECTOS_BUNDLE_VERSION = 4`.

Regeln:

- v4 speichert `session`, `sync_log`, stabile `project_id` und `user_management`;
- v2/v3 bleiben lesbar und werden beim Laden als migrationspflichtig markiert;
- Migration auf v4 erfolgt ausschließlich beim expliziten Speichern;
- v3 behält seine vorhandene `project_id`, Benutzerverwaltung startet leer;
- v2 erhält wie bisher erst im Manager eine neue stabile `project_id`;
- fremde `user_management.project_id` wird fail-closed abgewiesen;
- `user_management` ist Bestandteil des Manager-Snapshots und Dirty-State;
- Save, Load, Save-As, Recover, Discard und New Project führen den Benutzerverwaltungszustand mit.

## Bundle-v4-Hardening – zuletzt umgesetzt

Neu abgesichert sind die harten Lifecycle- und Fehlerfälle:

- Save-As bewahrt die stabile `project_id` und den vollständigen `user_management`-Zustand;
- v4-Recovery stellt Benutzerverwaltung und Projektidentität aus dem Recovery-Bundle vollständig wieder her;
- Recovery-Metadaten zeigen `bundle_version`, `project_id` und `user_management_present`;
- beschädigte oder widersprüchliche Benutzerverwaltungsreferenzen werden bereits beim Laden fail-closed abgewiesen;
- fehlgeschlagenes v4-Load verändert keinerlei bestehenden Managerzustand;
- fehlgeschlagenes v4-Recover verändert keinerlei bestehenden Managerzustand.

Für die Transaktionssicherheit wird explizit der komplette relevante Zustand verglichen:

- `project_id`;
- aktueller Projektpfad;
- Sessionzustand;
- Sync-Log;
- vollständiger `user_management`-Block;
- Dirty-State;
- Migrationsstatus.

Damit gilt auch für Benutzerverwaltungsdaten dieselbe Grundregel wie für Session-/Persistenzdaten: **erst vollständig laden und validieren, dann atomar in den Manager übernehmen**.

Commits dieses Blocks:

- `e74f149f` feat(projectos): Bundle v4 mit Benutzerverwaltung ergänzen
- `7843a06f` feat(projectos): Projektmanager auf Bundle v4 umstellen
- `f3676ef0` test(projectos): Bundle v4 und Benutzerverwaltung absichern
- `866ccdfa` test(projectos): Bundle v4 Save-As Recovery und Transaktionssicherheit absichern

## Tests / letzter bestätigter Stand

Die vollständige `ProjectOS complete test suite`, Run #212, ist für Commit `866ccdfa71bf0f97228d59dfe83bf7b8f44e733c` erfolgreich.

PR #159 bleibt der integrierte ProjectOS-Umsetzungsbranch.

## Unmittelbar nächster Umsetzungsschritt

Als Nächstes Z_Cockpit um einen read-only Persistenz-/Migrationsstatus der Benutzerverwaltung ergänzen:

1. aktuelle Bundle-Version und Persistenzversion des Benutzerblocks anzeigen;
2. `migration_pending` für v2/v3 sichtbar machen;
3. Anzahl persistierter Benutzer, Rechte, Rollen, Aktivierungen, Rückgaben, Freigaben und Nachprüfungen anzeigen;
4. deutlich markieren, dass Simulationen/Evaluator-/Z_Cockpit-/Trace-/materialisierte Wissensdaten nicht persistiert werden;
5. Recovery-Status für Benutzerverwaltung in dieselbe Projektleiteransicht aufnehmen;
6. danach Persistenzdiagnosen für fehlende/inkonsistente Referenzen als read-only Z_Cockpit-Diagnose ergänzen.

## Starttext für einen neuen Chat

> Wir setzen die Entwicklung von `kicad-din-electrical / ProjectOS` fort. Lies zuerst `docs/handover/PROJECTOS_ZWISCHENSTAND_2026-08-09.md` auf Branch `test/load-failure-preserves-state` und prüfe PR #159. Der letzte vollständig grüne Stand ist ProjectOS complete test suite Run #212. Bundle v4 ist inklusive Benutzerverwaltung für Roundtrip, Dirty-State, Save-As, Recovery und transaktionssichere Fehlerfälle abgesichert. Ein fehlgeschlagener v4-Load/Recover verändert weder Session, Sync-Log, project_id, Pfad noch user_management. Fahre mit dem read-only Z_Cockpit-Persistenz-/Migrationsstatus für Benutzerverwaltung fort. Alles auf Deutsch. Architekturregeln, Benutzergewichtung, DENY-Vorrang, Rechteherkunft und Korrelationskette nicht verlieren.
