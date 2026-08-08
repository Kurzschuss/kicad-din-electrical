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

## Explizite Projektfunktionsaktivierung

Vorhanden sind `ProjectOSProjectRoleActivation` und `ProjectOSProjectRoleActivationRegistry`.

Eine Aktivierung enthält `activation_id`, `project_id`, `role_assignment_id`, `user_id`, `reason`, `scope`, `valid_from`, `valid_until`, `triggered_by_user_id`, `trigger_reference` und `metadata`.

Unterstützte Aktivierungsgründe: `manual`, `absence`, `incapacity`, `vacation`, `emergency`, `succession`, `temporary_transfer`.

Eine vorhandene Projektfunktion ohne passende, aktuell gültige Aktivierung erzeugt keine Rechtewirkung. Nur aktivierte Projektfunktionen werden über den expliziten `permission_map` in normale `ProjectOSPermissionAssignment`s übersetzt. Abgelaufene Aktivierungen erzeugen keine Rechte. Ein ALLOW aus aktivierter Projektfunktion kann ein explizites DENY nicht überstimmen. Benutzergewichtung bleibt ohne Entscheidungswirkung.

`ZCockpitProjectRoleActivationView` zeigt aktive, nicht aktivierte und abgelaufene Zustände und simuliert Aktivierungen read-only mit Vorher/Nachher-Rechteauswirkung und DENY-Konflikten.

## Aktivierungsende / Rückgabe – zuletzt umgesetzt

Neu vorhanden sind:

- `ProjectOSProjectRoleDeactivation`
- `ProjectOSProjectRoleLifecycleEvaluator`
- `ZCockpitProjectRoleDeactivationView`

Eine Beendigung referenziert immer eine konkrete `activation_id` und enthält:

- `deactivation_id`
- `activation_id`
- `project_id`
- `user_id`
- `reason`
- `ended_at`
- `scope`
- `triggered_by_user_id`
- `trigger_reference`
- `metadata`

Unterstützte Beendigungsgründe sind derzeit `manual_return`, `principal_returned`, `period_ended`, `revoked`, `handover_completed`, `emergency_ended` und `succession_completed`.

Zentrale Regel: Eine Beendigung entzieht die aus der betreffenden Aktivierung abgeleiteten Rollenrechte erst ab `ended_at`. Direkte Rechte, Delegationen, Ausnahmen, Whitelist/Blacklist und DENY-Zuweisungen bleiben davon unberührt.

`ProjectOSProjectRoleLifecycleEvaluator` führt Aktivierung und Beendigung zusammen und liefert `effective_roles`, `effective_activations`, `ended_activations` und `assigned_not_effective_roles` read-only.

`ZCockpitProjectRoleDeactivationView.simulate_deactivation()` simuliert die Rückgabe vor tatsächlicher Zustandsänderung. Es zeigt:

- Vorher-/Nachher-Rechte;
- verlorene rollenbasierte Rechte;
- weiterhin erlaubte direkte Rechte;
- weiterhin geltende DENYs;
- Beendigungsgrund mit deutschem Label;
- Anzahl geänderter und verlorener Rechte.

Commits des letzten Blocks:

- `186d3a75` feat(project): Aktivierungsende und Rückgabe von Projektfunktionen modellieren
- `8871b6c4` test(project): Aktivierungsende und Rückgabe absichern
- `84612343` feat(z-cockpit): Rückgabe aktivierter Projektfunktionen simulieren
- `e2c18f6b` test(z-cockpit): Rückgabe-Simulation und verbleibende Rechte absichern

## Tests / letzter bestätigter Stand

Die vollständige `ProjectOS complete test suite`, Run #157, ist für Commit `e2c18f6b0153a406944b8acc0e0745c6f30d934f` erfolgreich.

PR #159 ist offen, Draft und mergebar. Der Branch ist inzwischen ein integrierter ProjectOS-Umsetzungsbranch und enthält wesentlich mehr als den ursprünglichen Persistenz-Test.

## Unmittelbar nächster Umsetzungsschritt

Als Nächstes **Freigabe-/Vier-Augen-Regeln für kritische Aktivierungen und Beendigungen** modellieren:

1. Risikoklasse der betroffenen Rechte berücksichtigen;
2. für `high`/`critical` Aktivierungen optional oder verpflichtend eine zweite Freigabe verlangen;
3. Freigabe mit approver, Zeitpunkt, Scope, Grund und Referenz protokollieren;
4. Notfallaktivierung ausdrücklich kennzeichnen und nachträgliche Prüfung ermöglichen;
5. Aktivierung/Beendigung ohne erforderliche Freigabe darf keine Rechtewirkung erzeugen;
6. Freigabe-Simulation read-only in Z_Cockpit darstellen;
7. Benutzergewichtung darf auch hier keine fehlende Freigabe ersetzen und DENY bleibt vorrangig.

## Starttext für einen neuen Chat

> Wir setzen die Entwicklung von `kicad-din-electrical / ProjectOS` fort. Lies zuerst `docs/handover/PROJECTOS_ZWISCHENSTAND_2026-08-09.md` auf Branch `test/load-failure-preserves-state` und prüfe PR #159. Der letzte vollständig grüne Stand ist ProjectOS complete test suite Run #157. Fahre danach mit Freigabe-/Vier-Augen-Regeln für kritische Aktivierungen und Beendigungen fort. Alles auf Deutsch. Architekturregeln, Benutzergewichtung, DENY-Vorrang, Rechteherkunft sowie die strikte Trennung zwischen Zuweisung, Aktivierung und Beendigung nicht verlieren.
