# EE-PROJECTOS-0003 – Regrant, Neu-Zuweisung und identitätswechselnde Kompensation

Stand: 2026-08-09  
Status: beschlossen  
Geltungsbereich: ProjectOS-Benutzerverwaltung auf PR #159

## Entscheidung

Historische Rechte- und Rollenzuweisungen werden nach Widerruf bzw. Beendigung niemals wiederbelebt.

Ein erneuter fachlicher Zustand wird ausschließlich durch ein **neues Domainobjekt mit neuer Identität** hergestellt.

## Rechte-Regrant

`permission_regranted` erzeugt eine neue `ProjectOSPermissionAssignment`.

Verbindliche Invarianten:

- neue `assignment_id`;
- genau eine historische Vorgänger-Zuweisung;
- genau ein zu dieser Vorgänger-Zuweisung gehörender Widerruf;
- der Widerruf muss zum `regranted_at` wirksam sein;
- höchstens ein direkter Regrant-Nachfolger pro Zuweisung;
- Benutzer, Recht, Effekt, Scope, Quelltyp und Risikoklasse werden aus dem Vorgänger übernommen;
- Lineage wird in den persistierten Assignment-Metadaten geführt;
- alte Zuweisung und Widerruf bleiben unverändert erhalten.

Reservierte Lineage-Felder:

- `lineage_type=permission_regrant`
- `predecessor_assignment_id`
- `predecessor_revocation_id`
- `regranted_at`
- `regranted_by_user_id`

Der produktive Command benötigt `project.user_management.permission.regrant`.

## Rollen-Neu-Zuweisung

`project_role_reassigned` erzeugt eine neue `ProjectOSUserProjectRole`.

Verbindliche Invarianten:

- neue `role_assignment_id`;
- genau eine historische Vorgänger-Rollenzuweisung;
- genau eine dazugehörige Beendigung;
- die Beendigung muss zum `reassigned_at` zeitlich wirksam sein;
- im produktiven Pfad muss sie zusätzlich gemäß `EE-PROJECTOS-0002` approval-wirksam sein;
- fehlende Risikokonfiguration bleibt fail-closed;
- höchstens ein direkter Neu-Zuweisungs-Nachfolger pro historischer Rollenzuweisung;
- Projekt, Benutzer, Rollentyp und Scope werden aus dem Vorgänger übernommen;
- alte Rollenzuweisung, Beendigung, Aktivierungen und Freigaben bleiben erhalten.

Reservierte Lineage-Felder:

- `lineage_type=project_role_reassignment`
- `predecessor_role_assignment_id`
- `predecessor_termination_id`
- `reassigned_at`
- `reassigned_by_user_id`

Der produktive Command benötigt `project.user_management.role.reassign`.

## Persistenz

Es wird **kein neuer Persistenzbestand** eingeführt.

Die Lineage liegt in den bereits persistierten `metadata` der neuen `ProjectOSPermissionAssignment` bzw. `ProjectOSUserProjectRole`. Deshalb bleiben äußeres Bundle v4 und Benutzerverwaltungs-Persistenzversion 2 unverändert.

`ZCockpitUserManagementLineageView` materialisiert die Vorgänger→Lifecycle→Nachfolger-Ketten ausschließlich read-only.

## Identitätswechselndes Undo/Redo von Rechtezuweisungen

`permission_assigned` und `permission_regranted` sind jetzt explizit kompensierbar.

### Undo

Undo einer aktiven Rechtezuweisung:

1. löscht die Zuweisung nicht;
2. erzeugt einen neuen `permission_revoked`-Command;
3. erzeugt neue `revocation_id`, `command_id` und `correlation_id`;
4. nutzt das separate Recht `project.user_management.permission.undo_assign`;
5. erzeugt neue Audit-/Bus-Nachweise.

Ein normaler manueller `permission_revoked` bleibt nicht reversibel. Nur ein als `history_action=undo` erzeugter Widerrufs-History-Eintrag trägt den unmittelbar folgenden linearen Redo-Zustand.

### Redo

Redo nach einem Undo-Widerruf:

1. entfernt den Widerruf nicht;
2. reaktiviert die alte `assignment_id` nicht;
3. erzeugt über `permission_regranted` eine neue `assignment_id`;
4. verknüpft sie per Lineage mit der gerade widerrufenen Vorgänger-Zuweisung;
5. nutzt das separate Recht `project.user_management.permission.redo_assign`;
6. erzeugt neue Audit-/Bus-Nachweise.

Mehrere Undo-/Redo-Zyklen bilden daher eine lineare Kette neuer Zuweisungs- und Widerrufsidentitäten.

## Rollen bleiben außerhalb des generischen synchronen Undo/Redo

Obwohl Beendigung und Neu-Zuweisung vorhanden sind, wird `project_role_assigned` **nicht** automatisch reversibel geschaltet.

Grund: Bei High-/Critical-Rollen kann die Beendigung eine zweite Freigabe und ggf. einen Notfall-/Nachprüfungs-Lifecycle benötigen. Ein generischer synchroner `undo_latest()`-Aufruf darf keinen mehrstufigen Approval-Vorgang vortäuschen oder halb abgeschlossen hinterlassen.

Der nächste Schritt ist deshalb Simulation First: ein read-only Rollen-Kompensationsplan, der vorab Autorisierung, Risikoklasse, Vier-Augen-Bedarf, Synchronität und erwarteten Rechteverlust bewertet.

## Nicht erlaubt

- alte `assignment_id` oder `role_assignment_id` wiederverwenden;
- Widerrufe oder Beendigungen für Redo löschen;
- Lineage als separaten konkurrierenden Persistenzbestand führen;
- High-/Critical-Rollen-Neu-Zuweisung auf einer nur angelegten, aber nicht approval-wirksamen Beendigung aufbauen;
- Rollen-Undo synchron anbieten, solange der Approval-Lifecycle nicht vollständig als Kompensationsplan bewertet ist.
