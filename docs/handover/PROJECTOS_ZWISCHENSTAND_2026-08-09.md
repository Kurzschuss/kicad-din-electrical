# ProjectOS – Zwischenstand / Chat-Übergabe

Stand: 2026-08-09
Repository: `Kurzschuss/kicad-din-electrical`
Arbeitsbranch: `test/load-failure-preserves-state`
Pull Request: #159 – `Test: fehlgeschlagenes Projektladen hält Managerzustand stabil`

## Architekturgrundlagen

Architecture Freeze 1.0 bleibt maßgeblich. ProjectOS ist die Grundlage des Projekts. Es gelten weiterhin:

- Single Source of Truth;
- Domain Ownership;
- Object First;
- Offline First;
- Simulation First;
- Documentation First;
- Configuration before Code;
- die Perspektiven Entwickler, Engineering und Projektleiter.

Benutzergewichtung bleibt sichtbar, besitzt aber keine implizite Autorisierungswirkung. `DENY` hat Vorrang vor `ALLOW`. Historische Audit-/Bus-Nachweise bleiben append-only.

## Persistenz und Projektidentität

Bundle v4 speichert `session`, `sync_log`, stabile `project_id` und den fachlichen `user_management`-Block. v2/v3 bleiben lesbar und werden erst beim expliziten erfolgreichen Speichern auf v4 migriert.

`ProjectOSUserManagementState` persistiert ausschließlich fachliche Benutzer-, Rechte-, Rollen-, Aktivierungs-, Beendigungs-, Freigabe- und Nachprüfungsobjekte. Reproduzierbare Evaluator-, Simulations-, Trace-, History-, Navigation- und Z_Cockpit-Daten werden nicht als zweite Wahrheit in den Benutzerverwaltungsblock geschrieben.

Save, Save-As, Load, Recovery und Discard bleiben transaktionssicher. Fehlgeschlagene Vorgänge hinterlassen keinen Teilzustand.

## Benutzerverwaltung und Vier-Augen-Wirksamkeit

Vorhanden sind Benutzerprofile, Rechteherkünfte, Scope, Risikoklasse, Gültigkeit, Delegation sowie die Projektfunktionen `project_lead`, `deputy`, `trusted_person` und `successor`.

Zuweisung, Aktivierung, Freigabe und Beendigung sind getrennte fachliche Vorgänge. High-/Critical-Aktivierungen erhalten ohne wirksame Vier-Augen-Freigabe keine Rollenrechte. High-/Critical-Deaktivierungen beenden die Rechtewirkung ohne wirksame Freigabe nicht vorzeitig. Notfälle dürfen nach den vorhandenen Regeln vorläufig wirken, bleiben aber nachprüfungspflichtig.

Die vorhandenen Evaluatoren bleiben die einzige Quelle für diese Freigabewirksamkeit:

- `ProjectOSApprovedRoleActivationEvaluator`;
- `ProjectOSApprovedRoleDeactivationEvaluator`;
- `ProjectOSRoleActionApprovalEvaluator`.

Es wurde keine zweite Approval-State-Machine eingeführt.

## Atomarer Benutzerverwaltungs-Change-Service

`ProjectOSUserManagementChangeService` bleibt der niedrige atomare Domain-Primitive. Er baut zuerst einen vollständig validierten Kandidatenzustand auf und übernimmt ihn erst danach in den Manager.

Der reguläre Command-Pfad verwendet den öffentlichen `set_user_management()`-Setter nicht mehr. Der Manager besitzt `_commit_user_management_change()` als internen Commit-Pfad. Ein Guard-Test verhindert neue direkte Produktionsaufrufe von `.set_user_management(`.

Der rohe Change-Service bleibt bewusst für kontrollierten Bootstrap, Migration und Tests verfügbar. Produktive Autorisierung wird über eine eigene gesicherte Ausführungsgrenze gelegt, damit Bootstrap nicht durch ein zirkuläres „erst Recht anlegen, bevor ein Recht angelegt werden darf“ blockiert wird.

## Expliziter Command-Kontext und Command-ID

`ProjectOSUserManagementCommandContext` beschreibt genau einen Command und wird nicht im Domainzustand persistiert.

Er führt aktuell:

- `command_id` als stabile UUID pro Command;
- `actor_user_id`;
- `correlation_id`;
- optional `causation_id`;
- `history_action` mit `command`, `undo` oder `redo`;
- bei Undo/Redo `related_command_id`.

Ein Context darf nicht für einen zweiten Command wiederverwendet werden. Ein bereits verwendetes `command_id` wird vor einer zweiten Mutation abgewiesen.

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

Fehlgeschlagene oder nicht autorisierte Commands erzeugen weder Fachmutation noch Bus-/Audit-Nachweis.

`ProjectOSUserManagementCommandHistory` ist eine read-only Laufzeit-Historie und keine zweite fachliche Wahrheit. Ein Record referenziert den erfolgreichen Command, Bus-/Audit-Nachweis und – ausschließlich bei reversiblen Operationen – die minimal notwendigen Kompensationsdaten.

Die Historie wird nicht in Bundle v4 persistiert.

## Undo/Redo – umgesetzt

Die Entwurfsentscheidung `docs/00_Project/entwurfsentscheidungen/EE-PROJECTOS-0001_Command_Historie_Undo_Redo.md` ist umgesetzt.

Undo/Redo ist kein Snapshot-Rollback. `ProjectOSUserManagementUndoRedoService` führt Undo und Redo als neue fachliche Commands aus.

Erster vollständig reversibler Referenzfall: `user_weight_changed`.

Regeln:

- ursprünglicher Command und ursprünglicher Audit-Nachweis bleiben unverändert;
- Undo erhält neue `command_id` und neue `correlation_id`;
- Redo erhält wiederum neue `command_id` und neue `correlation_id`;
- Undo/Redo erzeugt neue Bus-/Audit-Nachweise;
- aktueller Domainzustand muss exakt zum erwarteten History-Wert passen, sonst fail-closed;
- nicht reversible Commands werden beim Undo nicht übersprungen;
- ein neuer normaler Command nach Undo schließt den Redo-Zweig;
- Freigabeentscheidungen und Nachprüfungen bleiben historische Tatsachen und sind nicht reversibel.

## Runtime-Lifecycle der Command-Historie – umgesetzt

Load, Recover, Discard, New Project und explizite vollständige Benutzerverwaltungs-Zustandssetzung erhöhen eine nicht persistierte `user_management_runtime_generation`.

Change-Service, Trace-Emitter und Command-Historie richten sich daran aus. Dadurch werden alte Laufzeit-History-, Trace-, Delta- und Kausaldaten nach einem vollständigen Projektzustandswechsel nicht in den neuen Zustand verschleppt.

Insbesondere:

- Laufzeit-Historie wird zurückgesetzt;
- alte Trace-/Message-Listen werden zurückgesetzt;
- der Delta-Ausgangspunkt wird neu gesetzt;
- bei managergebundenem Audit-Log wird nach Load/Recover wieder das aktuelle `manager.sync_log` verwendet;
- alte `command_id`-Runtime-Sperren werden generationstreu zurückgesetzt.

Tests decken Load, Recover, Discard und New Project ab.

## Command-Autorisierung – umgesetzt

Neu ist `ProjectOSUserManagementCommandAuthorization` als rein lesender, fail-closed Autorisierer.

Die erforderlichen Rechte werden **nicht im Service hart codiert**, sondern über `command_permission_map` konfiguriert. Für Undo und Redo können getrennte Rechte über Schlüssel wie `undo:user_weight_changed` und `redo:user_weight_changed` verlangt werden.

Der Autorisierer prüft:

- expliziten Command-Kontext;
- vorhandenen Akteur;
- konfigurierte Command→Recht-Zuordnung;
- persistierte Rechtezuweisungen;
- optional rollenabgeleitete Rechte;
- Scope und Gültigkeit;
- `DENY`-Vorrang über `ProjectOSAuthorizationEvaluator`.

Benutzergewichtung wird für die Entscheidung weiterhin nicht verwendet.

### Rollenabgeleitete Command-Rechte

Optional erhält der Autorisierer:

- `role_permission_map`;
- `role_risk_class_map`.

Rollenrechte werden nur aus wirksamen Aktivierungen abgeleitet. Für High-/Critical-Rollen wird die bereits vorhandene Vier-Augen-Auswertung verwendet.

Bei einer Deaktivierung gilt ebenfalls die vorhandene Freigabelogik:

- eine noch nicht wirksame High-/Critical-Deaktivierung entzieht die Rollenrechte nicht vorzeitig;
- erst eine wirksame Deaktivierung entfernt die Rollenrechte;
- ein explizites `DENY` kann ein rollenabgeleitetes `ALLOW` weiterhin blockieren.

Damit bleibt die Trennung erhalten: Command-Autorisierung entscheidet, ob der Akteur den Verwaltungs-Command ausführen darf; Approval-Evaluatoren entscheiden, ob eine risikobehaftete Rollenaktivierung/-deaktivierung Rechtewirkung entfaltet.

## Gesicherte Ausführungsgrenze – umgesetzt

`ProjectOSAuthorizedUserManagementChangeService` erbt vom atomaren Basisservice und prüft unmittelbar vor jedem `_commit()` über `ProjectOSUserManagementCommandAuthorization`.

Dadurch gilt dieselbe Grenze automatisch auch für `ProjectOSUserManagementUndoRedoService`, wenn dieser mit dem gesicherten Change-Service betrieben wird.

Nicht autorisierte Commands:

- verändern den Domainzustand nicht;
- erzeugen keinen Audit-Eintrag;
- erzeugen keine Busnachricht;
- erzeugen keinen Command-History-Eintrag.

Die letzte Autorisierungsentscheidung bleibt am gesicherten Service read-only diagnostizierbar – auch bei einer Abweisung.

## Relevante neue Dateien

- `distributions/projectos_user_management_command_context.py`
- `distributions/projectos_user_management_command_history.py`
- `distributions/projectos_user_management_undo_redo.py`
- `distributions/projectos_user_management_command_authorization.py`
- `distributions/projectos_authorized_user_management_change_service.py`
- `distributions/test_projectos_user_management_command_history.py`
- `distributions/test_projectos_user_management_undo_redo.py`
- `distributions/test_projectos_user_management_runtime_history_lifecycle.py`
- `distributions/test_projectos_user_management_command_authorization.py`

## Relevante aktuelle Commits

- `b0f3c1e3` test(projectos): kompensierendes Gewichts-Undo-Redo absichern
- `5278836f` test(projectos): Runtime-Historie bei Load-Recover-Discard-New zurücksetzen
- `07ad0d5f` feat(projectos): konfigurierbare Command-Autorisierung einführen
- `d77d4f33` feat(projectos): Benutzerverwaltungs-Commands vor Commit autorisieren
- `5c71fbb0` test(projectos): Command-Rechte und Vier-Augen-Wirkung absichern
- `31c4934b` fix(projectos): abgewiesene Autorisierungsentscheidung read-only sichtbar halten

## Tests / letzter bestätigter Stand

Bestätigte vollständige grüne Läufe dieses Entwicklungsblocks:

- Run #254 – `command_id` und erste read-only Command-Historie;
- Run #262 – kompensierendes Gewichts-Undo/-Redo;
- Run #268 – Runtime-Historie bei Load/Recover/Discard/New Project;
- Run #271 – Command-Autorisierung und Vier-Augen-Rechtewirkung;
- Run #272 – Diagnosehärtung der Autorisierungsgrenze.

Run #272 gehört zu Commit `31c4934b2078c41db3d0884bb1251c0ee2a677e2` und ist vollständig erfolgreich.

Die vollständigen Läufe umfassen Repository-Health-Check, komplette Pytest-Suite, Z_-Qualitätsprofil, KiCad-Bibliotheksprüfungen und Z_Cockpit-Generierung.

PR #159 bleibt bewusst Draft und der integrierte ProjectOS-Umsetzungsbranch.

## Unmittelbar nächster Umsetzungsschritt

Der nächste Block ist die **produktive Verdrahtung und Nachweisbarkeit der Command-Autorisierung**:

1. zentrale Konfigurationsquelle für `command_permission_map`, `role_permission_map` und `role_risk_class_map` definieren, statt die Maps nur beim Erzeugen des Autorisierers zu übergeben;
2. produktive Benutzerverwaltungs-Einstiegspunkte auf `ProjectOSAuthorizedUserManagementChangeService` verdrahten und einen Guard gegen versehentliche rohe Command-Ausführung außerhalb expliziter Bootstrap-/Testpfade einführen;
3. die erfolgreiche Autorisierungsentscheidung als read-only Nachweis mit dem bestehenden `command_id`/Bus-/Audit-Trace verknüpfen, ohne sie als zweite Domainwahrheit zu persistieren;
4. Z_Cockpit um read-only Command-/Autorisierungsdiagnostik erweitern: letzter Entscheid, erforderliches Recht, Entscheidungsquelle, `DENY`-Blockade, Undo-/Redo-Verfügbarkeit;
5. anschließend die Reversibilitätsmatrix nur dort erweitern, wo eine explizite fachliche Gegenoperation existiert;
6. danach End-to-End-Tests vom konfigurierten Recht über Command-Ausführung, Vier-Augen-Wirksamkeit, Undo/Redo, Audit und Z_Cockpit ergänzen.

## Starttext für einen neuen Chat

> Wir setzen die Entwicklung von `kicad-din-electrical / ProjectOS` fort. Lies zuerst `docs/handover/PROJECTOS_ZWISCHENSTAND_2026-08-09.md` auf Branch `test/load-failure-preserves-state` und prüfe PR #159. Der letzte vollständig grüne dokumentierte Code-Stand ist ProjectOS complete test suite Run #272 für Commit `31c4934b2078c41db3d0884bb1251c0ee2a677e2`. `command_id`, read-only Command-Historie, kompensierendes Undo/Redo für `user_weight_changed`, Runtime-History-Reset sowie die fail-closed Command-Autorisierung mit `DENY`-Vorrang und vorhandener Vier-Augen-Rollenwirkung sind umgesetzt. Fahre mit der zentralen Policy-Konfiguration, der produktiven Verdrahtung des `ProjectOSAuthorizedUserManagementChangeService`, dem Autorisierungsnachweis im Trace und der Z_Cockpit-Diagnostik fort. Alles auf Deutsch. Architecture Freeze 1.0, Single Source of Truth, Configuration before Code, DENY-Vorrang, Benutzergewichtung ohne Autorisierungswirkung und append-only Audit-/Bus-Historie nicht verletzen.
