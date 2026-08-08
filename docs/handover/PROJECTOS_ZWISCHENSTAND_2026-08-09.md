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

Runtime-Grundlagen:

- `ProjectOSUserProfile` mit stabiler `user_id`, Rollenliste und Benutzergewichtung 0–1000;
- `ProjectOSPermissionAssignment` mit Herkunftstypen `role`, `direct`, `delegation`, `deny`, `exception`, `whitelist`, `blacklist`;
- Wirkung `allow`/`deny`, Scope, Risikoklasse, Gültigkeitszeitraum, Herkunftsreferenz und optional Delegationsgeber;
- `ProjectOSAuthorizationEvaluator` liefert effektive Rechte samt Herkunft read-only;
- explizites `DENY` hat Vorrang vor `ALLOW`;
- Benutzergewichtung ist sichtbar, beeinflusst die Rechteentscheidung bewusst nicht;
- Rechte-Simulation vergleicht Baseline und hypothetischen Zustand ohne Persistenzänderung.

`ZCockpitAuthorizationView` zeigt effektive Rechte, aktive/inaktive Herkunft, deutsche Herkunfts- und Risiko-Labels, Scope, Ablauf, Delegationsgeber und Benutzergewichtung.

## Projektbezogene Benutzerfunktionen

Die Funktionen `project_lead`, `deputy`, `trusted_person` und `successor` sind als eigene projektbezogene Beziehungen vorhanden. Jede Zuordnung enthält `role_assignment_id`, `project_id`, `user_id`, `role_type`, `scope`, `valid_from`, `valid_until`, `assigned_by_user_id`, `source_reference` und `metadata`.

Zuweisung, Aktivierung und Beendigung sind strikt getrennte Zustände.

## Aktivierung und Rückgabe

Vorhanden sind `ProjectOSProjectRoleActivation`, `ProjectOSProjectRoleActivationRegistry`, `ProjectOSProjectRoleDeactivation`, `ProjectOSProjectRoleLifecycleEvaluator`, `ZCockpitProjectRoleActivationView` und `ZCockpitProjectRoleDeactivationView`.

Eine zugewiesene Projektfunktion erzeugt erst bei einer passenden, aktuell gültigen Aktivierung Rechtewirkung. Eine Beendigung referenziert eine konkrete Aktivierung und beendet deren Rollenrechte erst ab `ended_at`. Direkte Rechte, Delegationen, Ausnahmen, Whitelist/Blacklist und DENY-Zuweisungen bleiben erhalten. Aktivierung und Rückgabe sind jeweils read-only simulierbar.

## Vier-Augen-/Freigaberegeln – zuletzt umgesetzt

Neu vorhanden sind:

- `ProjectOSRoleActionApprovalRequest`
- `ProjectOSRoleActionApproval`
- `ProjectOSRoleActionApprovalEvaluator`
- `ZCockpitRoleActionApprovalView`

Der Freigabevertrag gilt einheitlich für `activation` und `deactivation`.

Regeln:

- `low` und `medium` benötigen derzeit keine zweite Freigabe;
- `high` und `critical` benötigen eine zweite, vom Auslöser verschiedene Person;
- Selbstfreigabe wird erkannt, aber nicht als Vier-Augen-Freigabe gewertet;
- eine externe Ablehnung blockiert die Aktion;
- Notfallaktionen können als `emergency_pending_review` vorläufig wirksam sein, bleiben aber ausdrücklich nachprüfungspflichtig;
- Benutzergewichtung ersetzt keine Freigabe;
- dieser Vertrag verändert keine Aktivierung, Beendigung oder Freigabe und ist vollständig read-only auswertbar.

Eine Freigabe führt `approval_id`, `action_id`, `approver_user_id`, `decision`, `decided_at` und optional Kommentar. Ein Freigabeauftrag führt unter anderem `action_id`, `project_id`, `action_type`, Zielreferenz, `requested_by_user_id`, Risikoklasse, Zeitpunkt, Scope, Emergency-Flag und Grund.

Z_Cockpit zeigt die Zustände `pending_approval`, `approved`, `approved_not_required`, `rejected` und `emergency_pending_review` mit deutschen Labels und `attention_required`.

Commits des letzten Blocks:

- `edf211d5` feat(project): Vier-Augen-Freigaben für kritische Rollenaktionen einführen
- `07db516f` test(project): Vier-Augen- und Notfallfreigaben absichern
- `716c4ccb` feat(z-cockpit): Vier-Augen- und Notfallfreigaben anzeigen
- `b14a3efa` test(z-cockpit): Freigabestatus und Notfallnachprüfung absichern

## Tests / letzter bestätigter Stand

Die vollständige `ProjectOS complete test suite`, Run #162, ist für Commit `b14a3efa48025544598ae77e081c6912ac3ab3c3` erfolgreich.

PR #159 ist offen, Draft und mergebar. Der Branch ist inzwischen ein integrierter ProjectOS-Umsetzungsbranch und enthält wesentlich mehr als den ursprünglichen Persistenz-Test.

## Unmittelbar nächster Umsetzungsschritt

Als Nächstes den Freigabestatus **wirklich in die Rechtewirksamkeit von Aktivierung und Beendigung integrieren**:

1. Aktivierungs-/Lifecycle-Evaluator bekommt optional einen Freigabestatus;
2. `high`/`critical` ohne Freigabe darf keine Rollenrechte erzeugen;
3. `emergency_pending_review` darf vorläufig wirken, muss aber im Z_Cockpit dauerhaft als offene Nachprüfung erscheinen;
4. Beendigung/Rückgabe mit kritischer Auswirkung ebenfalls Freigabestatus berücksichtigen;
5. DENY-Vorrang bleibt unverändert;
6. read-only Vorher/Nachher-Simulation muss Freigabe und fehlende Freigabe vergleichen können;
7. danach Audit/Korrelation für Freigabeentscheidungen ergänzen.

## Starttext für einen neuen Chat

> Wir setzen die Entwicklung von `kicad-din-electrical / ProjectOS` fort. Lies zuerst `docs/handover/PROJECTOS_ZWISCHENSTAND_2026-08-09.md` auf Branch `test/load-failure-preserves-state` und prüfe PR #159. Der letzte vollständig grüne Stand ist ProjectOS complete test suite Run #162. Fahre danach mit der Integration des Vier-Augen-Freigabestatus in die tatsächliche Rechtewirksamkeit von Aktivierung und Beendigung fort. Alles auf Deutsch. Architekturregeln, Benutzergewichtung, DENY-Vorrang, Rechteherkunft sowie die Trennung zwischen Zuweisung, Aktivierung, Freigabe und Beendigung nicht verlieren.
