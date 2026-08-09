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

Vorhanden sind Projektkorrelationssicht, Projektleiter-Gesamtübersicht, priorisierter Aufmerksamkeitsblock, read-only Diagnose-Arbeitsansichten, UI-neutraler Navigationsvertrag, Resolver, Breadcrumb-/Rücksprungkontext sowie kontextsensitive Detailfolgeziele.

## Benutzerverwaltung und Autorisierung

Vorhanden sind Benutzerprofile mit Benutzergewichtung 0–1000, typisierte Rechteherkünfte, Scope, Risikoklasse, Gültigkeit, Delegation und read-only Rechte-Simulation. `DENY` hat Vorrang vor `ALLOW`. Benutzergewichtung ist sichtbar, ersetzt aber keine Freigabe und überstimmt kein `DENY`.

## Projektbezogene Benutzerfunktionen

Die Funktionen `project_lead`, `deputy`, `trusted_person` und `successor` sind als eigene projektbezogene Beziehungen vorhanden. Zuweisung, Aktivierung, Freigabe und Beendigung sind strikt getrennte Zustände. Aktivierung und Rückgabe werden mit Grund, Zeitraum, Scope und Auslöser geführt und sind read-only simulierbar.

## Vier-Augen-/Freigabevertrag

Vorhanden sind `ProjectOSRoleActionApprovalRequest`, `ProjectOSRoleActionApproval`, `ProjectOSRoleActionApprovalEvaluator` und die zugehörigen Z_Cockpit-Sichten.

Regeln:

- `low` und `medium` benötigen derzeit keine zweite Freigabe;
- `high` und `critical` benötigen eine zweite, vom Auslöser verschiedene Person;
- Selbstfreigabe zählt nicht;
- externe Ablehnung blockiert die Aktion;
- Notfallaktionen können als `emergency_pending_review` vorläufig wirksam sein und bleiben nachprüfungspflichtig;
- Benutzergewichtung ersetzt keine Freigabe;
- DENY bleibt vorrangig.

## Freigabe in Aktivierung und Rückgabe integriert

`ProjectOSApprovedRoleActivationEvaluator` und `ProjectOSApprovedRoleDeactivationEvaluator` arbeiten fail-closed. Kritische Aktivierungen ohne wirksame Freigabe erzeugen keine Rollenrechte. Kritische Rückgaben ohne wirksame Freigabe beenden eine bestehende Aktivierung nicht. Notfallaktionen dürfen vorläufig wirken, bleiben aber unter `pending_post_reviews` offen.

## Audit-/Bus-/Korrelationsnachweis für Freigaben

`ProjectOSRoleApprovalTrace` und `ProjectOSRoleApprovalTraceEmitter` bilden den bestehenden fachlichen Freigabestatus nachvollziehbar auf Bus und Audit ab. Pro Vorgang werden `project_id`, `correlation_id` und `causation_id` durchgängig geführt.

Buskette:

1. `projectos.role_action.approval_requested`
2. optional `projectos.role_action.approval_decided`
3. `projectos.role_action.approval_effectiveness_evaluated`

Parallel entstehen die Audit-Aktionen `approval_requested`, `approval_decided` und `approval_effectiveness_evaluated`. Ausstehende Freigaben erzeugen kein erfundenes Entscheidungsereignis.

## Z_Cockpit-Freigabevorgangsansicht – zuletzt umgesetzt

Neu vorhanden ist `ZCockpitRoleApprovalTraceView`.

Die read-only Sicht filtert strikt nach `project_id`, `correlation_id` und `action_id` und zeigt:

- Freigabeanforderung;
- vorhandene Freigabe-/Ablehnungsentscheidungen;
- Wirksamkeitsstatus;
- komplette zeitliche Kausalkette mit `message_id` und `causation_id`;
- zugehörige Audit-Einträge;
- offenen Notfall-Nachprüfungsstatus.

Der Navigationsvertrag kennt jetzt `approval_trace`. Ein solches Ziel verlangt `correlation_id` und `action_id`; der `ZCockpitNavigationResolver` löst das Ziel direkt aus den aktuellen Bus-/Audit-Nachweisen des Projekts auf.

Der `ZCockpitAttentionView` kann zusätzlich vorhandene Freigabetraces berücksichtigen:

- `APPROVAL_PENDING` → gelb, direkte Navigation zum Freigabevorgang;
- `APPROVAL_REJECTED` → gelb, Klärungsbedarf;
- `APPROVAL_EMERGENCY_POST_REVIEW` → rot, Priorität 30, offene Nachprüfung.

Eine offene Notfall-Nachprüfung hebt die Aufmerksamkeitsampel auf Rot. Die Sicht bleibt vollständig read-only.

Commits dieses Blocks:

- `101fed18` feat(z-cockpit): Freigabevorgang als korrelierte Detailansicht darstellen
- `10687d17` test(z-cockpit): korrelierte Freigabevorgangsansicht absichern
- `a50cb828` feat(z-cockpit): Freigabevorgang als Navigationsziel ergänzen
- `50bf3aa2` feat(z-cockpit): Freigabevorgang über Navigation auflösen
- `514948c7` test(z-cockpit): Navigation zum Freigabevorgang absichern
- `cf96e979` feat(z-cockpit): offene Freigaben im Aufmerksamkeitsblock priorisieren
- `65d25858` test(z-cockpit): offene Freigaben im Aufmerksamkeitsblock absichern

## Tests / letzter bestätigter Stand

Die vollständige `ProjectOS complete test suite`, Run #183, ist für Commit `65d258587dad21d6f6515ac341ab9513015404f2` erfolgreich.

PR #159 ist offen, Draft und mergebar. Der Branch ist inzwischen ein integrierter ProjectOS-Umsetzungsbranch und enthält wesentlich mehr als den ursprünglichen Persistenz-Test.

## Unmittelbar nächster Umsetzungsschritt

Als Nächstes den **tatsächlichen Abschluss einer Notfall-Nachprüfung** modellieren und korrelieren:

1. Nachprüfung als eigener fachlicher Zustand mit Prüfer, Zeitpunkt, Ergebnis und Kommentar;
2. Abschluss muss auf die ursprüngliche `action_id`/`correlation_id` verweisen;
3. Bus-/Audit-Ereignis für `post_review_completed` erzeugen;
4. offene `emergency_pending_review`-Einträge nach gültiger Nachprüfung nicht mehr als offen anzeigen;
5. negative Nachprüfung ausdrücklich als Eskalation markieren, nicht stillschweigend rückwirkend umdeuten;
6. Projektleiter-Gesamtübersicht um offene/abgeschlossene Notfall-Nachprüfungen erweitern;
7. danach Freigabe-/Nachprüfungsdaten in Projektgedächtnis/Wissensherkunft einbinden.

## Starttext für einen neuen Chat

> Wir setzen die Entwicklung von `kicad-din-electrical / ProjectOS` fort. Lies zuerst `docs/handover/PROJECTOS_ZWISCHENSTAND_2026-08-09.md` auf Branch `test/load-failure-preserves-state` und prüfe PR #159. Der letzte vollständig grüne Stand ist ProjectOS complete test suite Run #183. Vier-Augen-Freigaben sind fail-closed in Aktivierung und Rückgabe integriert. Freigabeanforderung, Entscheidung und Wirksamkeit werden korreliert auf Bus/Audit nachgewiesen; Z_Cockpit besitzt eine `approval_trace`-Detailansicht und priorisiert offene Freigaben sowie Notfall-Nachprüfungen. Fahre mit dem expliziten Abschluss von Notfall-Nachprüfungen fort. Alles auf Deutsch. Architekturregeln, Benutzergewichtung, DENY-Vorrang, Rechteherkunft und Korrelationskette nicht verlieren.
