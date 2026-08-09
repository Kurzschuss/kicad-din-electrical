# ProjectOS – Zwischenstand / Chat-Übergabe

Stand: 2026-08-09
Repository: Kurzschuss/kicad-din-electrical
Arbeitsbranch: `test/load-failure-preserves-state`
Pull Request: #159 – `Test: fehlgeschlagenes Projektladen hält Managerzustand stabil`

## Architekturgrundlagen

Architecture Freeze 1.0 bleibt maßgeblich. ProjectOS ist die Grundlage des Projekts. Weiterhin gelten Single Source of Truth, Domain Ownership, Object First, Offline First, Simulation First, Documentation First und Configuration before Code. Die drei Perspektiven Entwickler, Engineering und Projektleiter bleiben erhalten.

## Benutzerverwaltung und Autorisierung

Vorhanden sind Benutzerprofile mit Benutzergewichtung 0–1000, typisierte Rechteherkünfte, Scope, Risikoklasse, Gültigkeit, Delegation und read-only Rechte-Simulation. `DENY` hat Vorrang vor `ALLOW`. Benutzergewichtung ist sichtbar, ersetzt aber keine Freigabe und überstimmt kein `DENY`.

Die Projektfunktionen `project_lead`, `deputy`, `trusted_person` und `successor` sind eigene projektbezogene Beziehungen. Zuweisung, Aktivierung, Freigabe und Beendigung sind strikt getrennt. Kritische Aktivierungen und Rückgaben arbeiten fail-closed über Vier-Augen-Freigaben. Notfälle dürfen vorläufig wirken, bleiben nachprüfungspflichtig und werden korreliert auf Bus/Audit nachgewiesen.

## Freigabe-/Nachprüfungskette

Die Kette wird durch `project_id`, `correlation_id` und `causation_id` durchgängig geführt:

1. `approval_requested`
2. optional `approval_decided`
3. `approval_effectiveness_evaluated`
4. bei Nachprüfung `post_review_completed` oder `post_review_escalated`

Negative Nachprüfung schreibt die historische Notfallwirkung nicht rückwirkend um; `historical_emergency_effect_preserved=true` bleibt erhalten.

## Z_Cockpit

Vorhanden sind Projektkorrelationssicht, Projektleiter-Gesamtübersicht, Aufmerksamkeitsblock, Diagnose-Arbeitsansichten, UI-neutraler Navigationsvertrag, Resolver, Breadcrumb-/Rücksprungkontext und `approval_trace`-Detailansicht.

Bestätigte Notfall-Nachprüfungen schließen Aufmerksamkeit. Negative Nachprüfungen bleiben als rote Eskalation sichtbar. Die Projektleiterübersicht zählt offene, bestätigte und eskalierte Nachprüfungen getrennt.

## Projektgedächtnis und Wissensherkunft – zuletzt umgesetzt

Neu vorhanden ist `ProjectOSRoleKnowledgeBridge`.

Der Adapter erzeugt ausdrücklich **keine zweite Freigabe- oder Nachprüfungswahrheit**. Die fachliche Wahrheit bleibt bei `ProjectOSRoleActionApprovalEvaluator` bzw. `ProjectOSRoleEmergencyPostReviewEvaluator`. Das Projektgedächtnis materialisiert nur referenzierte Nachweise aus bereits vorhandenen Trace-Daten.

Abgebildet werden unter anderem:

- Freigabeanforderung als Wissenselement `approval`;
- Freigabewirksamkeit als Wissenselement `approval`;
- Notfall-Nachprüfung als Wissenselement `review_result`;
- `derived_from`-Beziehungen zwischen Nachweisen;
- Originalreferenzen `action_id`, `review_id`, `message_id`, `correlation_id` und `truth_source` in den Metadaten;
- `historical_emergency_effect_preserved` und `escalation_required` beim Nachprüfungsnachweis.

Die Materialisierung ist idempotent: dieselbe `action_id`/`review_id` erzeugt nicht mehrfach denselben Wissensnachweis. Fremde Projekttraces werden abgewiesen.

Commits dieses Blocks:

- `906eac84` feat(project): Freigaben und Nachprüfungen ins Projektgedächtnis referenzieren
- `d6733091` test(project): Freigabe- und Nachprüfungswissen absichern

## Tests / letzter bestätigter Stand

Die vollständige `ProjectOS complete test suite`, Run #199, ist für Commit `d67330914525ed1bc746ded3f0f548d26b20a2c6` erfolgreich.

PR #159 ist offen, Draft und mergebar. Der Branch ist inzwischen ein integrierter ProjectOS-Umsetzungsbranch und enthält wesentlich mehr als den ursprünglichen Persistenz-Test.

## Unmittelbar nächster Umsetzungsschritt

Als Nächstes die referenzierten Freigabe-/Nachprüfungsnachweise in die bestehende Z_Cockpit-Wissensherkunft integrieren:

1. `knowledge_origin` soll `action_id`, `review_id`, `message_id`, `correlation_id` und `truth_source` sichtbar erklären;
2. von einem Freigabe-/Nachprüfungs-Wissensknoten direkt zum `approval_trace` navigieren;
3. Herkunftspfad `Freigabeanforderung → Wirksamkeit → Nachprüfung/Eskalation` lesbar aufbereiten;
4. anschließend Benutzerverwaltungsblock auf Konsistenz, Persistenzbedarf und offene Architekturpunkte prüfen.

## Starttext für einen neuen Chat

> Wir setzen die Entwicklung von `kicad-din-electrical / ProjectOS` fort. Lies zuerst `docs/handover/PROJECTOS_ZWISCHENSTAND_2026-08-09.md` auf Branch `test/load-failure-preserves-state` und prüfe PR #159. Der letzte vollständig grüne Stand ist ProjectOS complete test suite Run #199. Freigabe- und Notfall-Nachprüfungsdaten werden inzwischen ohne zweite Wahrheit als referenzierte Wissensnachweise ins Projektgedächtnis materialisiert. Fahre mit der Z_Cockpit-Wissensherkunft und Navigation vom Wissensknoten zum `approval_trace` fort. Alles auf Deutsch. Architekturregeln, Benutzergewichtung, DENY-Vorrang, Rechteherkunft und Korrelationskette nicht verlieren.
