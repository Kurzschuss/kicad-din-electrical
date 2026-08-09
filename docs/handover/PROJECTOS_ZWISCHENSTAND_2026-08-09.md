# ProjectOS – Zwischenstand / Chat-Übergabe

Stand: 2026-08-09
Repository: `Kurzschuss/kicad-din-electrical`
Arbeitsbranch: `test/load-failure-preserves-state`
Pull Request: #159 – `Test: fehlgeschlagenes Projektladen hält Managerzustand stabil`

## Architekturgrundlagen

Architecture Freeze 1.0 bleibt maßgeblich. Weiterhin gelten Single Source of Truth, Domain Ownership, Object First, Offline First, Simulation First, Documentation First und Configuration before Code.

Benutzergewichtung bleibt sichtbar, beeinflusst Autorisierung aber nicht. `DENY` hat Vorrang vor `ALLOW`. Audit-/Bus-Nachweise bleiben append-only. Historische Lifecycle-Tatsachen werden für Undo/Redo niemals aus dem Zustand gelöscht.

## Persistenz und Projektidentität

Bundle v4 bleibt unverändert der äußere Projektvertrag mit `session`, `sync_log`, stabiler `project_id` und fachlichem `user_management`-Block.

Der Benutzerverwaltungs-Persistenzvertrag steht jetzt auf **Version 2**. Version 1 bleibt lesbar. Version-1-Daten werden beim Laden nur im Speicher normalisiert; die Datei bleibt unverändert, bis ausdrücklich gespeichert wird. Beim expliziten Save wird der Benutzerverwaltungsblock auf Version 2 geschrieben.

Version 2 ergänzt zwei fachliche Lifecycle-Listen:

- `permission_revocations`;
- `role_assignment_terminations`.

Bundle-v4-Migration und Benutzerverwaltungs-v1→v2-Migration sind im Z_Cockpit getrennte Zustände und erzeugen getrennte, navigierbare Attention-Hinweise.

## Rechtewiderruf – umgesetzt

`ProjectOSPermissionRevocation` beendet die Wirksamkeit einer vorhandenen `ProjectOSPermissionAssignment`, ohne die historische Zuweisung zu löschen.

Der Widerruf führt:

- eigene `revocation_id`;
- `assignment_id`;
- `project_id`;
- Benutzer und Scope;
- `revoked_at`;
- `revoked_by_user_id`;
- Grund;
- optionale Quellreferenz und Metadaten.

Regeln:

- höchstens ein Widerruf pro Rechtezuweisung;
- Projekt, Benutzer und Scope müssen zur Zuweisung passen;
- der handelnde Benutzer muss existieren;
- vor `revoked_at` kann die Zuweisung noch wirken;
- ab `revoked_at` wird sie als widerrufen/inaktiv ausgewiesen;
- `DENY`-Vorrang bleibt für alle weiterhin aktiven Quellen unverändert.

Der atomare Command heißt `permission_revoked` und benötigt in der Default-Policy `project.user_management.permission.revoke`.

Er läuft über dieselbe gesicherte Runtime, erzeugt Bus-/Audit-/Command-History-Nachweis und bleibt selbst nicht reversibel.

Ein widerrufenes Command-Recht kann keinen späteren Benutzerverwaltungs-Command mehr autorisieren. Eine abgewiesene Folgeaktion erzeugt keine Domain-, Audit-, Bus- oder History-Mutation.

Z_Cockpit unterscheidet eine Widerrufsblockade ausdrücklich von „Recht nie erteilt“ und zeigt die widerrufene Quelle read-only an.

## Rollenzuweisungs-Beendigung – umgesetzt

`ProjectOSProjectRoleAssignmentTermination` beendet die zugrunde liegende `ProjectOSUserProjectRole`, ohne die historische Rollenzuweisung oder ihre früheren Aktivierungs-/Freigabenachweise zu löschen.

Die Beendigung führt:

- eigene `termination_id`;
- `role_assignment_id`;
- `project_id`;
- Benutzer und Scope;
- `ended_at`;
- `ended_by_user_id`;
- Grund;
- optionale Quellreferenz und Metadaten.

Regeln:

- höchstens eine Beendigung pro Rollenzuweisung;
- Projekt, Benutzer und Scope müssen zur Rollenzuweisung passen;
- der handelnde Benutzer muss existieren;
- vor `ended_at` kann die Rollenzuweisung noch wirken;
- ab `ended_at` liefert sie keine Rollenrechte mehr;
- beendete Rollen werden im Z_Cockpit als eigene Lifecycle-Gruppe gezeigt und nicht zusätzlich als bloß „inaktiv“ dupliziert;
- vorhandene Aktivierungen und Freigaben bleiben historisch erhalten;
- eine bereits zur Beendigung festgelegte Rollenzuweisung erhält keine neuen Aktivierungen mehr.

Der atomare Command heißt `project_role_assignment_terminated` und benötigt in der Default-Policy `project.user_management.role.terminate`.

### Wichtige Trennung zur Aktivierungs-Deaktivierung

`ProjectOSProjectRoleAssignmentTermination` beendet die **Rollenzuweisung selbst**.

`ProjectOSProjectRoleDeactivation` beendet dagegen nur eine konkrete **Aktivierung**. Die bestehende Vier-Augen-Logik für High-/Critical-Aktivierungs-Deaktivierungen bleibt unverändert und ist weiterhin die einzige Quelle der dortigen Freigabewirksamkeit.

Die neue Rollenzuweisungs-Beendigung ist derzeit ein separat autorisierter administrativer Lifecycle-Command. Sie darf nicht still als dieselbe fachliche Operation wie eine Aktivierungsrückgabe behandelt werden.

## Rollenrechte und Vier-Augen-Wirkung

Die Rollen-, Aktivierungs-, Approved-Activation-, Deaktivierungs- und Approved-Deactivation-Auswertungen berücksichtigen jetzt wirksame Rollenzuweisungs-Beendigungen.

Dadurch gilt:

- eine genehmigte High-/Critical-Aktivierung erzeugt vor der Zuweisungsbeendigung weiterhin ihre konfigurierten Rechte;
- ab wirksamer Zuweisungsbeendigung entstehen daraus keine Rollenrechte mehr;
- die historische Aktivierung und Freigabe bleiben unverändert nachweisbar;
- ein rollenabgeleitetes Benutzerverwaltungsrecht verschwindet ebenfalls aus der gesicherten Command-Autorisierung.

`ProjectOSUserManagementCommandAuthorization` weist zusätzlich aus, wenn genau eine für das aktuell benötigte Recht relevante Rollenzuweisung beendet wurde (`terminated_granting_role_count`).

`ZCockpitUserManagementCommandDiagnosticsView` zeigt daraus `role_termination_blocked` getrennt von `revocation_blocked` und `deny_blocked`.

## Command-, Audit- und Runtime-Infrastruktur

Weiterhin umgesetzt und unverändert gültig:

- `ProjectOSUserManagementCommandContext` mit `command_id`, Akteur, Korrelation, optionaler Kausalität und Undo-/Redo-Bezug;
- atomare Fachänderung über `ProjectOSUserManagementChangeService`;
- produktiver Einstieg über `build_projectos_user_management_runtime()`;
- fail-closed `ProjectOSUserManagementCommandAuthorization`;
- zentrale `ProjectOSUserManagementCommandPolicy`;
- `ProjectOSUserManagementChangeTraceEmitter` für Bus/Audit;
- `command_id` direkt im persistierten `DinSyncLog`;
- read-only `ProjectOSUserManagementAuthorizationEvidence`;
- read-only `ProjectOSUserManagementCommandHistory`;
- Runtime-Reset bei Load, Recover, Discard und New Project.

Fehlgeschlagene oder nicht autorisierte Commands verändern weder Domainzustand noch Audit, Bus oder Command-Historie.

## Undo/Redo und Reversibilitätsmatrix

Undo/Redo bleibt eine neue kompensierende Fachänderung und niemals Snapshot-Rollback.

Aktuell ist ausschließlich `user_weight_changed` vollständig reversibel.

Explizit nicht reversibel bleiben jetzt auch:

- `permission_assigned`: Widerruf existiert, aber für vollständiges Undo/Redo fehlt ein Regrant-Vertrag mit neuer Zuweisungsidentität;
- `permission_revoked`: historische Tatsache;
- `project_role_assigned`: Zuweisungsbeendigung existiert, aber für vollständiges Undo/Redo fehlt ein Neu-Zuweisungs-/Redo-Vertrag mit neuer Rollenidentität;
- `project_role_assignment_terminated`: historische Tatsache;
- Aktivierungs-/Deaktivierungs-, Freigabe- und Nachprüfungsvorgänge gemäß Entwurfsentscheidung.

Maßgeblich ist `docs/00_Project/entwurfsentscheidungen/EE-PROJECTOS-0001_Command_Historie_Undo_Redo.md`.

## Z_Cockpit

Read-only integriert sind jetzt insbesondere:

- Rechteherkunft samt wirksamen Widerrufen;
- Rollenzuweisungen samt Beendigungen;
- Aktivierungs-/Deaktivierungs- und Vier-Augen-Sichten mit beendeten Zuweisungen;
- Command-/Autorisierungsdiagnostik mit DENY-, Widerrufs- und Rollenbeendigungsursache;
- Konsistenzketten `user→permission→revocation` und `user→role→termination→activation→deactivation`;
- Persistenzzähler für beide neuen Lifecycle-Arten;
- getrennte Migration von Bundle-Version und Benutzerverwaltungs-Persistenzversion.

Simulationen bleiben read-only und berücksichtigen die vorhandenen Beendigungen, statt sie für hypothetische Zustände zu vergessen.

## Relevante neue Dateien dieses Lifecycle-Blocks

- `distributions/projectos_permission_revocation.py`
- `distributions/projectos_role_assignment_termination.py`
- `distributions/test_projectos_permission_revocation.py`
- `distributions/test_projectos_permission_revocation_integration.py`
- `distributions/test_projectos_role_assignment_termination.py`
- `distributions/test_projectos_role_assignment_termination_integration.py`

## Tests / letzter bestätigter Stand

Bestätigte vollständige grüne Läufe dieses Fortsetzungsblocks:

- Run #303 – Rechtewiderrufs-Kern;
- Run #307 – Bundle-/Command-Widerrufsintegration;
- Run #309 – Benutzerverwaltungs-v1→v2-Migrationsdiagnose;
- Run #313 – getrennte Attention-Migration;
- Run #331 – Rollenzuweisungs-Beendigungs-Kern;
- Run #332 – Bundle- und rollenabgeleitete Command-Rechteintegration;
- Run #336 – Z_Cockpit-/Simulationsadapter;
- **Run #342 – kombinierter aktueller Lifecycle-/Diagnose-/Entwurfsstand vollständig erfolgreich.**

Die vollständigen Läufe umfassen Repository-Health-Check, komplette Pytest-Suite, Z_-Qualitätsprofil, KiCad-Bibliotheksprüfungen, generierte Referenzen/Reports/Previews und Z_Cockpit-Generierung.

PR #159 bleibt bewusst Draft und der integrierte ProjectOS-Umsetzungsbranch.

## Unmittelbar nächster Umsetzungsschritt

Der nächste Architekturblock ist die **Risikound Vier-Augen-Regel für administrative Rollenzuweisungs-Beendigungen**.

Aktuell ist `project_role_assignment_terminated` durch das explizite Command-Recht `project.user_management.role.terminate` geschützt. Für High-/Critical-Rollen ist aber noch nicht beschlossen, ob zusätzlich eine zweite Person erforderlich sein muss.

Nächste Schritte:

1. Configuration-before-Code: Risikoklasse der zu beendenden Rollenzuweisung eindeutig bestimmen;
2. entscheiden, ob High-/Critical-Zuweisungsbeendigungen über den vorhandenen `ProjectOSRoleActionApproval`-Vertrag erweitert werden können oder einen eigenen Approval-Action-Typ benötigen;
3. keine zweite Approval-State-Machine einführen;
4. bei erforderlicher Freigabe die Rechtewirkung fail-closed erst nach wirksamer zweiter Entscheidung beenden;
5. Notfallverhalten und nachträgliche Prüfung ausdrücklich entscheiden;
6. Z_Cockpit vor Ausführung die Rechteauswirkung read-only simulieren lassen;
7. End-to-End-Test für High-Risk-Zuweisungsbeendigung → Freigabe → Rechteentzug → Audit/Bus → Z_Cockpit ergänzen.

Wichtig: Die vorhandene Vier-Augen-Regel einer **Aktivierungs-Deaktivierung** darf nicht still auf die **Rollenzuweisungs-Beendigung** umgedeutet werden. Der Vertrag muss explizit beschlossen und nachvollziehbar bleiben.

## Starttext für einen neuen Chat

> Wir setzen `kicad-din-electrical / ProjectOS` fort. Lies zuerst `docs/handover/PROJECTOS_ZWISCHENSTAND_2026-08-09.md` auf Branch `test/load-failure-preserves-state` und prüfe PR #159. Der letzte vollständig grüne dokumentierte Code-Stand ist ProjectOS complete test suite Run #342. Rechtewiderruf und Rollenzuweisungs-Beendigung sind als getrennte persistierte Lifecycle-Tatsachen in Benutzerverwaltungs-Persistenzversion 2 umgesetzt; Version 1 bleibt lesbar, Bundle v4 bleibt unverändert. Historische Zuweisungen werden nicht gelöscht. Command-Autorisierung, Audit/Bus, Z_Cockpit und Simulationen berücksichtigen beide Lifecycle-Arten. Fahre mit der expliziten Risikound Vier-Augen-Regel für administrative High-/Critical-Rollenzuweisungs-Beendigungen fort. Alles auf Deutsch. Architecture Freeze 1.0, Single Source of Truth, Configuration before Code, DENY-Vorrang, Benutzergewichtung ohne Autorisierungswirkung und append-only Audit-/Bus-Historie nicht verletzen.
