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

Die Funktionen `project_lead`, `deputy`, `trusted_person` und `successor` sind als eigene projektbezogene Beziehungen vorhanden. Zuweisung, Aktivierung, Freigabe und Beendigung sind strikt getrennte Zustände.

Aktivierung und Rückgabe werden mit Grund, Zeitraum, Scope und Auslöser geführt. Beide Richtungen sind read-only simulierbar. Direkte Rechte, Delegationen, Ausnahmen, Whitelist/Blacklist und DENY-Zuweisungen bleiben von einer Rückgabe unberührt.

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

## Freigabe in Aktivierungsrechte integriert

`ProjectOSApprovedRoleActivationEvaluator` arbeitet fail-closed:

- `high`/`critical` ohne Freigabeauftrag → `approval_missing`, keine Rollenrechte;
- Freigabe ausstehend → keine Rollenrechte;
- gültige zweite Freigabe → Rollenrechte können wirksam werden;
- Notfall → vorläufig wirksam, `pending_post_reviews` bleibt offen;
- Rechteherkunft führt `approval_status` und `post_review_required` mit.

## Freigabe in kritische Rückgabe/Beendigung integriert

`ProjectOSApprovedRoleDeactivationEvaluator` arbeitet ebenfalls fail-closed:

- `high`/`critical`-Beendigung ohne Freigabeauftrag bleibt blockiert; die zugrunde liegende Aktivierung bleibt wirksam;
- eine ausstehende oder abgelehnte Freigabe beendet die Aktivierung nicht;
- erst eine wirksame externe Freigabe macht die Beendigung wirksam und entzieht die daraus abgeleiteten Rollenrechte;
- eine Notfall-Beendigung darf vorläufig wirken, wird aber unter `pending_post_reviews` als offene Nachprüfung geführt;
- Z_Cockpit zeigt blockierte, freigegebene und Notfall-Rückgaben getrennt und read-only an.

## Audit-/Bus-/Korrelationsnachweis für Freigaben – zuletzt umgesetzt

Neu vorhanden sind:

- `ProjectOSRoleApprovalTrace`
- `ProjectOSRoleApprovalTraceEmitter`

Der Trace-Dienst erzeugt **keine eigene Freigabeentscheidung**. Er verwendet den bestehenden `ProjectOSRoleActionApprovalEvaluator` als fachliche Wahrheit und bildet dessen Ergebnis nachvollziehbar auf Bus und Audit ab.

Pro Freigabevorgang entsteht eine gemeinsame `correlation_id`. Die Buskette lautet:

1. `projectos.role_action.approval_requested`
2. optional eine oder mehrere `projectos.role_action.approval_decided`
3. `projectos.role_action.approval_effectiveness_evaluated`

Die Nachrichten verwenden denselben `project_id`/`correlation_id`-Kontext. Folgeereignisse referenzieren über `causation_id` die auslösende Vorgängernachricht. Fremde Freigaben mit anderer `action_id` werden nicht in den Vorgang aufgenommen.

Parallel erzeugt der Dienst Audit-Einträge für:

- `approval_requested`
- `approval_decided`
- `approval_effectiveness_evaluated`

Diese Audit-Einträge tragen ebenfalls `project_id`, `correlation_id` und `causation_id`. Ausstehende Freigaben erzeugen ausdrücklich **kein erfundenes Entscheidungsereignis**. Notfallzustände behalten `emergency_pending_review` und `post_review_required` im Wirksamkeitsnachweis.

Commits dieses Blocks:

- `167357f3` feat(project): Freigaben an Audit und Bus korrelieren
- `08e53f89` test(project): korrelierte Freigabespuren absichern

## Tests / letzter bestätigter Stand

Die vollständige `ProjectOS complete test suite`, Run #175, ist für Commit `08e53f895d35adba8eacf21d68c448b211a4aa1e` erfolgreich.

PR #159 ist offen, Draft und mergebar. Der Branch ist inzwischen ein integrierter ProjectOS-Umsetzungsbranch und enthält wesentlich mehr als den ursprünglichen Persistenz-Test.

## Unmittelbar nächster Umsetzungsschritt

Als Nächstes die korrelierten Freigabevorgänge in Z_Cockpit nutzbar machen:

1. Freigabevorgang als eigene read-only Detailansicht aus Bus/Audit aufbereiten;
2. „wer hat wann angefordert/freigegeben/abgelehnt?“ samt Kausalkette anzeigen;
3. Navigation vom Aufmerksamkeitspunkt direkt zum Freigabevorgang ergänzen;
4. Aktivierung/Rückgabe und Freigabe im selben Vorgang verknüpfen;
5. offene Notfall-Nachprüfungen in die Projektleiter-Gesamtübersicht und den Aufmerksamkeitsblock integrieren;
6. danach Korrelations-/Audit-Vertrag für tatsächliche Nachprüfung und Abschluss einer Notfallfreigabe erweitern.

## Starttext für einen neuen Chat

> Wir setzen die Entwicklung von `kicad-din-electrical / ProjectOS` fort. Lies zuerst `docs/handover/PROJECTOS_ZWISCHENSTAND_2026-08-09.md` auf Branch `test/load-failure-preserves-state` und prüfe PR #159. Der letzte vollständig grüne Stand ist ProjectOS complete test suite Run #175. Vier-Augen-Freigaben sind fail-closed in Aktivierungen und kritische Rückgaben integriert; Freigabeanforderung, Entscheidung und Wirksamkeit werden inzwischen mit `project_id`, `correlation_id` und `causation_id` auf Bus und Audit nachgewiesen. Fahre danach mit der Z_Cockpit-Freigabevorgangsansicht und offenen Notfall-Nachprüfungen fort. Alles auf Deutsch. Architekturregeln, Benutzergewichtung, DENY-Vorrang, Rechteherkunft und offene Notfallnachprüfungen nicht verlieren.
