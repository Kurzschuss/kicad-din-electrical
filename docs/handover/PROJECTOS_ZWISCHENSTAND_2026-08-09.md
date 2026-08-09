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

## Freigabe in kritische Rückgabe/Beendigung integriert – zuletzt umgesetzt

Neu vorhanden sind:

- `ProjectOSApprovedRoleDeactivationEvaluator`
- `ZCockpitRoleDeactivationApprovalView`

Die Rückgabe ist ebenfalls fail-closed:

- `high`/`critical`-Beendigung ohne Freigabeauftrag wird unter `approval_missing` blockiert; die zugrunde liegende Aktivierung bleibt wirksam;
- eine ausstehende oder abgelehnte Freigabe beendet die Aktivierung nicht;
- erst eine wirksame externe Freigabe macht die Beendigung wirksam und entzieht die daraus abgeleiteten Rollenrechte;
- eine Notfall-Beendigung darf vorläufig wirken, wird aber unter `pending_post_reviews` als offene Nachprüfung geführt;
- Freigabeauftrag und Beendigung werden eindeutig über `deactivation:<deactivation_id>` verknüpft;
- doppelte Freigabeaufträge für dieselbe Beendigung sowie unbekannte Beendigungsreferenzen werden abgewiesen;
- Risikoklasse von Rückgabe und Freigabeauftrag muss übereinstimmen;
- Z_Cockpit zeigt blockierte, freigegebene und Notfall-Rückgaben getrennt und read-only an.

Commits dieses Blocks:

- `69c58b71` feat(project): Freigabe in kritische Rollenrückgabe integrieren
- `ce6717e8` test(project): freigabegesteuerte Rollenrückgabe absichern
- `73f12841` feat(z-cockpit): freigabegesteuerte Rollenrückgabe anzeigen
- `ce3655a5` test(z-cockpit): freigabegesteuerte Rollenrückgabe absichern

## Tests / letzter bestätigter Stand

Die vollständige `ProjectOS complete test suite`, Run #172, ist für Commit `ce3655a58415e85cafebc0a33c4fe90679e8c922` erfolgreich.

PR #159 ist offen, Draft und mergebar. Der Branch ist inzwischen ein integrierter ProjectOS-Umsetzungsbranch und enthält wesentlich mehr als den ursprünglichen Persistenz-Test.

## Unmittelbar nächster Umsetzungsschritt

Als Nächstes Freigabeentscheidungen an Audit/Bus/Korrelation anbinden:

1. Freigabeauftrag, Freigabe, Ablehnung und Notfall-Nachprüfung mit `project_id`, `correlation_id` und `causation_id` versehen;
2. Audit-Einträge für Anforderung und Entscheidung erzeugen;
3. Z_Cockpit soll vom Aufmerksamkeitspunkt direkt zum Freigabevorgang navigieren können;
4. Aktivierung/Rückgabe und deren Freigabe im selben Korrelationsvorgang erklären;
5. read-only Nachweis „wer hat wann was ausgelöst/freigegeben/abgelehnt?“ bereitstellen;
6. offene Notfall-Nachprüfungen in die Projektleiter-Gesamtübersicht integrieren.

## Starttext für einen neuen Chat

> Wir setzen die Entwicklung von `kicad-din-electrical / ProjectOS` fort. Lies zuerst `docs/handover/PROJECTOS_ZWISCHENSTAND_2026-08-09.md` auf Branch `test/load-failure-preserves-state` und prüfe PR #159. Der letzte vollständig grüne Stand ist ProjectOS complete test suite Run #172. Die Vier-Augen-Freigabe ist fail-closed in Aktivierungen und kritische Beendigungen/Rückgaben integriert. Fahre danach mit Audit/Bus/Korrelation für Freigabeentscheidungen und offenen Notfall-Nachprüfungen fort. Alles auf Deutsch. Architekturregeln, Benutzergewichtung, DENY-Vorrang, Rechteherkunft und offene Notfallnachprüfungen nicht verlieren.
