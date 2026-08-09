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

## Benutzerverwaltung und Autorisierung

Vorhanden sind Benutzerprofile mit Benutzergewichtung 0–1000, typisierte Rechteherkünfte, Scope, Risikoklasse, Gültigkeit, Delegation und read-only Rechte-Simulation. `DENY` hat Vorrang vor `ALLOW`. Benutzergewichtung ist sichtbar, ersetzt aber keine Freigabe und überstimmt kein `DENY`.

Die Projektfunktionen `project_lead`, `deputy`, `trusted_person` und `successor` sind als eigene Beziehungen vorhanden. Zuweisung, Aktivierung, Freigabe und Beendigung sind strikt getrennt. Kritische Aktivierungen und Rückgaben arbeiten fail-closed über Vier-Augen-Freigaben; Notfallaktionen dürfen vorläufig wirken und bleiben nachprüfungspflichtig.

## Freigabe- und Notfall-Nachprüfungskette

Freigabeanforderung, Entscheidung und Wirksamkeit werden mit `project_id`, `correlation_id` und `causation_id` auf Bus und Audit nachgewiesen. Eine Notfall-Nachprüfung ist ein eigener Lifecycle-Schritt und kann `confirmed` oder `negative` ergeben. Negative Nachprüfung schreibt die historische Notfallwirkung nicht rückwirkend um; `historical_emergency_effect_preserved=true` bleibt erhalten.

Der Nachprüfungsabschluss wird im selben Vorgang fortgesetzt:

- bestätigt → `projectos.role_action.post_review_completed` / Audit `post_review_completed`;
- negativ → `projectos.role_action.post_review_escalated` / Audit `post_review_escalated`;
- ohne Nachprüfung wird kein künstliches Abschlussereignis erzeugt.

## Z_Cockpit – aktueller Stand

Vorhanden sind Projektkorrelationssicht, Projektleiter-Gesamtübersicht, priorisierter Aufmerksamkeitsblock, Diagnose-Arbeitsansichten, UI-neutraler Navigationsvertrag, Resolver, Breadcrumb-/Rücksprungkontext und `approval_trace`-Detailansicht.

Zuletzt umgesetzt:

- `ZCockpitRoleApprovalTraceView` zeigt jetzt auch `post_review_completed` und `post_review_escalated`;
- bestätigte Nachprüfung führt zu `completed_confirmed`, `post_review_completed=true`, `attention_required=false`;
- negative Nachprüfung führt zu `completed_negative`, `escalation_required=true`, `attention_required=true`;
- Projektleiter-Gesamtübersicht zählt `post_review_open_count`, `post_review_confirmed_count` und `post_review_escalated_count` getrennt;
- offene oder eskalierte Nachprüfungen setzen die Gesamtampel auf Rot;
- der Aufmerksamkeitsblock entfernt bestätigte Notfall-Nachprüfungen aus der offenen Liste;
- negative Nachprüfungen bleiben als `APPROVAL_POST_REVIEW_ESCALATED` rot mit Priorität 30 und direktem `approval_trace`-Ziel sichtbar.

Commits dieses Blocks:

- `a2006174` feat(z-cockpit): Nachprüfungsabschluss im Freigabevorgang anzeigen
- `e44df5eb` feat(z-cockpit): Notfall-Nachprüfungen in Projektleiterübersicht aggregieren
- `734409a4` feat(z-cockpit): Nachprüfungsabschluss im Aufmerksamkeitsblock berücksichtigen
- `1cefeb16` test(z-cockpit): Nachprüfungsabschluss in Übersicht und Aufmerksamkeit absichern

## Tests / letzter bestätigter Stand

Die vollständige `ProjectOS complete test suite`, Run #196, ist für Commit `1cefeb16b0aa91707cd252f59bb7440271e947d5` erfolgreich.

PR #159 ist offen, Draft und mergebar. Der Branch ist inzwischen ein integrierter ProjectOS-Umsetzungsbranch und enthält wesentlich mehr als den ursprünglichen Persistenz-Test.

## Unmittelbar nächster Umsetzungsschritt

Als Nächstes Freigabe- und Nachprüfungsdaten in Projektgedächtnis und Wissensherkunft einbinden:

1. Freigabeanforderung, Entscheidung, Notfallwirkung, Nachprüfung und Eskalation als nachvollziehbare Wissens-/Herkunftsnachweise modellieren;
2. keine zweite Wahrheit neben Audit/Bus erzeugen – Projektgedächtnis referenziert bestehende IDs;
3. Z_Cockpit soll von Wissensherkunft direkt zum Freigabe-/Nachprüfungsvorgang navigieren können;
4. danach Benutzerverwaltungsblock auf Konsistenz, Persistenzbedarf und offene Architekturpunkte prüfen.

## Starttext für einen neuen Chat

> Wir setzen die Entwicklung von `kicad-din-electrical / ProjectOS` fort. Lies zuerst `docs/handover/PROJECTOS_ZWISCHENSTAND_2026-08-09.md` auf Branch `test/load-failure-preserves-state` und prüfe PR #159. Der letzte vollständig grüne Stand ist ProjectOS complete test suite Run #196. Notfall-Nachprüfungen sind vollständig korreliert und in Z_Cockpit integriert: bestätigte Nachprüfungen schließen Aufmerksamkeit, negative bleiben als rote Eskalation bestehen. Fahre mit der Einbindung von Freigabe-/Nachprüfungsdaten in Projektgedächtnis und Wissensherkunft fort. Alles auf Deutsch. Architekturregeln, Benutzergewichtung, DENY-Vorrang, Rechteherkunft und Korrelationskette nicht verlieren.
