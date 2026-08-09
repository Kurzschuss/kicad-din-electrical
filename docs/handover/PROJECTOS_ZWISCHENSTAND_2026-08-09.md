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

## Freigabe-/Nachprüfungskette und Wissensherkunft

Die Kette wird durch `project_id`, `correlation_id` und `causation_id` durchgängig geführt: `approval_requested` → optional `approval_decided` → `approval_effectiveness_evaluated` → bei Nachprüfung `post_review_completed` oder `post_review_escalated`.

Negative Nachprüfung schreibt die historische Notfallwirkung nicht rückwirkend um; `historical_emergency_effect_preserved=true` bleibt erhalten. Freigabe-/Nachprüfungs-Traces werden ohne zweite Wahrheit als referenzierte Wissensnachweise materialisiert. `knowledge_origin` erklärt `truth_source`, `action_id`, `review_id`, `message_id`, `correlation_id` und kann direkt zum `approval_trace` navigieren.

## Persistenz und Bundle v4

`ProjectOSUserManagementState` mit `USER_MANAGEMENT_PERSISTENCE_VERSION = 1` persistiert ausschließlich fachliche Benutzer-, Rechte-, Rollen-, Aktivierungs-, Beendigungs-, Freigabe- und Nachprüfungsdaten. Reproduzierbare Evaluator-, Simulations-, Z_Cockpit-, Navigation-, Trace- und materialisierte Wissensdaten werden nicht persistiert.

Bundle v4 speichert `session`, `sync_log`, stabile `project_id` und `user_management`. v2/v3 bleiben lesbar und werden erst beim expliziten Speichern auf v4 migriert. Save-As, Recovery, Dirty-State und transaktionssichere Fehlerfälle sind inklusive Benutzerverwaltung abgesichert.

## Z_Cockpit Persistenz/Migration und Konsistenz

`ZCockpitUserManagementPersistenceView` zeigt tatsächliche gespeicherte Bundle-Version, Migrationsbedarf, Persistenzversion des Benutzerblocks, Objektzähler und bewusst nicht persistierte Ableitungen. Der Status ist in Projektleiterübersicht, Attention und Navigation integriert. `USER_MANAGEMENT_BUNDLE_MIGRATION_PENDING` erscheint gelb und führt zum read-only Ziel `user_management_persistence`.

`ZCockpitUserManagementConsistencyView` prüft read-only die semantischen Lifecycle-Ketten Benutzer→Recht/Rolle→Aktivierung→Beendigung sowie Freigabeanforderung→Freigabe→Nachprüfung. Rote Fehler und gelbe Hinweise sind in Projektleiterübersicht, Aufmerksamkeit und Navigation eingebunden.

## Benutzerverwaltungs-Command-/Change-Service

`ProjectOSUserManagementChangeService` übernimmt Änderungen atomar: Für jede Operation wird zuerst ein vollständig validierter neuer `ProjectOSUserManagementState` aufgebaut und erst danach in den Manager übernommen. Erfolgreiche Änderungen markieren den Dirty-State; fehlgeschlagene Änderungen lassen State, Dirty-State und Hook unverändert.

Enge fachliche Commands existieren für Rechte, Projektrollen, Aktivierung, Rückgabe, Freigabeanforderung, Freigabeentscheidung und Nachprüfung. Projekt, Benutzer und Scope werden aus dem bestehenden Zustand abgeleitet; unbekannte Referenzen werden vor Commit abgewiesen.

## Audit-/Bus-/Korrelationsanbindung

`ProjectOSUserManagementChangeTrace` und `ProjectOSUserManagementChangeTraceEmitter` bilden ausschließlich bereits erfolgreich übernommene Änderungen als ProjectOS-Busnachricht und Audit-Eintrag ab. Sie erzeugen keine Fachmutation und keine zweite Wahrheit.

Regeln:

- jede erfolgreiche Benutzerverwaltungsänderung erzeugt genau einen Bus-Nachweis und genau einen Audit-Eintrag;
- fehlgeschlagene Commands rufen den Hook nicht auf und erzeugen keinen Nachweis;
- der Nachweis führt `operation`, `actor_user_id`, fachliche `reference`, Dirty-State und das bereits übernommene Domainobjekt;
- fachlich im Domainobjekt vorhandene Akteure werden weiterhin genutzt;
- der Emitter hält einen read-only vorherigen Snapshot, um die tatsächlich geänderte Fachreferenz aus dem Delta zu bestimmen.

## Expliziter Benutzerverwaltungs-Command-Kontext – umgesetzt

Neu ist `ProjectOSUserManagementCommandContext` als nicht persistierter Ausführungskontext mit:

- `actor_user_id`;
- `correlation_id`;
- optionaler `causation_id`.

Alle relevanten Operationen des `ProjectOSUserManagementChangeService` akzeptieren optional diesen Kontext und reichen ihn bis zum Audit-/Bus-Hook durch.

Der explizite Kontext hat Vorrang vor einer Akteursableitung aus dem geänderten Domainobjekt. Dadurch wird zum Beispiel bei einer Gewichtsänderung durch einen Administrator nicht mehr fälschlich der geänderte Benutzer als Akteur ausgewiesen. Gleiches gilt für direkte Rechtezuweisungen ohne Delegationsakteur.

Korrelationsketten werden im Emitter getrennt pro `correlation_id` geführt. Unterschiedliche fachliche Vorgänge werden dadurch nicht versehentlich über eine globale Kausalkette miteinander verknüpft. Innerhalb derselben Korrelation wird die `causation_id` weiterhin über die vorherige `message_id` fortgesetzt.

Commits:

- `8396f871` feat(projectos): expliziten Benutzerverwaltungs-Command-Kontext einführen
- `d2ed7c66` feat(projectos): Command-Kontext bis zum Änderungsereignis durchreichen
- `d5a74317` feat(projectos): expliziten Akteur und Korrelation im Trace verwenden
- `32e0bd6b` test(projectos): expliziten Command-Kontext und Korrelationsketten absichern

## Direkte Zustandssetzung weiter zurückgedrängt – umgesetzt

Der reguläre Benutzerverwaltungs-Command-Pfad verwendet den öffentlichen `DinEditorProjectManager.set_user_management()`-Setter nicht mehr.

Der Manager besitzt jetzt `_commit_user_management_change()` als internen Commit-Pfad für bereits vollständig validierte Kandidaten. Der öffentliche Setter bleibt vorerst als Kompatibilitäts-/expliziter Zustandssetzungspfad erhalten, darf aber von Produktionsmodulen nicht für normale Fachänderungen verwendet werden.

Ein Guard-Test durchsucht die Produktionsmodule in `distributions` und schlägt fehl, sobald dort erneut ein direkter Aufruf von `.set_user_management(` eingeführt wird.

Commits:

- `d450c452` refactor(projectos): Benutzerverwaltungs-Commit im Manager kapseln
- `13f2a6db` refactor(projectos): öffentlichen User-Management-Setter im Command-Pfad vermeiden
- `2d88800d` test(projectos): öffentliche User-Management-Setter im Produktionspfad sperren

## Command-Historie und Undo/Redo – Strategie beschlossen

Die Entwurfsentscheidung `docs/00_Project/entwurfsentscheidungen/EE-PROJECTOS-0001_Command_Historie_Undo_Redo.md` legt den Vertrag fest.

Grundregeln:

- Audit und Bus bleiben append-only und werden durch Undo/Redo niemals gelöscht oder rückwirkend verändert;
- eine Benutzerverwaltungs-Command-Historie ist read-only Laufzeitmetadaten und keine zweite fachliche Wahrheit;
- Undo/Redo darf keinen historischen `ProjectOSUserManagementState` blind zurückkopieren;
- Undo und Redo sind neue fachliche Commands mit neuer `command_id`, neuer `correlation_id`, normaler Validierung und neuer Audit-/Bus-Spur;
- der ursprüngliche Command bleibt unverändert nachweisbar und wird explizit referenziert;
- Reversibilität ist fail-closed und muss je Operation fachlich begründet sein;
- `user_weight_changed` ist der erste vollständig reversible Referenzfall;
- Freigabeentscheidungen und Nachprüfungen sind historische Tatsachen und nicht reversibel;
- die erste Undo-/Redo-Historie bleibt bewusst laufzeitbezogen und wird nicht in Bundle v4 persistiert.

Commit:

- `cb1126ce` docs(projectos): Command-Historie und Undo-Redo-Vertrag festlegen

## Tests / letzter bestätigter Stand

Bestätigte vollständige Läufe:

- Run #244 für Commit `32e0bd6b73cd689d8e2e49945f24001a19fdac34`: erfolgreich;
- Run #247 für Commit `2d88800dcfda7eb9ae50eb947a1291c3e010e527`: erfolgreich;
- Run #248 für Commit `cb1126cef76c7fc3ccdc0dd3e047981da66da4fa`: erfolgreich.

Die Läufe umfassen Repository-Health-Check, vollständige Pytest-Suite, Z_-Qualitätsprofil, KiCad-Bibliotheksprüfungen und Z_Cockpit-Generierung.

PR #159 bleibt bewusst Draft und der integrierte ProjectOS-Umsetzungsbranch.

## Unmittelbar nächster Umsetzungsschritt

Die ersten drei Punkte des vorherigen Handover-Blocks sind erledigt. Als Nächstes wird die beschlossene Undo-/Redo-Architektur implementiert:

1. pro Benutzerverwaltungs-Command eine stabile `command_id` ergänzen;
2. read-only `ProjectOSUserManagementCommandHistory` für erfolgreiche Commands einführen;
3. `user_weight_changed` als ersten reversiblen Referenzfall mit Vorher-/Nachherwert erfassen;
4. Undo der Gewichtsänderung als neue fachliche Änderung mit eigener `command_id`, eigener `correlation_id` und neuer Audit-/Bus-Spur umsetzen;
5. Redo analog als neue fachliche Änderung umsetzen;
6. Reversibilität anschließend nur für Operationen erweitern, für die eine explizite fachliche Gegenoperation vorhanden ist;
7. danach normale Commands sowie Undo/Redo über den vorhandenen Autorisierungs-/Vier-Augen-Vertrag absichern.

## Starttext für einen neuen Chat

> Wir setzen die Entwicklung von `kicad-din-electrical / ProjectOS` fort. Lies zuerst `docs/handover/PROJECTOS_ZWISCHENSTAND_2026-08-09.md` auf Branch `test/load-failure-preserves-state` und prüfe PR #159. Der letzte vollständig grüne dokumentierte Stand ist ProjectOS complete test suite Run #248. Expliziter Benutzerverwaltungs-Command-Kontext mit Akteur/Korrelation/Kausalität ist umgesetzt, der normale Command-Pfad umgeht den öffentlichen `set_user_management()`-Setter nicht mehr, und `EE-PROJECTOS-0001_Command_Historie_Undo_Redo.md` beschließt Undo/Redo als neue kompensierende Fachänderungen statt Snapshot-Rollback. Fahre mit `command_id`, read-only Command-Historie und `user_weight_changed` als erstem reversiblen Referenzfall fort. Alles auf Deutsch. Architecture Freeze 1.0, Single Source of Truth, DENY-Vorrang, Benutzergewichtung ohne Autorisierungswirkung, Rechteherkunft und append-only Audit-/Bus-Historie nicht verletzen.
