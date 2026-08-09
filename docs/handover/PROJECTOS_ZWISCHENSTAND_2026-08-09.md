# ProjectOS – Zwischenstand / Chat-Übergabe

Stand: 2026-08-09  
Repository: `Kurzschuss/kicad-din-electrical`  
Arbeitsbranch: `test/load-failure-preserves-state`  
Pull Request: #159 – `Test: fehlgeschlagenes Projektladen hält Managerzustand stabil`

## Architekturgrundlagen

Architecture Freeze 1.0 bleibt maßgeblich. Weiterhin gelten Single Source of Truth, Domain Ownership, Object First, Offline First, Simulation First, Documentation First und Configuration before Code.

Benutzergewichtung bleibt sichtbar, beeinflusst Autorisierung aber nicht. `DENY` hat Vorrang vor `ALLOW`. Audit-/Bus-Nachweise bleiben append-only. Historische Lifecycle-Tatsachen werden für Undo/Redo niemals aus dem Zustand gelöscht.

## Persistenz

Das äußere Projektbundle bleibt **Bundle v4**.

Der Benutzerverwaltungs-Persistenzvertrag steht aktuell auf **Version 2** und persistiert zusätzlich zu Benutzern/Rechten/Rollen/Aktivierungen/Freigaben zwei explizite Lifecycle-Listen:

- `permission_revocations`;
- `role_assignment_terminations`.

Version 1 bleibt lesbar und wird erst beim expliziten Speichern auf Version 2 geschrieben. Reproduzierbare Runtime-, Z_Cockpit-, Autorisierungs- und Undo/Redo-History-Zustände werden nicht als zweite Domainwahrheit persistiert.

## Rechtewiderruf – umgesetzt

`ProjectOSPermissionRevocation` beendet die Wirksamkeit einer vorhandenen `ProjectOSPermissionAssignment`, ohne die historische Zuweisung zu löschen.

Der atomare Command `permission_revoked` benötigt in der Default-Policy `project.user_management.permission.revoke`.

Wirksame Widerrufe werden von der allgemeinen Autorisierung und der produktiven Command-Autorisierung berücksichtigt. `DENY` bleibt auf den verbleibenden aktiven Quellen vorrangig.

## Rollenzuweisungs-Beendigung – umgesetzt

`ProjectOSProjectRoleAssignmentTermination` beendet eine `ProjectOSUserProjectRole`, ohne die historische Rollenzuweisung, Aktivierungen oder Freigaben zu löschen.

Der atomare Command `project_role_assignment_terminated` benötigt `project.user_management.role.terminate`.

Die Beendigung der **Rollenzuweisung** bleibt fachlich getrennt von `ProjectOSProjectRoleDeactivation`, das lediglich eine konkrete Aktivierung beendet.

## Vier-Augen-Vertrag für administrative Rollenzuweisungs-Beendigungen – beschlossen und umgesetzt

Maßgeblich ist:

`docs/00_Project/entwurfsentscheidungen/EE-PROJECTOS-0002_Rollenzuweisungsbeendigung_Vier_Augen.md`

### Action-Typ

Der vorhandene Approval-Vertrag wurde um den expliziten Action-Typ

`role_assignment_termination`

erweitert. Der Target-Vertrag lautet:

`role_assignment_termination:<termination_id>`

Es gibt **keine zweite Approval-State-Machine**.

### Configuration before Code

Die Risikoklasse der zu beendenden Rolle kommt ausschließlich aus `role_risk_class_map`.

Fehlt die Risikoklasse, wird nicht mehr implizit `low` angenommen. Der Status lautet `risk_not_configured`; die Beendigung bleibt fail-closed ohne Rechtewirkung.

### Wirksamkeit

- `low` / `medium`: keine zweite Person erforderlich, Wirkung ab `ended_at`;
- `high` / `critical` ohne Request: `approval_missing`, keine Rechtewirkung;
- pending Request: `pending_approval`, keine Rechtewirkung;
- Selbstfreigabe wird ignoriert;
- fremde Freigabe: `approved`, Wirkung ab `ended_at`;
- fremde Ablehnung: `rejected`, keine Rechtewirkung;
- Notfall: `emergency_pending_review`, vorläufig wirksam und nachprüfungspflichtig.

`ProjectOSApprovedRoleAssignmentTerminationEvaluator` ist die zentrale read-only Quelle für die freigabewirksamen Beendigungen.

## Rechte-/Command-Wirkung

`ProjectOSApprovedRoleActivationEvaluator` berücksichtigt ausschließlich freigabewirksame Rollenzuweisungs-Beendigungen.

`ProjectOSUserManagementCommandAuthorization` wurde gegen einen früheren Doppelpfad gehärtet:

- eine pending/rejected High-Risk-Beendigung entfernt keine rollenabgeleiteten Command-Rechte;
- erst eine approval-wirksame Beendigung erhöht `terminated_granting_role_count` und kann ein rollenabgeleitetes Recht entfernen;
- blockierte relevante Beendigungen werden separat als `blocked_granting_role_termination_count` diagnostiziert;
- fehlende Risikokonfiguration wird als `role_termination_configuration_required` sichtbar.

Die nachgelagerte Approved-Deactivation-Auswertung verarbeitet Rollenzuweisungs-Beendigungen ebenfalls nur noch über deren eigenen Approval-Vertrag.

## Konservativer Aktivierungs-Guard

Die bestehende Command-Grenze eröffnet keine neue Aktivierung derselben historischen Rollenzuweisung mehr, sobald ein Beendigungsobjekt angelegt wurde.

Das ist bewusst konservativer als die Rechtewirkung: vorhandene High-/Critical-Aktivierungen behalten ihre Rechte bis zur wirksamen zweiten Freigabe; neue Aktivierungszyklen werden nach angelegter administrativer Beendigung nicht mehr eröffnet.

## Z_Cockpit / Simulation First

Neu ist:

`distributions/z_cockpit_role_assignment_termination.py`

`ZCockpitRoleAssignmentTerminationView` zeigt read-only:

- vorhandene Termination-/Approval-Zustände;
- `risk_not_configured`, fehlende/pending Freigabe, Freigabe, Ablehnung und Notfall-Nachprüfung;
- eine Vorab-Simulation einer geplanten Beendigung;
- die potenziell verlorenen rollenabgeleiteten Rechte;
- ob eine zweite Freigabe erforderlich ist;
- den nächsten fachlichen Schritt.

Die bestehende Approved-Activation-Z_Cockpit-Sicht zeigt den Rollenzuweisungs-Beendigungs-Approval-Zustand ebenfalls an.

`ZCockpitUserManagementCommandDiagnosticsView` unterscheidet wirksame und blockierte rollenbezogene Beendigungsursachen.

## Command-/Audit-/Undo-Infrastruktur – weiterhin gültig

Weiterhin umgesetzt:

- expliziter `ProjectOSUserManagementCommandContext` mit `command_id`, Akteur, Korrelation und Undo-/Redo-Bezug;
- atomare Fachmutation über `ProjectOSUserManagementChangeService`;
- produktiver Einstieg über `build_projectos_user_management_runtime()`;
- zentrale `ProjectOSUserManagementCommandPolicy`;
- fail-closed `ProjectOSUserManagementCommandAuthorization`;
- Bus-/Audit-Nachweis über `ProjectOSUserManagementChangeTraceEmitter`;
- read-only Authorization Evidence und Command History;
- Runtime-History-Reset bei Load/Recover/Discard/New Project;
- Undo/Redo als neue kompensierende Fachcommands, niemals Snapshot-Rollback.

Aktuell vollständig reversibler Referenzfall bleibt `user_weight_changed`. Rechtewiderruf und Rollenzuweisungs-Beendigung bleiben historische Tatsachen; Regrant/Neu-Zuweisung sind noch nicht als vollständiger Undo/Redo-Vertrag umgesetzt.

## Neue/angepasste Dateien dieses Sicherheitsblocks

- `distributions/projectos_role_assignment_termination_approval.py`
- `distributions/projectos_user_management_command_authorization.py`
- `distributions/projectos_role_deactivation_approval.py`
- `distributions/z_cockpit_role_assignment_termination.py`
- `distributions/z_cockpit_approved_role_activation.py`
- `distributions/z_cockpit_user_management_command_diagnostics.py`
- `distributions/test_projectos_role_assignment_termination_approval.py`
- `distributions/test_z_cockpit_role_assignment_termination.py`
- angepasste Rollenbeendigungs-/Integrationstests

## Tests / bestätigter Stand

**ProjectOS complete test suite Run #356** ist vollständig erfolgreich.

Bestätigt wurden unter anderem:

- Repository Health;
- komplette Pytest-Suite;
- High-/Critical-Beendigungen ohne/pending Freigabe behalten bestehende Rechtewirkung;
- fremde Freigabe beendet die Rechtewirkung;
- Selbstfreigabe wird ignoriert;
- Ablehnung bleibt wirkungslos;
- Notfall bleibt vorläufig wirksam und nachprüfungspflichtig;
- fehlende Risikokonfiguration ist fail-closed;
- Command-Autorisierung und Z_Cockpit verwenden denselben Wirksamkeitsvertrag;
- Z_-Qualitätsprofil;
- KiCad-Bibliotheks- und Generierungsprüfungen;
- Z_Cockpit-HTML-Generierung.

PR #159 bleibt bewusst **Draft**.

## Unmittelbar nächster Umsetzungsschritt

Als nächstes den **Regrant-/Neu-Zuweisungsvertrag mit neuen Identitäten** umsetzen, ohne historische Lifecycle-Tatsachen zu verändern:

1. `permission_regranted` als neue `ProjectOSPermissionAssignment` mit neuer `assignment_id` und expliziter Lineage zur widerrufenen Zuweisung;
2. `project_role_reassigned` als neue `ProjectOSUserProjectRole` mit neuer `role_assignment_id` und Lineage zur beendeten Zuweisung;
3. keine Wiederbelebung alter IDs;
4. neue Commands über zentrale Policy, Audit/Bus und gesicherte Runtime führen;
5. High-/Critical-Rollen-Neu-Zuweisung nur auf Basis einer tatsächlich wirksamen alten Beendigung zulassen;
6. Lineage read-only im Z_Cockpit zeigen;
7. erst danach prüfen, ob `permission_assigned` oder `project_role_assigned` in der Reversibilitätsmatrix erweitert werden dürfen.

## Starttext für einen neuen Chat

> Wir setzen `kicad-din-electrical / ProjectOS` fort. Lies `docs/handover/PROJECTOS_ZWISCHENSTAND_2026-08-09.md` auf Branch `test/load-failure-preserves-state` und prüfe PR #159. Der letzte bestätigte Code-Stand ist ProjectOS complete test suite Run #356. Der Vier-Augen-Vertrag für administrative Rollenzuweisungs-Beendigungen ist über den vorhandenen Approval-Action-Typ `role_assignment_termination` umgesetzt; fehlende Risikokonfiguration ist fail-closed, High/Critical wirkt erst nach fremder Freigabe, Notfall bleibt nachprüfungspflichtig, und Z_Cockpit kann die Rechteauswirkung vorab read-only simulieren. Fahre mit Regrant/Neu-Zuweisung mit neuen Identitäten fort. Alles auf Deutsch. Architecture Freeze 1.0, Single Source of Truth, Configuration before Code, DENY-Vorrang, Benutzergewichtung ohne Autorisierungswirkung und append-only Audit-/Bus-Historie nicht verletzen.
