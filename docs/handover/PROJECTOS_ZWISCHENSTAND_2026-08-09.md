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

Die Funktionen `project_lead`, `deputy`, `trusted_person` und `successor` sind als eigene projektbezogene Beziehungen vorhanden. Zuweisung, Aktivierung, Freigabe und Beendigung sind getrennte Zustände.

## Aktivierung und Rückgabe

Vorhanden sind `ProjectOSProjectRoleActivation`, `ProjectOSProjectRoleActivationRegistry`, `ProjectOSProjectRoleDeactivation`, `ProjectOSProjectRoleLifecycleEvaluator`, `ZCockpitProjectRoleActivationView` und `ZCockpitProjectRoleDeactivationView`.

Eine zugewiesene Projektfunktion erzeugt erst bei einer passenden, aktuell gültigen Aktivierung Rechtewirkung. Eine Beendigung referenziert eine konkrete Aktivierung und beendet deren Rollenrechte erst ab `ended_at`. Direkte Rechte, Delegationen, Ausnahmen, Whitelist/Blacklist und DENY-Zuweisungen bleiben erhalten. Aktivierung und Rückgabe sind read-only simulierbar.

## Vier-Augen-/Freigabevertrag

Vorhanden sind `ProjectOSRoleActionApprovalRequest`, `ProjectOSRoleActionApproval`, `ProjectOSRoleActionApprovalEvaluator` und `ZCockpitRoleActionApprovalView`.

Regeln:

- `low` und `medium` benötigen derzeit keine zweite Freigabe;
- `high` und `critical` benötigen eine zweite, vom Auslöser verschiedene Person;
- Selbstfreigabe zählt nicht;
- externe Ablehnung blockiert die Aktion;
- Notfallaktionen können als `emergency_pending_review` vorläufig wirksam sein und bleiben nachprüfungspflichtig;
- Benutzergewichtung ersetzt keine Freigabe;
- DENY bleibt vorrangig.

## Freigabe in tatsächliche Aktivierungs-Rechtewirkung integriert – zuletzt umgesetzt

Neu vorhanden sind:

- `ProjectOSApprovedRoleActivationEvaluator`
- `ZCockpitApprovedRoleActivationView`

Die Integration ist fail-closed:

- eine aktive `high`/`critical`-Projektfunktion ohne passenden Freigabeauftrag erhält `approval_missing` und erzeugt keine Rollenrechte;
- ein vorhandener Freigabeauftrag ohne zweite Freigabe erhält `pending_approval` und erzeugt ebenfalls keine Rollenrechte;
- erst eine wirksame externe Freigabe erzeugt die aus der Aktivierung abgeleiteten Rollenrechte;
- `emergency_pending_review` darf vorläufig Rollenrechte erzeugen, wird aber unter `pending_post_reviews` dauerhaft als offene Nachprüfung sichtbar;
- Freigaberisikoklasse und Rollenrisikoklasse müssen übereinstimmen;
- mehrere Freigabeaufträge für dieselbe Aktivierung werden als mehrdeutig abgewiesen;
- Freigabeaufträge müssen auf eine tatsächlich vorhandene `activation_id` zeigen;
- Rechteherkunft führt `approval_status` und `post_review_required` mit;
- ein freigegebenes rollenbasiertes ALLOW kann ein explizites DENY weiterhin nicht überstimmen;
- Benutzergewichtung bleibt ohne Entscheidungswirkung.

Z_Cockpit unterscheidet dadurch ausdrücklich:

- `Freigabeauftrag fehlt`;
- `Freigabe ausstehend`;
- `Freigegeben`;
- `Keine zweite Freigabe erforderlich`;
- `Abgelehnt`;
- `Notfall vorläufig wirksam – Nachprüfung erforderlich`.

Commits dieses Blocks:

- `d68be131` feat(project): Freigabe in Aktivierungsrechte integrieren
- `6890780a` test(project): freigabegesteuerte Aktivierungsrechte absichern
- `f353055c` feat(z-cockpit): freigabegesteuerte Aktivierungswirkung anzeigen
- `ae757b88` test(z-cockpit): freigabegesteuerte Aktivierungswirkung absichern

## Tests / letzter bestätigter Stand

Die vollständige `ProjectOS complete test suite`, Run #167, ist für Commit `ae757b88d33c4d51e9a4d74f3e82b2d843187c7e` erfolgreich.

PR #159 ist offen, Draft und mergebar. Der Branch ist inzwischen ein integrierter ProjectOS-Umsetzungsbranch und enthält wesentlich mehr als den ursprünglichen Persistenz-Test.

## Unmittelbar nächster Umsetzungsschritt

Als Nächstes die Freigabe analog in **kritische Beendigungen/Rückgaben** integrieren:

1. `high`/`critical`-Beendigung ohne wirksame Freigabe darf die bestehende Aktivierungswirkung noch nicht beenden;
2. Notfall-Beendigung darf vorläufig wirken, bleibt aber nachprüfungspflichtig;
3. Z_Cockpit muss blockierte, freigegebene und notfallbedingte Rückgaben getrennt anzeigen;
4. read-only Simulation muss Vorher/Nachher unter fehlender bzw. vorhandener Freigabe vergleichen;
5. danach Freigabeentscheidungen über `project_id`, `correlation_id` und `causation_id` an Audit/Bus anbinden.

## Starttext für einen neuen Chat

> Wir setzen die Entwicklung von `kicad-din-electrical / ProjectOS` fort. Lies zuerst `docs/handover/PROJECTOS_ZWISCHENSTAND_2026-08-09.md` auf Branch `test/load-failure-preserves-state` und prüfe PR #159. Der letzte vollständig grüne Stand ist ProjectOS complete test suite Run #167. Die Vier-Augen-Freigabe ist bereits fail-closed in die tatsächliche Rechtewirksamkeit von Aktivierungen integriert. Fahre danach mit derselben Integration für kritische Beendigungen/Rückgaben fort. Alles auf Deutsch. Architekturregeln, Benutzergewichtung, DENY-Vorrang, Rechteherkunft und offene Notfallnachprüfungen nicht verlieren.
