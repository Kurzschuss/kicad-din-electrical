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

## Projektgedächtnis und Wissensherkunft

`ProjectOSRoleKnowledgeBridge` materialisiert vorhandene Freigabe-/Nachprüfungs-Traces als referenzierte Wissensnachweise, ohne eine zweite fachliche Wahrheit zu erzeugen. Die fachliche Wahrheit bleibt bei `ProjectOSRoleActionApprovalEvaluator` bzw. `ProjectOSRoleEmergencyPostReviewEvaluator`.

Abgebildet werden Freigabeanforderung und Freigabewirksamkeit als `approval`, Nachprüfung als `review_result`, dazu `derived_from`-Beziehungen und Originalreferenzen wie `action_id`, `review_id`, `message_id`, `correlation_id`, `truth_source`, `escalation_required` und `historical_emergency_effect_preserved`.

## Z_Cockpit-Wissensherkunft – zuletzt umgesetzt

Neu vorhanden ist `ZCockpitKnowledgeOriginEvidenceView`.

Die bestehende `knowledge_origin`-Erklärung bleibt die Quelle für gespeicherte Wissenspfade. Darüber legt die neue read-only Evidenzsicht ausschließlich die bereits gespeicherten Referenzmetadaten offen.

Sie zeigt für Freigabe-/Nachprüfungswissen unter anderem:

- `truth_source`;
- `action_id`;
- `review_id`;
- `message_id`;
- `correlation_id`;
- `reference_id`;
- Quelltyp und Evidenzstatus des Wissensknotens.

Wenn `action_id` und `correlation_id` vorhanden sind, wird ein validiertes `approval_trace`-Navigationsziel erzeugt. Der `ZCockpitNavigationResolver` verwendet diese evidenzbewusste Herkunftssicht jetzt direkt für `knowledge_origin`.

Normale Wissensknoten ohne Freigabe-/Nachprüfungsmetadaten erhalten ausdrücklich keine künstliche Freigabeherkunft.

Commits dieses Blocks:

- `e4d6c7f1` feat(z-cockpit): Freigabenachweise in Wissensherkunft erklären
- `e7fee07e` feat(z-cockpit): Wissensherkunft mit Freigabenachweisen auflösen
- `97abe866` test(z-cockpit): Freigabenachweise in Wissensherkunft absichern

## Tests / letzter bestätigter Stand

Die vollständige `ProjectOS complete test suite`, Run #203, ist für Commit `97abe866e635784be74564bd395a8ec35228e9fe` erfolgreich.

PR #159 ist offen, Draft und mergebar. Der Branch ist inzwischen ein integrierter ProjectOS-Umsetzungsbranch und enthält wesentlich mehr als den ursprünglichen Persistenz-Test.

## Unmittelbar nächster Umsetzungsschritt

Als Nächstes den Benutzerverwaltungsblock als Ganzes auf Konsistenz und Persistenzreife prüfen:

1. welche Benutzer-/Rollen-/Freigabe-/Aktivierungsdaten müssen dauerhaft im Projektbundle gespeichert werden;
2. welche Daten sind ausschließlich abgeleitete read-only Sichten und dürfen nicht persistiert werden;
3. Projektgrenzen, ID-Stabilität und Migration für bestehende Bundle-Versionen festlegen;
4. Validierungsregeln für unvollständige oder widersprüchliche Benutzer-/Freigabedaten definieren;
5. danach Persistenzschema versionieren und Roundtrip-/Migrations-Tests ergänzen.

## Starttext für einen neuen Chat

> Wir setzen die Entwicklung von `kicad-din-electrical / ProjectOS` fort. Lies zuerst `docs/handover/PROJECTOS_ZWISCHENSTAND_2026-08-09.md` auf Branch `test/load-failure-preserves-state` und prüfe PR #159. Der letzte vollständig grüne Stand ist ProjectOS complete test suite Run #203. Freigabe-/Nachprüfungswissen ist ohne zweite Wahrheit im Projektgedächtnis referenziert; `knowledge_origin` erklärt jetzt `truth_source`, `action_id`, `review_id`, `message_id` und `correlation_id` und kann direkt zum `approval_trace` navigieren. Fahre mit der Konsistenz- und Persistenzreifeprüfung des gesamten Benutzerverwaltungsblocks fort. Alles auf Deutsch. Architekturregeln, Benutzergewichtung, DENY-Vorrang, Rechteherkunft und Korrelationskette nicht verlieren.
