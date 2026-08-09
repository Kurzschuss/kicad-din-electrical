# EE-PROJECTOS-0001 – Command-Historie und Undo/Redo der Benutzerverwaltung

Stand: 2026-08-09  
Status: beschlossen  
Geltungsbereich: ProjectOS-Benutzerverwaltung auf dem integrierten PR-#159-Branch

## Ausgangslage

`ProjectOSUserManagementChangeService` übernimmt Benutzerverwaltungsänderungen atomar. Erfolgreiche Änderungen können über `ProjectOSUserManagementChangeTraceEmitter` als Bus-/Audit-Nachweis mit `project_id`, Akteur, `correlation_id` und `causation_id` beschrieben werden.

Der allgemeine `DinEditorHistory` arbeitet mit technischen Zustands-Snapshots. Dieses Verfahren darf nicht ungeprüft auf die ProjectOS-Benutzerverwaltung übertragen werden. Benutzerverwaltung enthält fachlich historische Tatsachen wie Rechtezuweisungen, Rechtewiderrufe, Rollenzuweisungen, Rollenzuweisungs-Beendigungen, Rollenaktivierungen, Aktivierungs-Beendigungen, Freigabeentscheidungen und Nachprüfungen. Ein technisches Zurücksetzen eines Snapshots könnte solche Tatsachen aus dem aktuellen Domainzustand entfernen, obwohl ihre Auditspur bestehen bleibt.

## Entscheidung

### 1. Audit und Command-Historie bleiben getrennte Verantwortlichkeiten

Der Audit-/Bus-Nachweis bleibt append-only und ist niemals Ziel einer Undo-/Redo-Operation.

Die Command-Historie ist eine zusätzliche, read-only auswertbare Laufzeitstruktur für erfolgreich ausgeführte Benutzerverwaltungs-Commands. Sie ersetzt weder den Domainzustand noch Audit, Bus oder Persistenz.

Jeder History-Eintrag muss mindestens führen:

- `command_id` als stabile UUID des ausgeführten Commands;
- `project_id`;
- `operation`;
- `actor_user_id`;
- `correlation_id`;
- optional `causation_id`;
- fachliche `reference`;
- Zeitstempel;
- Reversibilitätsstatus;
- für reversible Commands die für eine Kompensation erforderlichen Vorher-/Nachherwerte;
- Verweis auf einen bereits erzeugten Bus-/Audit-Nachweis, sobald vorhanden.

Die Command-Historie ist kein zweiter fachlicher Wahrheitsbestand. Fachlich maßgeblich bleibt `ProjectOSUserManagementState`.

### 2. Undo/Redo ist keine technische Zustandswiederherstellung

Undo/Redo darf `ProjectOSUserManagementState` nicht durch einen historischen Gesamtsnapshot ersetzen.

Ein Undo erzeugt stattdessen einen **neuen fachlichen Command**, der die Wirkung eines früheren reversiblen Commands kompensiert. Dieser neue Command:

- läuft erneut durch Validierung und Autorisierung;
- besitzt eine neue `command_id`;
- besitzt eine neue `correlation_id`;
- referenziert den ursprünglichen Command als Undo-Ziel;
- erzeugt einen neuen Bus-/Audit-Nachweis;
- löscht oder verändert keinen früheren Audit-Eintrag.

Redo ist analog ein neuer fachlicher Command, der die kompensierte Wirkung erneut herstellt. Auch Redo erhält neue Identitäten und eine neue Auditspur.

### 3. Fail-closed-Reversibilität

Nicht jede Benutzerverwaltungsoperation ist automatisch reversibel.

Eine Operation darf nur dann als `reversible=true` markiert werden, wenn sowohl eine fachlich zulässige Gegenoperation für Undo als auch ein fachlich definierter Wiederherstellungspfad für Redo existieren und vollständig validiert werden können. Fehlt einer der beiden Wege, wird Undo/Redo fail-closed nicht angeboten.

Aktuelle Reversibilitätsmatrix:

| Operation | Status | Begründung / Gegenoperation |
|---|---|---|
| `user_weight_changed` | reversibel | neuer Gewichtsänderungs-Command auf den vorherigen bzw. erneuten Wert |
| `user_created` | nicht reversibel | Löschen eines Benutzers wäre keine zulässige historische Kompensation; Archivierungs-/Deaktivierungsmodell fehlt |
| `permission_assigned` | nicht reversibel | Widerruf ist modelliert und könnte eine Wirkung beenden; für vollständiges Undo/Redo fehlt aber ein expliziter Regrant-Vertrag mit neuer Zuweisungsidentität |
| `permission_revoked` | nicht reversibel | Widerruf ist historische Tatsache; Wiedererteilung muss als neuer fachlicher Vorgang erfolgen |
| `project_role_assigned` | nicht reversibel | Rollenzuweisungs-Beendigung ist modelliert; für vollständiges Undo/Redo fehlt aber ein expliziter Neu-Zuweisungs-/Redo-Vertrag mit neuer Identität |
| `project_role_assignment_terminated` | nicht reversibel | Beendigung ist historische Tatsache; eine spätere erneute Zuweisung ist ein neuer fachlicher Vorgang |
| `project_role_activated` | nicht reversibel | eine Deaktivierung beendet die Aktivierung historisch; ein Redo müsste als neue Aktivierung mit neuer Identität und ggf. neuer Freigabe erfolgen |
| `project_role_deactivated` | nicht reversibel | Reaktivierung muss als neue Aktivierung erfolgen und benötigt einen eigenen Vertrag |
| `approval_requested` | nicht reversibel | historische Anforderung darf nicht verschwinden |
| `approval_recorded` | nicht reversibel | Freigabeentscheidung ist historische Tatsache |
| `post_review_completed` | nicht reversibel | Nachprüfung ist historische Tatsache |

Die Matrix wird nur durch explizite fachliche Gegen- und Wiederherstellungsoperationen erweitert.

### 4. Linearer Undo-/Redo-Vertrag

Die erste Umsetzung verwendet einen linearen Verlauf pro Benutzerverwaltungs-Change-Service:

- Undo betrifft ausschließlich den jüngsten noch nicht kompensierten reversiblen Command.
- Es werden keine nicht reversiblen Commands stillschweigend übersprungen.
- Redo ist nur für einen unmittelbar zuvor erfolgreich kompensierten Command zulässig.
- Ein neuer normaler Command nach einem Undo verwirft den Redo-Zweig der Laufzeithistorie.
- Load, Recover, Discard und New Project setzen die Laufzeit-Undo-/Redo-Historie zurück.
- Persistierte Audit-/Bus-Daten bleiben davon unberührt.

### 5. Konsistenzschutz

Vor einem Undo oder Redo muss geprüft werden, ob der aktuelle Domainzustand noch zu der erwarteten Wirkung des History-Eintrags passt. Bei Abweichung wird fail-closed abgebrochen; es gibt kein best-effort Zurücksetzen.

Für `user_weight_changed` bedeutet dies beispielsweise:

- Undo ist nur zulässig, wenn der Benutzer noch existiert und aktuell genau den im History-Eintrag erwarteten Nachherwert besitzt.
- Redo ist nur zulässig, wenn der Benutzer nach erfolgreichem Undo genau den erwarteten Vorherwert besitzt.

### 6. Korrelation und Kausalität

Der ursprüngliche Command behält seine unveränderte Korrelation und Auditspur.

Undo/Redo eröffnet einen neuen Vorgang mit eigener `correlation_id`. Die Beziehung zum ursprünglichen Command wird explizit im Command-/History-Payload geführt. Innerhalb des neuen Undo-/Redo-Vorgangs wird die vorhandene `causation_id`-Kette normal fortgesetzt.

Damit bleiben zwei Fragen getrennt beantwortbar:

1. Welcher ursprüngliche Vorgang hat die fachliche Änderung erzeugt?
2. Welcher spätere Vorgang hat diese Wirkung kompensiert oder erneut hergestellt?

### 7. Persistenz

Die erste Undo-/Redo-Historie ist bewusst **laufzeitbezogen** und wird nicht Bestandteil von Bundle v4. Dadurch bleibt die bestehende Persistenzregel erhalten: Im Benutzerverwaltungsblock werden fachliche Domainobjekte persistiert, nicht reproduzierbare Bedien-/Historienzustände.

Audit-/Bus-Nachweise bleiben wie bisher über den vorhandenen Projekt-/Sync-Kontext erhalten.

Eine spätere persistente Command-Historie benötigt eine eigene versionierte Persistenzentscheidung und darf nicht implizit in `ProjectOSUserManagementState` eingeschoben werden.

### 8. Rechtewiderruf ist Lifecycle, nicht Löschen

`ProjectOSPermissionRevocation` beendet die Wirksamkeit einer bestehenden `ProjectOSPermissionAssignment` ab einem expliziten Zeitpunkt. Die ursprüngliche Zuweisung bleibt vollständig erhalten und referenzierbar.

Der Widerruf ist damit eine fachliche Lifecycle-Tatsache mit eigener Identität, Projekt, Benutzer, Scope, Akteur, Zeitpunkt, Grund und optionaler Quellreferenz. Er darf nicht durch Undo aus dem Zustand entfernt werden.

Diese Gegenoperation reicht allein noch nicht aus, um `permission_assigned` als vollständig reversibel zu markieren: Ein späteres Redo müsste eine **neue** Rechtezuweisung erzeugen, statt den historischen Widerruf zu löschen oder dieselbe `assignment_id` wiederzubeleben. Dieser Regrant-Vertrag ist noch nicht beschlossen und bleibt daher fail-closed.

### 9. Rollenzuweisungs-Beendigung ist eigener Lifecycle

`ProjectOSProjectRoleAssignmentTermination` beendet die Wirksamkeit einer bestehenden `ProjectOSUserProjectRole` ab einem expliziten Zeitpunkt. Die historische Rollenzuweisung und vorhandene Aktivierungs-/Freigabenachweise bleiben erhalten.

Die Beendigung der **Rollenzuweisung** ist ausdrücklich nicht identisch mit `ProjectOSProjectRoleDeactivation`, das ausschließlich eine konkrete **Aktivierung** beendet. Beide Lifecycle-Ebenen bleiben getrennt:

- Aktivierungs-Deaktivierung beschreibt die Rückgabe/Beendigung eines konkreten Aktivierungszustands und behält ihre vorhandene Vier-Augen-Wirksamkeit;
- Rollenzuweisungs-Beendigung beschreibt das administrative Ende der zugrunde liegenden Projektfunktion selbst und läuft als eigener autorisierter Command `project_role_assignment_terminated`;
- ab `ended_at` erzeugt die zugrunde liegende Zuweisung keine direkten oder aktivierungsabgeleiteten Rollenrechte mehr;
- eine vorhandene historische Aktivierung oder Freigabe wird dadurch nicht gelöscht oder umgeschrieben;
- neue Aktivierungen einer bereits zur Beendigung festgelegten Zuweisung werden fail-closed abgewiesen.

Die administrative Beendigung benötigt das explizite Command-Recht `project.user_management.role.terminate`. Ob High-/Critical-Rollenzuweisungs-Beendigungen zusätzlich einen eigenen Vier-Augen-Vertrag benötigen, ist **noch nicht beschlossen** und darf nicht implizit aus der Aktivierungs-Deaktivierungsfreigabe abgeleitet werden. Diese Risikofrage ist ein eigener nächster Architekturpunkt.

Wie beim Rechtewiderruf reicht die Gegenoperation noch nicht für Undo/Redo: Ein Redo von `project_role_assigned` müsste eine **neue Rollenzuweisung mit neuer `role_assignment_id`** erzeugen; die historische Beendigung darf nicht entfernt und die alte Zuweisung nicht wiederbelebt werden.

## Umsetzungsreihenfolge

1. `command_id` in den Benutzerverwaltungs-Command-Kontext aufnehmen.
2. Read-only `ProjectOSUserManagementCommandHistory` für erfolgreiche Commands einführen.
3. Zunächst `user_weight_changed` als vollständig reversiblen Referenzfall implementieren.
4. `undo_user_weight_change` als neuen fachlichen Command mit neuer Korrelation/Auditspur umsetzen.
5. Redo analog als neuen fachlichen Command umsetzen.
6. Reversibilitätsmatrix nur mit vorhandenen expliziten Gegen- **und Wiederherstellungsoperationen** erweitern.
7. Undo/Redo und normale Benutzerverwaltungs-Commands über den Autorisierungs-/Vier-Augen-Vertrag absichern.
8. Rechtewiderruf als eigenen Lifecycle modellieren; `permission_assigned` bleibt bis zu einem expliziten Regrant-Vertrag nicht reversibel.
9. Rollenzuweisungs-Beendigung als eigenen Lifecycle modellieren; `project_role_assigned` bleibt bis zu einem expliziten Neu-Zuweisungs-/Redo-Vertrag nicht reversibel.
10. Für High-/Critical-Rollenzuweisungs-Beendigungen einen eigenen Risikound Freigabevertrag entscheiden, bevor deren Sicherheitsniveau ausgeweitet wird.

## Nicht erlaubt

- Audit-Einträge löschen oder umschreiben;
- Bus-Nachweise rückwirkend entfernen;
- einen kompletten historischen `ProjectOSUserManagementState` blind zurückkopieren;
- Rechtezuweisungen, Rechtewiderrufe, Rollenzuweisungen, Rollenzuweisungs-Beendigungen, Freigaben, Nachprüfungen oder andere Lifecycle-Ereignisse durch Entfernen aus Tupeln "ungeschehen" machen;
- nicht reversible Commands beim Undo still überspringen;
- Undo/Redo ohne neue fachliche Identität und neue Auditspur durchführen.
