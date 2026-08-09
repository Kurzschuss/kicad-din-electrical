# ProjectOS – Zwischenstand / Chat-Übergabe

Stand: 2026-08-09
Repository: Kurzschuss/kicad-din-electrical
Arbeitsbranch: `test/load-failure-preserves-state`
Pull Request: #159 – `Test: fehlgeschlagenes Projektladen hält Managerzustand stabil`

## Architekturgrundlagen

Architecture Freeze 1.0 bleibt maßgeblich. ProjectOS ist die Grundlage des Projekts. Weiterhin gelten Single Source of Truth, Domain Ownership, Object First, Offline First, Simulation First, Documentation First und Configuration before Code. Die drei Perspektiven Entwickler, Engineering und Projektleiter bleiben erhalten.

## Persistenz, Recovery und Projektidentität

Der Persistenz-/Recovery-Vertrag umfasst atomare Saves, transaktionssicheres Laden, explizite semantisch validierte Recovery, read-only Recovery-Status, Bundle v3 mit stabiler `project_id`, Save-As mit identischer Projektidentität und rückwärtskompatible v2→v3-Migration ohne Hintergrundschreibzugriff.

## Projektkorrelation, Bus, Audit und Projektgedächtnis

`project_id`, `correlation_id` und `causation_id` werden durch Bus, Audit, Projektgedächtnis und Z_Cockpit geführt. Vorhanden sind transportneutraler Nachrichtenumschlag, korreliertes Sync-Audit, Wissenselemente, typisierte Wissensbeziehungen, Pfad-/Herkunftserklärung, Widerspruchs-/Ablöseanalyse und Konsistenzdiagnose.

## Z_Cockpit – aktueller Stand

Vorhanden sind Projektkorrelationssicht, Projektleiter-Gesamtübersicht, priorisierter Aufmerksamkeitsblock, read-only Diagnose-Arbeitsansichten, UI-neutraler Navigationsvertrag, Resolver, Breadcrumb-/Rücksprungkontext, kontextsensitive Detailfolgeziele sowie die `approval_trace`-Freigabevorgangsansicht.

## Benutzerverwaltung und Autorisierung

Vorhanden sind Benutzerprofile mit Benutzergewichtung 0–1000, typisierte Rechteherkünfte, Scope, Risikoklasse, Gültigkeit, Delegation und read-only Rechte-Simulation. `DENY` hat Vorrang vor `ALLOW`. Benutzergewichtung ist sichtbar, ersetzt aber keine Freigabe und überstimmt kein `DENY`.

## Projektbezogene Benutzerfunktionen

Die Funktionen `project_lead`, `deputy`, `trusted_person` und `successor` sind als eigene projektbezogene Beziehungen vorhanden. Zuweisung, Aktivierung, Freigabe und Beendigung sind strikt getrennte Zustände. Aktivierung und Rückgabe werden mit Grund, Zeitraum, Scope und Auslöser geführt und sind read-only simulierbar.

## Vier-Augen-/Freigabevertrag

`low` und `medium` benötigen derzeit keine zweite Freigabe. `high` und `critical` benötigen eine zweite, vom Auslöser verschiedene Person. Selbstfreigabe zählt nicht. Externe Ablehnung blockiert die Aktion. Notfallaktionen können als `emergency_pending_review` vorläufig wirksam sein. Benutzergewichtung ersetzt keine Freigabe; `DENY` bleibt vorrangig.

`ProjectOSApprovedRoleActivationEvaluator` und `ProjectOSApprovedRoleDeactivationEvaluator` arbeiten fail-closed. Kritische Aktivierungen ohne Freigabe erzeugen keine Rollenrechte. Kritische Rückgaben ohne Freigabe beenden bestehende Aktivierungen nicht. Notfälle dürfen vorläufig wirken und bleiben nachprüfungspflichtig.

## Audit-/Bus-/Korrelationsnachweis für Freigaben

`ProjectOSRoleApprovalTrace` und `ProjectOSRoleApprovalTraceEmitter` bilden den fachlichen Freigabestatus auf Bus und Audit ab. Pro Vorgang werden `project_id`, `correlation_id` und `causation_id` durchgängig geführt. Die Buskette umfasst `approval_requested`, optional `approval_decided` und `approval_effectiveness_evaluated`. Ausstehende Freigaben erzeugen kein erfundenes Entscheidungsereignis.

## Z_Cockpit-Freigabevorgang und Aufmerksamkeit

`ZCockpitRoleApprovalTraceView` zeigt Anforderung, Entscheidungen, Wirksamkeit, Kausalkette und Audit-Nachweise. Der Navigationsvertrag kennt `approval_trace` und löst über `project_id`, `correlation_id` und `action_id` den konkreten Vorgang auf.

Der Aufmerksamkeitsblock priorisiert:

- `APPROVAL_PENDING` → gelb;
- `APPROVAL_REJECTED` → gelb;
- `APPROVAL_EMERGENCY_POST_REVIEW` → rot, Priorität 30.

## Expliziter Abschluss von Notfall-Nachprüfungen

Vorhanden sind `ProjectOSRoleEmergencyPostReview`, `ProjectOSRoleEmergencyPostReviewEvaluator` und `ZCockpitRoleEmergencyPostReviewView`.

Eine Nachprüfung referenziert die ursprüngliche `action_id` und führt `review_id`, `reviewer_user_id`, Ergebnis (`confirmed` oder `negative`), `reviewed_at`, optional Kommentar und Metadaten.

Regeln:

- offene Notfallaktion ohne Nachprüfung → `pending`;
- anfordernde Person darf nicht selbst nachprüfen;
- bestätigt → `completed_confirmed`;
- negativ → `completed_negative`, `escalation_required=true`;
- negative Nachprüfung schreibt die ursprüngliche Notfallwirkung nicht rückwirkend um;
- `historical_emergency_effect_preserved=true` bleibt erhalten;
- mehrere Nachprüfungen derselben `action_id` gelten derzeit als mehrdeutig.

## Korrelierter Nachprüfungsabschluss – zuletzt umgesetzt

Neu vorhanden sind:

- `ProjectOSRolePostReviewTrace`
- `ProjectOSRolePostReviewTraceEmitter`

Der Trace-Erweiterer verwendet den bestehenden `ProjectOSRoleEmergencyPostReviewEvaluator` als fachliche Wahrheit und hängt nur den Nachprüfungsnachweis an den bereits vorhandenen Freigabevorgang an.

Regeln:

- bestätigte Nachprüfung erzeugt `projectos.role_action.post_review_completed`;
- negative Nachprüfung erzeugt `projectos.role_action.post_review_escalated`;
- beide Ereignisse verwenden dieselbe `project_id` und `correlation_id` wie der ursprüngliche Freigabevorgang;
- `causation_id` zeigt auf den letzten bisherigen Nachweis, typischerweise `approval_effectiveness_evaluated`;
- Audit verwendet entsprechend `post_review_completed` bzw. `post_review_escalated`;
- ohne vorhandene Nachprüfung wird kein künstliches Abschlussereignis erzeugt;
- bei Eskalation bleibt `historical_emergency_effect_preserved=true` sichtbar.

Commits dieses Blocks:

- `cb1d71e7` feat(project): Notfall-Nachprüfung an Freigabekorrelation anbinden
- `6bf8680b` test(project): korrelierte Notfall-Nachprüfung absichern

## Tests / letzter bestätigter Stand

Die vollständige `ProjectOS complete test suite`, Run #191, ist für Commit `6bf8680bb3e1dae4f6c419e68307cb9b1723bfe1` erfolgreich.

PR #159 ist offen, Draft und mergebar. Der Branch ist inzwischen ein integrierter ProjectOS-Umsetzungsbranch und enthält wesentlich mehr als den ursprünglichen Persistenz-Test.

## Unmittelbar nächster Umsetzungsschritt

Als Nächstes Z_Cockpit und Projektleiterübersicht auf die abgeschlossene Nachprüfung umstellen:

1. `ZCockpitRoleApprovalTraceView` um `post_review_completed` und `post_review_escalated` erweitern;
2. bestätigte Nachprüfungen nicht mehr als offene Notfall-Nachprüfung anzeigen;
3. negative Nachprüfungen als eigene rote Eskalation beibehalten;
4. Projektleiter-Gesamtübersicht um offene, bestätigte und eskalierte Nachprüfungen ergänzen;
5. Navigation vom Aufmerksamkeitspunkt direkt auf den erweiterten Freigabe-/Nachprüfungsvorgang;
6. danach Freigabe- und Nachprüfungsdaten in Projektgedächtnis/Wissensherkunft einbinden.

## Starttext für einen neuen Chat

> Wir setzen die Entwicklung von `kicad-din-electrical / ProjectOS` fort. Lies zuerst `docs/handover/PROJECTOS_ZWISCHENSTAND_2026-08-09.md` auf Branch `test/load-failure-preserves-state` und prüfe PR #159. Der letzte vollständig grüne Stand ist ProjectOS complete test suite Run #191. Notfall-Nachprüfungen werden jetzt im selben `project_id`/`correlation_id`-Vorgang mit sauberer `causation_id` als `post_review_completed` oder `post_review_escalated` auf Bus und Audit nachgewiesen. Fahre danach mit der Z_Cockpit-Auswertung und Projektleiterübersicht für abgeschlossene bzw. eskalierte Nachprüfungen fort. Alles auf Deutsch. Architekturregeln, Benutzergewichtung, DENY-Vorrang, Rechteherkunft und Korrelationskette nicht verlieren.
