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
- Benutzergewichtung ist sichtbar, beeinflusst die Rechteentscheidung derzeit bewusst nicht;
- Rechte-Simulation vergleicht Baseline und hypothetischen Zustand ohne Persistenzänderung.

`ZCockpitAuthorizationView` zeigt effektive Rechte, aktive/inaktive Herkunft, deutsche Herkunfts- und Risiko-Labels, Scope, Ablauf, Delegationsgeber und Benutzergewichtung. Simulationen liefern Vorher/Nachher und Impact.

## Projektbezogene Benutzerfunktionen

Die Funktionen `project_lead`, `deputy`, `trusted_person` und `successor` sind als eigene projektbezogene Beziehungen vorhanden.

Jede Zuordnung enthält `role_assignment_id`, `project_id`, `user_id`, `role_type`, `scope`, `valid_from`, `valid_until`, `assigned_by_user_id`, `source_reference` und `metadata`.

Die reine Zuweisung einer Projektfunktion ist jetzt ausdrücklich von ihrer tatsächlichen Aktivierung getrennt.

## Explizite Projektfunktionsaktivierung

Neu vorhanden sind `ProjectOSProjectRoleActivation` und `ProjectOSProjectRoleActivationRegistry`.

Eine Aktivierung enthält:

- `activation_id`
- `project_id`
- `role_assignment_id`
- `user_id`
- `reason`
- `scope`
- `valid_from`
- `valid_until`
- `triggered_by_user_id`
- `trigger_reference`
- `metadata`

Unterstützte Aktivierungsgründe sind derzeit `manual`, `absence`, `incapacity`, `vacation`, `emergency`, `succession` und `temporary_transfer`.

Zentrale Regel: Eine vorhandene Projektfunktion ohne passende, aktuell gültige Aktivierung erzeugt keine Rechtewirkung. Solche Rollen werden explizit unter `assigned_not_activated_roles` ausgewiesen.

Nur aktivierte Projektfunktionen werden über den bekannten `permission_map` in normale `ProjectOSPermissionAssignment`s übersetzt. Die Rechteherkunft enthält zusätzlich `activation_id`, `activation_reason`, `triggered_by_user_id` und `trigger_reference`.

Abgelaufene Aktivierungen erzeugen keine Rechte. Aktivierungen müssen auf eine existierende Rollenbeziehung verweisen. Projekt-/Scope-/Benutzerbezug bleibt strikt. Ein aus aktivierter Funktion abgeleitetes ALLOW kann ein explizites DENY weiterhin nicht überstimmen. Benutzergewichtung bleibt ohne Entscheidungswirkung.

## Z_Cockpit-Benutzersicht und Funktionswechsel

`ZCockpitUserProjectRoleView` führt aktive und abgelaufene Projektfunktionen, deutsche Funktionsbezeichnungen, Zuweisungsherkunft, Scope, Gültigkeit, Benutzergewichtung, daraus abgeleitete Rechte und effektive Rechteherkunft zusammen.

`ProjectOSProjectRoleTransitionSimulator` unterstützt read-only Funktionswechsel. `ZCockpitProjectRoleTransitionView` bereitet diese für Projektleiter verständlich auf und zeigt Rechtezugewinn/-verlust, DENY-Konflikte, Risikoklassen und höchste betroffene Risikoklasse.

## Tests / letzter bestätigter Stand

Die vollständige `ProjectOS complete test suite`, Run #148, ist für Commit `f129804cb3bbbe9a59db5d7dbe8c77431318df42` erfolgreich.

PR #159 ist offen, Draft und mergebar. Der Branch ist inzwischen ein integrierter ProjectOS-Umsetzungsbranch und enthält wesentlich mehr als den ursprünglichen Persistenz-Test.

## Unmittelbar nächster Umsetzungsschritt

Als Nächstes die **Aktivierung selbst simulierbar und in Z_Cockpit sichtbar** machen:

1. aktuelle Zuweisung vs. aktuelle Aktivierung nebeneinander darstellen;
2. hypothetische Aktivierung vor Wirksamwerden simulieren;
3. Rechteauswirkungen der Aktivierung pro Permission zeigen;
4. Aktivierungsgrund, Trigger, Zeitraum und Scope in Z_Cockpit erklären;
5. Aktivierungsende bzw. Rückgabe der Funktion simulierbar machen;
6. später explizite Regeln für Vier-Augen-Freigabe, Notfallaktivierung und Nachfolgeauslösung ergänzen;
7. keine automatische Machtübertragung allein aus Rollenzuweisung oder Benutzergewichtung ableiten.

## Starttext für einen neuen Chat

> Wir setzen die Entwicklung von `kicad-din-electrical / ProjectOS` fort. Lies zuerst `docs/handover/PROJECTOS_ZWISCHENSTAND_2026-08-09.md` auf Branch `test/load-failure-preserves-state` und prüfe PR #159. Der letzte vollständig grüne Stand ist ProjectOS complete test suite Run #148. Fahre danach mit der Z_Cockpit-Sicht und read-only Simulation der expliziten Projektfunktionsaktivierung fort. Alles auf Deutsch. Architekturregeln, Benutzergewichtung, DENY-Vorrang, Rechteherkunft sowie die strikte Trennung zwischen Zuweisung und Aktivierung nicht verlieren.
