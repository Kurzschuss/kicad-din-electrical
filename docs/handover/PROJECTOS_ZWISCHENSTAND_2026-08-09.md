# ProjectOS – Zwischenstand / Chat-Übergabe

Stand: 2026-08-09  
Repository: `Kurzschuss/kicad-din-electrical`  
Arbeitsbranch: `test/load-failure-preserves-state`  
Pull Request: #159 – `Test: fehlgeschlagenes Projektladen hält Managerzustand stabil`

## Architekturgrundlagen

Architecture Freeze 1.0 bleibt maßgeblich. Weiterhin gelten Single Source of Truth, Domain Ownership, Object First, Offline First, Simulation First, Documentation First und Configuration before Code.

Benutzergewichtung beeinflusst Autorisierung nicht. `DENY` hat Vorrang vor `ALLOW`. Audit-/Bus-Nachweise und fachliche Lifecycle-Tatsachen bleiben append-only; Undo/Redo löscht keine historische Tatsache.

## Persistenz

Das äußere Projektbundle bleibt **Bundle v4**. Der Benutzerverwaltungs-Persistenzvertrag bleibt **Version 2**; Version 1 bleibt lesbar.

Persistiert sind insbesondere:

- Rechtezuweisungen und `permission_revocations`;
- Projektrollen und `role_assignment_terminations`;
- Aktivierungen/Deaktivierungen;
- Approval-Requests, Approvals und Nachprüfungen.

Regrant-/Neu-Zuweisungs-Lineage nutzt die bereits persistierten `metadata` der neuen Assignment-Objekte. Es gibt dafür **keinen Schema-Bump** und keinen zweiten Wahrheitsbestand.

## Rechtewiderruf und Rollenzuweisungs-Beendigung

`ProjectOSPermissionRevocation` beendet eine Rechtezuweisung, ohne sie zu löschen.

`ProjectOSProjectRoleAssignmentTermination` beendet eine Rollenzuweisung, ohne Rolle, Aktivierung oder Freigaben historisch zu entfernen.

Administrative High-/Critical-Rollenzuweisungs-Beendigungen nutzen den bestehenden Approval-Action-Typ `role_assignment_termination`. Maßgeblich ist `EE-PROJECTOS-0002_Rollenzuweisungsbeendigung_Vier_Augen.md`.

Fehlende `role_risk_class_map`-Konfiguration bleibt `risk_not_configured` und fail-closed. High/Critical wirken erst nach fremder Freigabe; Selbstfreigabe wird ignoriert; Ablehnung bleibt wirkungslos; Notfall bleibt vorläufig wirksam und nachprüfungspflichtig.

## Regrant mit neuer Rechtezuweisungsidentität – umgesetzt

Der neue produktive Command `permission_regranted` benötigt:

`project.user_management.permission.regrant`

Er erzeugt eine **neue** `ProjectOSPermissionAssignment` und reaktiviert niemals die alte `assignment_id`.

Invarianten:

- genau eine historische Vorgänger-Zuweisung;
- genau ein zugehöriger Widerruf;
- Widerruf muss zum `regranted_at` wirksam sein;
- neue `assignment_id`;
- höchstens ein direkter Regrant-Nachfolger pro Zuweisung;
- Benutzer, Permission, Effekt, Scope, Quelltyp und Risikoklasse werden aus dem Vorgänger übernommen;
- Lineage-Metadaten referenzieren Vorgänger, Widerruf, Zeitpunkt und Akteur;
- alte Zuweisung und Widerruf bleiben erhalten.

## Rollen-Neu-Zuweisung mit neuer Identität – umgesetzt

Der neue produktive Command `project_role_reassigned` benötigt:

`project.user_management.role.reassign`

Er erzeugt eine **neue** `ProjectOSUserProjectRole` mit neuer `role_assignment_id`.

Invarianten:

- genau eine historische Vorgänger-Rollenzuweisung;
- genau eine zugehörige Beendigung;
- Beendigung muss zum `reassigned_at` zeitlich wirksam sein;
- produktiv muss die Beendigung zusätzlich gemäß Vier-Augen-Vertrag approval-wirksam sein;
- fehlende Risikokonfiguration bleibt fail-closed;
- neue `role_assignment_id`;
- höchstens ein direkter Neu-Zuweisungs-Nachfolger pro Vorgänger;
- alte Rollenzuweisung, Beendigung, Aktivierungen und Approvals bleiben erhalten.

## Lineage im Z_Cockpit

`ZCockpitUserManagementLineageView` zeigt read-only:

- Vorgänger-Zuweisung;
- Widerruf bzw. Beendigung;
- neue Nachfolger-Zuweisung;
- Gültigkeit der Lineage-Kette;
- Diagnosefehler als Attention.

Die Sicht verändert keinen Domainzustand und wird nicht persistiert.

## Identitätswechselndes Undo/Redo für Rechtezuweisungen – umgesetzt

`permission_assigned` und `permission_regranted` sind jetzt explizit kompensierbar.

### Undo

Undo erzeugt einen **neuen `permission_revoked`-Command**. Die Zuweisung bleibt erhalten. Der Undo-Widerruf erhält eigene `revocation_id`, `command_id`, Korrelation sowie neue Audit-/Bus-Nachweise.

Benötigtes Recht:

`project.user_management.permission.undo_assign`

### Redo

Redo entfernt den Undo-Widerruf nicht und belebt die alte Assignment-ID nicht wieder. Es erzeugt einen **neuen `permission_regranted`-Command** mit neuer `assignment_id` und Lineage zum gerade widerrufenen Vorgänger.

Benötigtes Recht:

`project.user_management.permission.redo_assign`

Mehrere Undo-/Redo-Zyklen erzeugen eine lineare Folge neuer Assignment- und Widerrufsidentitäten.

Ein **normaler manueller `permission_revoked`** bleibt ausdrücklich nicht reversibel. Nur ein als `history_action=undo` erzeugter Widerrufs-History-Eintrag kann den unmittelbar folgenden Redo-Schritt tragen.

## Reversibilitätsmatrix

Aktuell vollständig kompensierbar sind:

- `user_weight_changed` über Wiederherstellung des vorherigen Gewichts;
- `permission_assigned` über neuen Widerruf / neuen Regrant;
- `permission_regranted` analog über neuen Widerruf / erneuten Regrant.

Nicht generisch reversibel bleiben insbesondere:

- normale `permission_revoked`;
- `project_role_assigned`;
- `project_role_assignment_terminated`;
- `project_role_reassigned`;
- Rollenaktivierungen/-deaktivierungen;
- Approval- und Nachprüfungsereignisse.

Für Rollen ist die Sperre bewusst: High-/Critical-Beendigungen können einen mehrstufigen Approval-/Notfall-/Nachprüfungs-Lifecycle besitzen. Ein synchrones generisches Undo darf diesen Ablauf nicht vortäuschen.

Maßgeblich sind `EE-PROJECTOS-0001`, `EE-PROJECTOS-0002` und `EE-PROJECTOS-0003_Regrant_Lineage_Kompensation.md`.

## Bestätigte vollständige Teststände

- **Run #360** – bereinigter Vier-Augen-/Risikovertrag und Dokumentationsstand vollständig grün;
- **Run #367** – Regrant-/Rollen-Neu-Zuweisung, Lineage, Bundle-Roundtrip und High-Risk-Grenze vollständig grün;
- **Run #373** – identitätswechselndes Rechte-Undo/Redo einschließlich Mehrfachzyklen und Rechteprüfung vollständig grün.

Die vollständige `ProjectOS complete test suite` umfasst Repository Health, komplette Pytest-Suite, Z_-Qualitätsprofil, KiCad-Prüfungen und Z_Cockpit-Generierung.

PR #159 bleibt bewusst **Draft**.

## Unmittelbar nächster Umsetzungsschritt

Als nächstes **Simulation First: read-only Rollen-Kompensationsplan**.

Noch kein mutierendes generisches Rollen-Undo einführen.

Der Plan soll für eine konkrete `project_role_assigned`-/`project_role_reassigned`-Zuweisung vorab beantworten:

1. darf der Akteur `project.user_management.role.terminate` ausführen;
2. welche Risikoklasse gilt aus `role_risk_class_map`;
3. ist eine zweite Person erforderlich;
4. ist eine bereits vorhandene Beendigung approval-wirksam oder nur pending/rejected/not configured;
5. kann die Kompensation synchron abgeschlossen werden oder benötigt sie einen mehrstufigen Approval-/Nachprüfungsablauf;
6. welche effektiven rollenabgeleiteten Rechte würden nach wirksamer Beendigung verloren gehen;
7. welche spätere Neu-Zuweisung wäre als neuer Lifecycle-Vorgang möglich.

Z_Cockpit soll diesen Plan rein lesend anzeigen. Erst danach entscheiden, ob irgendein Rollenfall in generisches Undo/Redo aufgenommen werden darf.

## Starttext für einen neuen Chat

> Wir setzen `kicad-din-electrical / ProjectOS` fort. Lies `docs/handover/PROJECTOS_ZWISCHENSTAND_2026-08-09.md` auf Branch `test/load-failure-preserves-state` und prüfe PR #159. Der letzte vollständig grüne Code-Stand ist ProjectOS complete test suite Run #373. Regrant und Rollen-Neu-Zuweisung erzeugen neue IDs mit persistierter Lineage; High-/Critical-Rollen-Neu-Zuweisung erfordert eine approval-wirksame alte Beendigung. `permission_assigned` und `permission_regranted` sind identitätswechselnd undo-/redo-fähig: Undo erzeugt Widerruf, Redo neuen Regrant mit neuer `assignment_id`; normale Widerrufe bleiben nicht reversibel. Fahre mit einem read-only Rollen-Kompensationsplan fort, ohne mutierendes Rollen-Undo einzuführen. Alles auf Deutsch. Architecture Freeze 1.0, Single Source of Truth, Configuration before Code, DENY-Vorrang und append-only Audit-/Bus-Historie nicht verletzen.
