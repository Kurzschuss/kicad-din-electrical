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

Aktive Projektfunktionen werden über einen expliziten `permission_map` in normale rollenbasierte `ProjectOSPermissionAssignment`s übersetzt. Die Herkunft bleibt über `project_role`, `role_assignment_id` und `assigned_by_user_id` nachvollziehbar. Auch aus Projektfunktionen abgeleitete ALLOW-Rechte können ein explizites DENY nicht überstimmen.

## Z_Cockpit-Benutzersicht

`ZCockpitUserProjectRoleView` führt zusammen:

- aktive und abgelaufene Projektfunktionen;
- deutsche Funktionsbezeichnungen;
- Zuweisungsherkunft;
- Scope und Gültigkeit;
- Benutzergewichtung;
- daraus abgeleitete Rechtezuweisungen;
- effektive Rechteentscheidung und Rechteherkunft.

Die Sicht ist read-only. Hypothetische Projektfunktionen können simuliert werden, ohne den Ausgangszustand zu verändern.

## Projektfunktionswechsel-Simulation

`ProjectOSProjectRoleTransitionSimulator` unterstützt read-only Rollenwechsel:

- Projektfunktion hinzufügen;
- Projektfunktion anhand `role_assignment_id` entfernen;
- Funktionen ersetzen, z. B. Stellvertretung → Nachfolger;
- Rechteauswirkungen je Permission als Vorher/Nachher vergleichen;
- `decision_changed`, `became_allowed`, `became_denied` und Anzahl geänderter Permissions ausgeben.

Explizites DENY bleibt auch in simulierten Rollenwechseln vorrangig. Benutzergewichtung beeinflusst die Rechteentscheidung weiterhin nicht.

## Z_Cockpit-Projektleiteransicht für Funktionswechsel

`ZCockpitProjectRoleTransitionView` bereitet simulierte Funktionswechsel für Projektleiter verständlich auf. Die Sicht zeigt aktuelle und hypothetische Projektfunktionen, deutsche Funktionslabels, hinzugekommene und entfallene effektive Rechte, DENY-Konflikte, Risikoklassen, höchste betroffene Risikoklasse und eine kompakte Gesamtzusammenfassung.

Wichtig: Eine neu hinzugefügte Projektfunktion gilt nicht automatisch als erfolgreich wirksame Machtübertragung. Wenn ein explizites DENY weiterhin greift, wird dies als DENY-Konflikt ausgewiesen und das Recht bleibt verweigert.

## Tests / letzter bestätigter Stand

Die vollständige `ProjectOS complete test suite`, Run #145, ist für Commit `c6723ed117ab5ae0996b6965d0b4c045a437e5c9` erfolgreich.

PR #159 ist offen, Draft und mergebar. Der Branch ist inzwischen ein integrierter ProjectOS-Umsetzungsbranch und enthält wesentlich mehr als den ursprünglichen Persistenz-Test.

## Unmittelbar nächster Umsetzungsschritt

Als Nächstes die Regeln für **Aktivierung, Vertretungsfall und Nachfolgeauslösung** explizit modellieren:

1. Projektfunktion-Zuweisung strikt von tatsächlicher Aktivierung trennen;
2. Vertretung nur aufgrund eines expliziten Aktivierungsgrunds wirksam werden lassen;
3. Nachfolger nicht automatisch allein durch vorhandene `successor`-Zuordnung aktivieren;
4. Aktivierungszeitraum, auslösender Benutzer/Systemgrund und Scope protokollieren;
5. Simulation der Aktivierung vor echter Zustandsänderung ermöglichen;
6. DENY-Vorrang und read-only Simulationsprinzip beibehalten;
7. keine versteckte automatische Machtübertragung über Benutzergewichtung einführen.

## Starttext für einen neuen Chat

> Wir setzen die Entwicklung von `kicad-din-electrical / ProjectOS` fort. Lies zuerst `docs/handover/PROJECTOS_ZWISCHENSTAND_2026-08-09.md` auf Branch `test/load-failure-preserves-state` und prüfe PR #159. Der letzte vollständig grüne Stand ist ProjectOS complete test suite Run #145. Fahre danach mit den expliziten Aktivierungsregeln für Projektleiter, Stellvertretung und Nachfolger fort. Alles auf Deutsch. Architekturregeln, Benutzergewichtung, DENY-Vorrang, Rechteherkunft und read-only Simulation nicht verlieren.
