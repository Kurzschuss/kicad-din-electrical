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

## Z_Cockpit und Wissensherkunft

Vorhanden sind Projektkorrelationssicht, Projektleiter-Gesamtübersicht, Aufmerksamkeitsblock, Diagnose-Arbeitsansichten, UI-neutraler Navigationsvertrag, Resolver, Breadcrumb-/Rücksprungkontext und `approval_trace`-Detailansicht.

`ProjectOSRoleKnowledgeBridge` materialisiert vorhandene Freigabe-/Nachprüfungs-Traces als referenzierte Wissensnachweise, ohne eine zweite fachliche Wahrheit zu erzeugen. `ZCockpitKnowledgeOriginEvidenceView` erklärt `truth_source`, `action_id`, `review_id`, `message_id`, `correlation_id` und kann bei belegbarer Herkunft direkt zum `approval_trace` navigieren.

## Benutzerverwaltungs-Persistenzreife – zuletzt umgesetzt

Neu vorhanden sind:

- `ProjectOSUserManagementState`
- `USER_MANAGEMENT_PERSISTENCE_VERSION = 1`
- explizite Liste `DERIVED_NOT_PERSISTED`

Persistenzpflichtige fachliche Daten sind jetzt klar abgegrenzt:

- Benutzerprofile einschließlich Benutzergewichtung;
- explizite Rechtezuweisungen einschließlich `DENY`, Delegation, Scope, Risiko und Gültigkeit;
- Projektfunktions-Zuweisungen;
- Aktivierungen;
- Beendigungen/Rückgaben;
- Freigabeanforderungen;
- Freigabe-/Ablehnungsentscheidungen;
- Notfall-Nachprüfungen.

Ausdrücklich **nicht** persistiert werden reproduzierbare Ableitungen:

- Autorisierungs-/Evaluator-Ergebnisse;
- Simulationen;
- Z_Cockpit-Sichten;
- Attention-Items;
- Breadcrumb-/Navigationskontexte;
- materialisierte Freigabe-/Nachprüfungs-Wissensnachweise;
- Approval-/Post-Review-Traces.

Der Persistenzvertrag validiert referenzielle Konsistenz vor einer späteren Bundle-Integration:

- Projektrolle referenziert einen bekannten Benutzer und dasselbe Projekt;
- Rechtezuweisung referenziert einen bekannten Benutzer;
- Aktivierung referenziert bekannte Rolle und Benutzer;
- Beendigung referenziert bekannte Aktivierung und Benutzer;
- Freigabeanforderung gehört zum Projekt und referenziert bekannten Anforderer;
- Freigabe referenziert bekannte `action_id` und bekannten Prüfer;
- Nachprüfung referenziert bekannte `action_id` und bekannten Nachprüfer;
- IDs innerhalb jeder Objektklasse müssen eindeutig sein.

`as_dict()` / `from_dict()` bilden einen versionierten Roundtrip. Unbekannte Persistenzversionen, fremde Projektrollen und gebrochene Referenzen werden fail-closed abgewiesen.

Commits dieses Blocks:

- `270c99cb` feat(projectos): Benutzerverwaltungs-Persistenzvertrag einführen
- `42779fa1` test(projectos): Benutzerverwaltungs-Persistenzvertrag absichern

## Tests / letzter bestätigter Stand

Die vollständige `ProjectOS complete test suite`, Run #206, ist für Commit `42779fa1ae659011f15ea8f4b9273cc4384e0bc9` erfolgreich.

PR #159 ist offen und bleibt der integrierte ProjectOS-Umsetzungsbranch.

## Unmittelbar nächster Umsetzungsschritt

Als Nächstes den neuen Benutzerverwaltungs-Persistenzvertrag in das Projektbundle integrieren:

1. Bundle-Version gezielt von v3 auf v4 anheben;
2. optionalen `user_management`-Block in v4 speichern und laden;
3. v2/v3 ohne Benutzerverwaltungsdaten weiterhin rückwärtskompatibel laden;
4. v3→v4-Migration darf keinen Hintergrundschreibzugriff auslösen;
5. Manager-Snapshot/Dirty-State um persistierte Benutzerverwaltungsdaten erweitern;
6. Roundtrip-, Save-As-, Recovery- und fehlerhafte-Referenz-Tests für v4 ergänzen;
7. abgeleitete Z_Cockpit-/Simulations-/Wissensdaten weiterhin **nicht** in das Bundle aufnehmen.

## Starttext für einen neuen Chat

> Wir setzen die Entwicklung von `kicad-din-electrical / ProjectOS` fort. Lies zuerst `docs/handover/PROJECTOS_ZWISCHENSTAND_2026-08-09.md` auf Branch `test/load-failure-preserves-state` und prüfe PR #159. Der letzte vollständig grüne Stand ist ProjectOS complete test suite Run #206. Der Benutzerverwaltungsblock besitzt jetzt einen versionierten Persistenzvertrag `ProjectOSUserManagementState`: fachliche Benutzer-, Rechte-, Rollen-, Aktivierungs-, Rückgabe-, Freigabe- und Nachprüfungsdaten werden persistiert; Evaluator-Ergebnisse, Simulationen, Z_Cockpit, Navigation, Traces und materialisierte Wissensnachweise ausdrücklich nicht. Fahre mit Bundle v4 und der Integration des optionalen `user_management`-Blocks fort. Alles auf Deutsch. Architekturregeln, Benutzergewichtung, DENY-Vorrang, Rechteherkunft und Korrelationskette nicht verlieren.
