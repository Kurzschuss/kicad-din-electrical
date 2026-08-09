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

## Expliziter Abschluss von Notfall-Nachprüfungen – zuletzt umgesetzt

Neu vorhanden sind:

- `ProjectOSRoleEmergencyPostReview`
- `ProjectOSRoleEmergencyPostReviewEvaluator`
- `ZCockpitRoleEmergencyPostReviewView`

Eine Nachprüfung referenziert die ursprüngliche `action_id` und führt `review_id`, `reviewer_user_id`, Ergebnis (`confirmed` oder `negative`), `reviewed_at`, optional Kommentar und Metadaten.

Regeln:

- eine offene `emergency_pending_review`-Aktion ohne Nachprüfung bleibt `pending`;
- die anfordernde Person darf die eigene Notfallaktion nicht selbst nachprüfen;
- bestätigte Nachprüfung → `completed_confirmed`, Nachprüfung geschlossen;
- negative Nachprüfung → `completed_negative`, `escalation_required=true`;
- eine negative Nachprüfung schreibt die ursprüngliche Notfallwirkung nicht rückwirkend um;
- historische Notfallwirkung bleibt ausdrücklich mit `historical_emergency_effect_preserved=true` erhalten;
- mehrere Nachprüfungen derselben `action_id` werden derzeit als mehrdeutig abgewiesen;
- Nachprüfungen sind nur zulässig, solange der Freigabestatus tatsächlich `emergency_pending_review` ist.

Z_Cockpit zeigt offene und negative Nachprüfungen rot. Eine bestätigte Nachprüfung wird grün und benötigt keine weitere Aufmerksamkeit.

Commits dieses Blocks:

- `b5d477db` feat(project): Notfall-Nachprüfung als eigenen Lifecycle-Schritt modellieren
- `3679407b` test(project): Notfall-Nachprüfung und Eskalation absichern
- `20a46c6b` feat(z-cockpit): Notfall-Nachprüfung und Eskalation anzeigen
- `cf6b185c` test(z-cockpit): Notfall-Nachprüfung und Eskalationssicht absichern

## Tests / letzter bestätigter Stand

Die vollständige `ProjectOS complete test suite`, Run #188, ist für Commit `cf6b185cf10474411e533135ea037b473f20d57e` erfolgreich.

PR #159 ist offen, Draft und mergebar. Der Branch ist inzwischen ein integrierter ProjectOS-Umsetzungsbranch und enthält wesentlich mehr als den ursprünglichen Persistenz-Test.

## Unmittelbar nächster Umsetzungsschritt

Als Nächstes die Nachprüfung selbst in die bestehende Korrelations-/Auditkette integrieren:

1. `post_review_completed` bzw. `post_review_escalated` als Bus-/Audit-Ereignis erzeugen;
2. dieselbe `project_id`/`correlation_id` wie der ursprüngliche Freigabevorgang verwenden;
3. `causation_id` auf den bisherigen Wirksamkeits-/Notfallnachweis beziehen;
4. `ZCockpitRoleApprovalTraceView` um Nachprüfungsabschluss erweitern;
5. `ZCockpitAttentionView` soll bestätigte Nachprüfungen nicht mehr als offen führen, negative Nachprüfungen aber als Eskalation rot beibehalten;
6. Projektleiter-Gesamtübersicht um offene, bestätigte und eskalierte Notfall-Nachprüfungen erweitern;
7. danach Freigabe-/Nachprüfungsdaten in Projektgedächtnis und Wissensherkunft einbinden.

## Starttext für einen neuen Chat

> Wir setzen die Entwicklung von `kicad-din-electrical / ProjectOS` fort. Lies zuerst `docs/handover/PROJECTOS_ZWISCHENSTAND_2026-08-09.md` auf Branch `test/load-failure-preserves-state` und prüfe PR #159. Der letzte vollständig grüne Stand ist ProjectOS complete test suite Run #188. Der explizite Abschluss von Notfall-Nachprüfungen ist bereits modelliert; bestätigte Nachprüfungen schließen die Aufmerksamkeit, negative erzeugen eine Eskalation und schreiben die historische Notfallwirkung nicht rückwirkend um. Fahre danach mit der Korrelations-/Auditintegration von `post_review_completed`/`post_review_escalated` fort. Alles auf Deutsch. Architekturregeln, Benutzergewichtung, DENY-Vorrang, Rechteherkunft und Korrelationskette nicht verlieren.
