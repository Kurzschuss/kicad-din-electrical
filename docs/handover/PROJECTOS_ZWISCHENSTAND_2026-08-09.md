# ProjectOS – Zwischenstand / Chat-Übergabe

Stand: 2026-08-09
Repository: `Kurzschuss/kicad-din-electrical`
Arbeitsbranch: `test/load-failure-preserves-state`
Pull Request: #159 – `Test: fehlgeschlagenes Projektladen hält Managerzustand stabil`

## Architekturgrundlagen

Architecture Freeze 1.0 bleibt maßgeblich. ProjectOS bleibt Grundlage des Projekts. Weiterhin gelten:

- Single Source of Truth;
- Domain Ownership;
- Object First;
- Offline First;
- Simulation First;
- Documentation First;
- Configuration before Code;
- die Perspektiven Entwickler, Engineering und Projektleiter.

Benutzergewichtung bleibt sichtbar, besitzt aber keine implizite Autorisierungswirkung. `DENY` hat Vorrang vor `ALLOW`. Audit-/Bus-Nachweise bleiben append-only.

## Persistenz und Projektidentität

Bundle v4 speichert `session`, `sync_log`, stabile `project_id` und den fachlichen `user_management`-Block. v2/v3 bleiben lesbar und werden erst beim expliziten erfolgreichen Speichern auf v4 migriert.

`ProjectOSUserManagementState` persistiert ausschließlich fachliche Benutzer-, Rechte-, Rollen-, Aktivierungs-, Beendigungs-, Freigabe- und Nachprüfungsobjekte. Reproduzierbare Evaluator-, Simulations-, Trace-, Runtime-History-, Autorisierungsdiagnose-, Navigation- und Z_Cockpit-Daten werden nicht als zweite Wahrheit persistiert.

Save, Save-As, Load, Recovery und Discard bleiben transaktionssicher. Fehlgeschlagene Vorgänge hinterlassen keinen Teilzustand.

## Benutzerverwaltung und Vier-Augen-Wirksamkeit

Vorhanden sind Benutzerprofile, Rechteherkünfte, Scope, Risikoklasse, Gültigkeit, Delegation sowie die Projektfunktionen `project_lead`, `deputy`, `trusted_person` und `successor`.

Zuweisung, Aktivierung, Freigabe und Beendigung sind getrennte fachliche Vorgänge. High-/Critical-Aktivierungen erhalten ohne wirksame Vier-Augen-Freigabe keine Rollenrechte. High-/Critical-Deaktivierungen beenden die Rechtewirkung ohne wirksame Freigabe nicht vorzeitig. Notfälle dürfen nach den vorhandenen Regeln vorläufig wirken, bleiben aber nachprüfungspflichtig.

Die vorhandenen Evaluatoren bleiben die einzige Quelle dieser Freigabewirksamkeit:

- `ProjectOSApprovedRoleActivationEvaluator`;
- `ProjectOSApprovedRoleDeactivationEvaluator`;
- `ProjectOSRoleActionApprovalEvaluator`.

Es wurde keine zweite Approval-State-Machine eingeführt.

## Atomarer Benutzerverwaltungs-Change-Service

`ProjectOSUserManagementChangeService` bleibt der niedrige atomare Domain-Primitive. Er baut zuerst einen vollständig validierten Kandidatenzustand auf und übernimmt ihn erst danach in den Manager.

Der reguläre Command-Pfad verwendet den öffentlichen `set_user_management()`-Setter nicht mehr. Der Manager besitzt `_commit_user_management_change()` als internen Commit-Pfad. Ein Guard-Test verhindert direkte Produktionsaufrufe von `.set_user_management(`.

Der rohe Change-Service bleibt bewusst nur für kontrollierten Bootstrap, Migration und Tests verfügbar. Produktive Command-Ausführung erfolgt über die gesicherte Runtime.

## Expliziter Command-Kontext und Command-ID

`ProjectOSUserManagementCommandContext` beschreibt genau einen Command und wird nicht im Domainzustand persistiert.

Er führt:

- `command_id` als stabile UUID pro Command;
- `actor_user_id`;
- `correlation_id`;
- optional `causation_id`;
- `history_action` mit `command`, `undo` oder `redo`;
- bei Undo/Redo `related_command_id`.

Ein Context darf nicht für einen zweiten Command wiederverwendet werden. Eine bereits verwendete `command_id` wird vor einer zweiten Mutation abgewiesen.

Der explizite Akteur hat Vorrang vor einer bloßen Ableitung aus dem geänderten Domainobjekt. Korrelations-/Kausalketten werden getrennt pro `correlation_id` geführt.

## Audit, Bus und Command-Historie

`ProjectOSUserManagementChangeTraceEmitter` bildet ausschließlich erfolgreich übernommene Änderungen als Bus-/Audit-Nachweise ab.

Jede erfolgreiche verfolgte Änderung erhält:

- `command_id`;
- Operation;
- Akteur;
- fachliche Referenz;
- `project_id`;
- `correlation_id`;
- `causation_id`;
- Busnachricht;
- Audit-Eintrag.

Die `command_id` wird inzwischen zusätzlich direkt im `DinSyncLog`-Audit-Eintrag geführt. Der Projektbundle-Loader validiert und erhält diese optionale UUID beim Roundtrip. Damit ist die Command↔Audit-Verknüpfung auch nach Save/Load explizit erhalten.

Fehlgeschlagene oder nicht autorisierte Commands erzeugen weder Fachmutation noch Bus-/Audit-Nachweis.

`ProjectOSUserManagementCommandHistory` ist eine read-only Laufzeit-Historie und keine zweite fachliche Wahrheit. Sie wird nicht in Bundle v4 persistiert.

## Undo/Redo – kompensierende Fachänderungen

Die Entwurfsentscheidung `docs/00_Project/entwurfsentscheidungen/EE-PROJECTOS-0001_Command_Historie_Undo_Redo.md` ist umgesetzt.

Undo/Redo ist kein Snapshot-Rollback. `ProjectOSUserManagementUndoRedoService` führt Undo und Redo als neue fachliche Commands aus.

Aktuell vollständig reversibler Referenzfall: `user_weight_changed`.

Regeln:

- ursprünglicher Command und ursprünglicher Audit-Nachweis bleiben unverändert;
- Undo erhält neue `command_id` und neue `correlation_id`;
- Redo erhält wiederum neue `command_id` und neue `correlation_id`;
- Undo/Redo erzeugt neue Bus-/Audit-Nachweise;
- aktueller Domainzustand muss exakt zum erwarteten History-Wert passen, sonst fail-closed;
- nicht reversible Commands werden beim Undo nicht übersprungen;
- ein neuer normaler Command nach Undo schließt den Redo-Zweig;
- Freigabeentscheidungen und Nachprüfungen bleiben historische Tatsachen und sind nicht reversibel.

## Zentrale Reversibilitätsmatrix – umgesetzt

`ProjectOSUserManagementReversibilityPolicy` ist die zentrale fail-closed Matrix für Kompensierbarkeit.

Aktuell ist ausschließlich `user_weight_changed` reversibel, mit der Gegenoperation `restore_previous_weight`.

Bewusst nicht reversibel sind derzeit:

- `user_created` – keine fachliche Benutzer-Deaktivierungs-/Löschoperation vorhanden;
- `permission_assigned` – noch kein expliziter Rechtewiderruf modelliert;
- `project_role_assigned` – noch keine explizite Aufhebung der Rollenzuweisung modelliert;
- `project_role_activated` – eine Deaktivierung beendet historisch, sie löscht die Aktivierung nicht;
- `project_role_deactivated` – eine Reaktivierung wäre ein neuer Lifecycle-Vorgang;
- `approval_requested` – historische Anforderung;
- `approval_recorded` – historische Entscheidung;
- `post_review_completed` – historische Nachprüfung.

`ProjectOSUserManagementUndoRedoService` prüft diese Matrix zusätzlich zur Command-Historie. Unbekannte Operationen sind ebenfalls fail-closed.

## Runtime-Lifecycle – umgesetzt

Load, Recover, Discard, New Project und explizite vollständige Benutzerverwaltungs-Zustandssetzung erhöhen eine nicht persistierte `user_management_runtime_generation`.

Change-Service, Trace-Emitter, Command-Historie und Autorisierungsnachweise richten sich daran aus. Dadurch werden alte Runtime-History-, Trace-, Delta-, Kausal- und Autorisierungsdaten nach einem vollständigen Projektzustandswechsel nicht in den neuen Zustand verschleppt.

## Zentrale Command-Policy – umgesetzt

`ProjectOSUserManagementCommandPolicy` ist die zentrale unveränderliche Runtime-Konfigurationsquelle.

Die Default-Policy definiert Command→Recht-Zuordnungen für alle vorhandenen Benutzerverwaltungsoperationen, darunter:

- `project.user_management.user.create`;
- `project.user_management.weight.change`;
- `project.user_management.permission.assign`;
- `project.user_management.role.assign`;
- `project.user_management.role.activate`;
- `project.user_management.role.deactivate`;
- `project.user_management.approval.request`;
- `project.user_management.approval.record`;
- `project.user_management.post_review.complete`;
- getrennte Rechte für Gewichts-Undo und -Redo.

Rollenabgeleitete Rechte bleiben in der Default-Policy bewusst leer. Es gibt keine implizite Regel „Projektleiter darf automatisch alles“. `role_permission_map` und `role_risk_class_map` müssen projektspezifisch explizit konfiguriert werden.

## Produktive Benutzerverwaltungs-Runtime – umgesetzt

`build_projectos_user_management_runtime()` ist der zentrale produktive Einstieg. Er bindet gemeinsam:

- `ProjectOSUserManagementCommandPolicy`;
- `ProjectOSUserManagementChangeTraceEmitter`;
- `ProjectOSUserManagementCommandAuthorization`;
- `ProjectOSAuthorizedUserManagementChangeService`;
- `ProjectOSUserManagementUndoRedoService`.

Ein Guard-Test verhindert, dass Produktionsmodule den rohen `ProjectOSUserManagementChangeService` direkt instanziieren. Bootstrap-/Migrations-/Testpfade bleiben davon ausdrücklich ausgenommen.

## Command-Autorisierung – umgesetzt

`ProjectOSUserManagementCommandAuthorization` ist rein lesend und fail-closed.

Der Autorisierer prüft:

- expliziten Command-Kontext;
- vorhandenen Akteur;
- zentrale Command→Recht-Zuordnung;
- persistierte Rechtezuweisungen;
- optional rollenabgeleitete Rechte;
- Scope und Gültigkeit;
- `DENY`-Vorrang über `ProjectOSAuthorizationEvaluator`.

Benutzergewichtung wird nicht für die Entscheidung verwendet.

### Rollenabgeleitete Command-Rechte

Rollenrechte werden nur aus wirksamen Aktivierungen abgeleitet. High-/Critical-Rollen verwenden die vorhandenen Vier-Augen-Evaluatoren.

Damit gilt weiterhin:

- nicht freigegebene High-/Critical-Aktivierung gewährt keine Rollenrechte;
- nicht freigegebene High-/Critical-Deaktivierung entzieht Rollenrechte nicht vorzeitig;
- erst eine wirksame Deaktivierung entfernt Rollenrechte;
- explizites `DENY` blockiert auch rollenabgeleitetes `ALLOW`.

## Erfolgreicher Autorisierungsnachweis – umgesetzt

`ProjectOSUserManagementAuthorizationEvidence` ist ein read-only Runtime-Nachweis einer erfolgreichen Autorisierung.

Er verknüpft:

- `command_id`;
- `project_id`;
- Operation;
- Akteur;
- `correlation_id`;
- Policy-Key;
- erforderliches Recht;
- Entscheidung;
- effektive Rechteherkünfte;
- `message_id` des Bus-Nachweises;
- Audit-Referenz.

Der Nachweis wird nicht in Bundle v4 persistiert. Eine abgewiesene Entscheidung bleibt als letzte Diagnose sichtbar, erzeugt aber keinen erfolgreichen Autorisierungsnachweis und weiterhin keine Domain-/Bus-/Audit-/History-Mutation.

## Z_Cockpit Command-/Autorisierungsdiagnostik – umgesetzt

`ZCockpitUserManagementCommandDiagnosticsView` zeigt read-only:

- letzten Autorisierungsentscheid;
- deutsche Entscheidungsbezeichnung;
- erforderliches Recht und Policy-Key;
- Akteur und Scope;
- effektive Rechteherkünfte;
- rollenabgeleitete Quellenanzahl;
- `DENY`-Blockade;
- letzten erfolgreichen Autorisierungsnachweis;
- Command-History-Zustand;
- Undo-/Redo-Verfügbarkeit;
- Trace-/Message-Anzahl.

Eine abgewiesene letzte Entscheidung wird gelb dargestellt. Sie ist ein Aufmerksamkeitsgrund, aber kein roter fachlicher Konsistenzfehler.

`ZCockpitProjectLeadOverview` kann die produktive Benutzerverwaltungs-Runtime optional einbinden und führt diese Diagnose in Übersicht und Summary mit.

## End-to-End-Sicherheitsweg – abgesichert

Der neue End-to-End-Test deckt folgende Kette ab:

1. Projektfunktion `deputy`;
2. High-Risk-Aktivierung;
3. wirksame Vier-Augen-Freigabe;
4. explizit konfigurierte rollenabgeleitete Benutzerverwaltungsrechte;
5. autorisierte Gewichtsänderung;
6. autorisiertes Undo;
7. autorisiertes Redo;
8. drei getrennte Bus-/Audit-/Autorisierungsnachweise;
9. Z_Cockpit-Diagnose;
10. anschließendes explizites `DENY`, das das rollenabgeleitete `ALLOW` ohne neue Fach-/Audit-/History-Mutation blockiert.

## Relevante neue Dateien dieses Blocks

- `distributions/projectos_user_management_command_policy.py`
- `distributions/projectos_user_management_runtime.py`
- `distributions/projectos_user_management_authorization_evidence.py`
- `distributions/projectos_user_management_reversibility.py`
- `distributions/z_cockpit_user_management_command_diagnostics.py`
- `distributions/test_projectos_user_management_runtime.py`
- `distributions/test_projectos_user_management_authorization_evidence.py`
- `distributions/test_z_cockpit_user_management_command_diagnostics.py`
- `distributions/test_projectos_user_management_authorization_e2e.py`
- `distributions/test_projectos_user_management_reversibility.py`
- `distributions/test_projectos_user_management_audit_command_id.py`

## Relevante aktuelle Commits

- `4961a8fa` feat(projectos): zentrale Benutzerverwaltungs-Command-Policy einführen
- `f88a68b2` feat(projectos): gesicherte Benutzerverwaltungs-Runtime verdrahten
- `2133e8eb` test(projectos): zentrale Policy und gesicherte Runtime absichern
- `4ded27a0` feat(projectos): Autorisierungsnachweis ergänzen
- `56e628dd` feat(projectos): erfolgreiche Autorisierung mit Trace verknüpfen
- `ef4a19c8` feat(projectos): Z-Cockpit-Command-Autorisierungsdiagnose ergänzen
- `be345317` feat(projectos): Command-Diagnose in Z-Cockpit-Gesamtübersicht integrieren
- `7393ff4b` test(projectos): Command-Autorisierung End-to-End absichern
- `0f0d49c4` feat(projectos): zentrale Reversibilitätsmatrix einführen
- `799630e9` refactor(projectos): Undo-Redo an Reversibilitätsmatrix binden
- `8d3fecd1` feat(projectos): Command-ID im Audit-Bundle erhalten
- `af45a636` feat(projectos): Command-ID direkt mit Audit-Nachweis verknüpfen
- `2de84c8f` test(projectos): Command-ID im Audit-Bundle-Roundtrip absichern

## Tests / letzter bestätigter Stand

Bestätigte vollständige grüne Läufe dieses Entwicklungsblocks:

- Run #285 – zentrale Policy, produktive Runtime, Autorisierungsnachweis, Z_Cockpit und End-to-End-Sicherheitsweg;
- Run #288 – zentrale fail-closed Reversibilitätsmatrix;
- **Run #291 – Commit `2de84c8f3f05dbec3f68d8264044f08a9b92bdf0`: Audit-`command_id` und Bundle-Roundtrip vollständig erfolgreich.**

Die vollständigen Läufe umfassen Repository-Health-Check, komplette Pytest-Suite, Z_-Qualitätsprofil, KiCad-Bibliotheksprüfungen und Z_Cockpit-Generierung.

PR #159 bleibt bewusst Draft und der integrierte ProjectOS-Umsetzungsbranch.

## Unmittelbar nächster Umsetzungsschritt

Der Sicherheits-/Command-Infrastrukturblock ist jetzt geschlossen. Neue Undo-Fälle dürfen erst eingeführt werden, wenn eine explizite fachliche Gegenoperation existiert.

Als nächstes den **Rechte-Lifecycle mit explizitem Widerruf** modellieren:

1. fachliches Modell für Rechtewiderruf/-beendigung definieren, statt `ProjectOSPermissionAssignment` historisch zu löschen;
2. Scope, Zeitpunkt, Akteur, Grund und Referenz des Widerrufs festlegen;
3. `ProjectOSAuthorizationEvaluator` um die Wirksamkeit solcher Widerrufe erweitern, weiterhin `DENY`-priorisiert;
4. Persistenz/Bundle v4 rückwärtskompatibel erweitern;
5. Change-Service, Command-Policy, Audit/Bus und Z_Cockpit anbinden;
6. erst danach entscheiden, ob `permission_assigned` über eine neue Widerrufsoperation kompensierbar werden darf;
7. anschließend analog prüfen, ob für Rollenzuweisungen eine explizite Beendigungsoperation benötigt wird.

Wichtig: Rechtezuweisungen, Freigaben oder andere historische Tatsachen niemals für Undo rückwirkend aus dem Zustand löschen.

## Starttext für einen neuen Chat

> Wir setzen die Entwicklung von `kicad-din-electrical / ProjectOS` fort. Lies zuerst `docs/handover/PROJECTOS_ZWISCHENSTAND_2026-08-09.md` auf Branch `test/load-failure-preserves-state` und prüfe PR #159. Der letzte vollständig grüne Code-Stand ist ProjectOS complete test suite Run #291 für Commit `2de84c8f3f05dbec3f68d8264044f08a9b92bdf0`. Zentrale Command-Policy, produktive gesicherte Benutzerverwaltungs-Runtime, Autorisierungsnachweis, Z_Cockpit-Command-Diagnostik, End-to-End-Vier-Augen-/DENY-Pfad, fail-closed Reversibilitätsmatrix und persistierte Audit-`command_id` sind umgesetzt. Fahre mit einem expliziten Rechtewiderrufs-Lifecycle fort; historische Rechtezuweisungen dürfen nicht gelöscht werden. Alles auf Deutsch. Architecture Freeze 1.0, Single Source of Truth, Configuration before Code, DENY-Vorrang, Benutzergewichtung ohne Autorisierungswirkung und append-only Audit-/Bus-Historie nicht verletzen.
