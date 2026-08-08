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

Vorhanden sind Projektkorrelationssicht, Projektleiter-Gesamtübersicht, priorisierter Aufmerksamkeitsblock, read-only Diagnose-Arbeitsansichten, ein UI-neutraler Navigationsvertrag, Resolver, Breadcrumb-/Rücksprungkontext sowie kontextsensitive Detailfolgeziele.

## Benutzerverwaltung und Autorisierung

Runtime-Grundlagen sind vorhanden:

- `ProjectOSUserProfile` mit stabiler `user_id`, Rollenliste und Benutzergewichtung 0–1000;
- `ProjectOSPermissionAssignment` mit Herkunftstypen `role`, `direct`, `delegation`, `deny`, `exception`, `whitelist`, `blacklist`;
- Rechtezuweisungen führen Wirkung (`allow`/`deny`), Scope, Risikoklasse, Gültigkeitszeitraum, Herkunftsreferenz und optional Delegationsgeber;
- `ProjectOSAuthorizationEvaluator` liefert effektive Rechte samt Herkunft read-only;
- explizites `DENY` hat Vorrang vor `ALLOW`;
- Benutzergewichtung ist sichtbar, beeinflusst die Rechteentscheidung bewusst nicht;
- Rechte-Simulation vergleicht Baseline und hypothetischen Zustand ohne Persistenzänderung.

`ZCockpitAuthorizationView` zeigt effektive Rechte, aktive/inaktive Herkunft, deutsche Herkunfts- und Risiko-Labels, Scope, Ablauf, Delegationsgeber und Benutzergewichtung.

## Projektbezogene Benutzerfunktionen

Die Funktionen `project_lead`, `deputy`, `trusted_person` und `successor` sind als eigene projektbezogene Beziehungen vorhanden. Jede Zuordnung enthält `role_assignment_id`, `project_id`, `user_id`, `role_type`, `scope`, `valid_from`, `valid_until`, `assigned_by_user_id`, `source_reference` und `metadata`.

Die reine Zuweisung einer Projektfunktion ist ausdrücklich von ihrer tatsächlichen Aktivierung getrennt.

## Explizite Projektfunktionsaktivierung

Vorhanden sind `ProjectOSProjectRoleActivation` und `ProjectOSProjectRoleActivationRegistry`.

Eine Aktivierung enthält `activation_id`, `project_id`, `role_assignment_id`, `user_id`, `reason`, `scope`, `valid_from`, `valid_until`, `triggered_by_user_id`, `trigger_reference` und `metadata`.

Unterstützte Aktivierungsgründe: `manual`, `absence`, `incapacity`, `vacation`, `emergency`, `succession`, `temporary_transfer`.

Zentrale Regel: Eine vorhandene Projektfunktion ohne passende, aktuell gültige Aktivierung erzeugt keine Rechtewirkung. Solche Rollen erscheinen unter `assigned_not_activated_roles`. Nur aktivierte Projektfunktionen werden über den expliziten `permission_map` in normale `ProjectOSPermissionAssignment`s übersetzt. Herkunft enthält zusätzlich `activation_id`, `activation_reason`, `triggered_by_user_id` und `trigger_reference`.

Abgelaufene Aktivierungen erzeugen keine Rechte. Projekt-/Scope-/Benutzerbezug bleibt strikt. Ein aus aktivierter Funktion abgeleitetes ALLOW kann ein explizites DENY weiterhin nicht überstimmen. Benutzergewichtung bleibt ohne Entscheidungswirkung.

## Z_Cockpit-Benutzersicht und Funktionswechsel

`ZCockpitUserProjectRoleView` führt Projektfunktionen, Zuweisungsherkunft, Scope, Gültigkeit, Benutzergewichtung, daraus abgeleitete Rechte und effektive Rechteherkunft zusammen.

`ProjectOSProjectRoleTransitionSimulator` unterstützt read-only Funktionswechsel. `ZCockpitProjectRoleTransitionView` zeigt aktuelle/hypothetische Funktionen, Rechtezugewinn/-verlust, DENY-Konflikte, Risikoklassen und höchste betroffene Risikoklasse.

## Z_Cockpit-Aktivierungssicht – zuletzt umgesetzt

Neu vorhanden ist `ZCockpitProjectRoleActivationView`.

Die Sicht zeigt:

- aktuell aktivierte Projektfunktionen mit deutscher Funktionsbezeichnung;
- zugewiesene, aber nicht aktivierte Projektfunktionen;
- inaktive/abgelaufene Rollen und Aktivierungen;
- Aktivierungsgrund mit deutschem Label;
- Trigger, Zeitraum und Scope über die vorhandenen Aktivierungsdaten;
- Rechte, die aus aktuell aktivierten Funktionen entstehen;
- Rechteherkunft inklusive Aktivierungs-ID und Aktivierungsgrund.

`simulate_activation()` simuliert eine hypothetische Aktivierung vollständig read-only. Die Ausgabe enthält Baseline und simulierten Zustand, Permission-Auswirkungen, `decision_changed`, `became_allowed`, `became_denied` und `deny_conflict`. Ein vorhandenes DENY bleibt auch bei simuliert aktivierter Projektfunktion wirksam. Der Baseline-Zustand wird nicht verändert.

Commits des letzten Blocks:

- `e0e48878` feat(z-cockpit): Projektfunktionsaktivierung und Simulation anzeigen
- `41aa6073` fix(z-cockpit): Aktivierungssicht an Registry-Vertrag anbinden
- `c666f01e` test(z-cockpit): Aktivierungssicht und Simulation absichern

## Tests / letzter bestätigter Stand

Die vollständige `ProjectOS complete test suite`, Run #152, ist für Commit `c666f01e9f5e0a4fd643d31c0177f0230b3f72ee` erfolgreich.

PR #159 ist offen, Draft und mergebar. Der Branch ist inzwischen ein integrierter ProjectOS-Umsetzungsbranch und enthält wesentlich mehr als den ursprünglichen Persistenz-Test.

## Unmittelbar nächster Umsetzungsschritt

Als Nächstes das **Aktivierungsende / die Rückgabe einer Projektfunktion** explizit modellieren und simulieren:

1. aktive Aktivierung gezielt beenden bzw. Rückgabe abbilden;
2. Beendigungsgrund, Zeitpunkt, Scope und auslösenden Benutzer/Systemgrund führen;
3. Rechteverlust vor tatsächlicher Beendigung read-only simulieren;
4. Rückgabe der Stellvertretung an den Projektleiter nachvollziehbar darstellen;
5. Nachfolgeaktivierung und spätere Rücknahme strikt trennen;
6. Z_Cockpit soll Vorher/Nachher, entfallende Rechte, weiterhin bestehende direkte Rechte und DENY-Zustände zeigen;
7. danach Vier-Augen-/Freigaberegeln für kritische Aktivierungen definieren.

## Starttext für einen neuen Chat

> Wir setzen die Entwicklung von `kicad-din-electrical / ProjectOS` fort. Lies zuerst `docs/handover/PROJECTOS_ZWISCHENSTAND_2026-08-09.md` auf Branch `test/load-failure-preserves-state` und prüfe PR #159. Der letzte vollständig grüne Stand ist ProjectOS complete test suite Run #152. Fahre danach mit Aktivierungsende/Rückgabe einer Projektfunktion und deren read-only Rechte-Simulation fort. Alles auf Deutsch. Architekturregeln, Benutzergewichtung, DENY-Vorrang, Rechteherkunft sowie die strikte Trennung zwischen Zuweisung, Aktivierung und Beendigung nicht verlieren.
