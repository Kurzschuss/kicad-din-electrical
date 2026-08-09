# ProjectOS – Zwischenstand / Chat-Übergabe

Stand: 2026-08-09  
Repository: `Kurzschuss/kicad-din-electrical`  
Arbeitsbranch: `test/load-failure-preserves-state`  
Pull Request: #159 – `Test: fehlgeschlagenes Projektladen hält Managerzustand stabil`

## Maßgeblicher Stand

Für Merge- und Testentscheidungen ist ausschließlich der aktuelle Branch-Head maßgeblich. Frühere Zwischenbeschreibungen hatten zeitweise Funktionen genannt, die im tatsächlichen Head nicht vorhanden waren; dieser Handover wurde deshalb auf den realen Codezustand zurückgeführt.

Architecture Freeze 1.0 bleibt maßgeblich. Weiterhin gelten Single Source of Truth, Domain Ownership, Object First, Offline First, Simulation First, Documentation First und Configuration before Code.

Benutzergewichtung beeinflusst Autorisierung nicht. `DENY` hat Vorrang vor `ALLOW`. Audit-/Bus-Nachweise und fachliche Lifecycle-Tatsachen bleiben append-only; Undo/Redo löscht keine historische Tatsache.

## Persistenz

Das äußere Projektbundle bleibt **Bundle v4**.

Der aktuelle Benutzerverwaltungs-Persistenzvertrag steht auf **Version 4**. Versionen 1–3 bleiben lesbar.

Persistiert sind insbesondere:

- Benutzer;
- Benutzer-Deaktivierungen;
- Benutzer-Reaktivierungen;
- Rechtezuweisungen und Rechtewiderrufe;
- Projektrollen und Rollenzuweisungs-Beendigungen;
- Aktivierungen und Deaktivierungen;
- Approval-Requests und Approvals;
- Notfall-Nachprüfungen.

Reproduzierbare Evaluator-, Runtime- und Z_Cockpit-Zustände werden nicht als zweite Domainwahrheit persistiert.

## Benutzeridentitäts-Lifecycle

Umgesetzt sind Benutzer-Deaktivierung und -Reaktivierung als historische Ereignisse derselben `user_id`.

- Benutzer werden nicht gelöscht;
- direkte und rollenabgeleitete Rechte folgen dem chronologischen Benutzer-Lifecycle;
- historische Rechte-, Rollen-, Aktivierungs- und Approval-Bezüge bleiben erhalten;
- mehrere De-/Reaktivierungszyklen sind chronologisch validiert.

`user_created` ist im aktuellen Head **noch nicht** generisch reversibel.

## Rechte-Lifecycle und Undo/Redo

Umgesetzt sind:

- expliziter Rechtewiderruf;
- `permission_regranted` mit neuer `assignment_id` und Lineage zur widerrufenen Vorgänger-Zuweisung;
- `permission_assigned` und `permission_regranted` als identitätswechselnde kompensierbare Fälle;
- Undo erzeugt einen neuen Widerruf;
- Redo erzeugt einen neuen Regrant mit neuer `assignment_id`;
- normale manuelle Widerrufe bleiben historische, nicht reversible Tatsachen;
- `user_weight_changed` bleibt vollständig reversibel.

Es gibt keinen Snapshot-Rollback.

## Rollen-Lifecycle

Umgesetzt sind:

- Rollenzuweisungen;
- Rollenzuweisungs-Beendigungen;
- Vier-Augen-/Risikovertrag für High/Critical-Beendigungen;
- fehlende Risikokonfiguration bleibt fail-closed;
- Rollen-Neu-Zuweisung mit neuer `role_assignment_id` und Lineage zur beendeten Vorgängerrolle;
- read-only `ProjectOSRoleCompensationPlanner` / Z_Cockpit-Sicht für Simulation First.

Generisches synchrones Rollen-Undo bleibt bewusst deaktiviert. High/Critical darf nicht durch einen scheinbar atomaren Undo-Schritt über den mehrstufigen Approval-Lifecycle hinweggehen.

## Im aktuellen Head ausdrücklich nicht umgesetzt

Folgende Funktionen waren in früheren Zwischenbeschreibungen erwähnt, sind aber **nicht Bestandteil des aktuellen Heads**:

- Approval-Supersession;
- Cross-User-Rollen-Handover;
- Offboarding-/Verantwortungsdiagnostik;
- Offboarding-Handover-/Resolution-/Closure-Plan;
- Benutzerverwaltungs-Persistenz v5;
- generisches Undo/Redo von `user_created`.

Diese Punkte dürfen bei Merge, Test oder Dokumentation nicht als vorhanden vorausgesetzt werden.

## Reversibilitätsmatrix

Aktuell vollständig kompensierbar:

- `user_weight_changed`;
- `permission_assigned`;
- `permission_regranted`.

Nicht generisch reversibel bleiben insbesondere:

- `user_created`;
- normale Benutzer-Deaktivierung/-Reaktivierung;
- normale Rechtewiderrufe;
- Rollen-Lifecycle;
- Approval- und Post-Review-Ereignisse.

## Verifizierter Merge-Kandidat

Aktueller vor der Handover-Synchronisierung verifizierter Code-Head:

`262b53b74d5737f313e00a4369de56308885daa2`

Auf diesem Head ist **ProjectOS complete test suite Run #414** vollständig grün.

Die Suite umfasst:

- Repository Health;
- komplette Pytest-Suite;
- Z_-Qualitätsprofil;
- KiCad-Prüfungen;
- Z_Cockpit-Generierung.

PR #159 ist laut GitHub **mergeable** und bleibt bis zur expliziten Merge-Freigabe Draft.

## Empfehlung vor dem Merge

Nach diesem Dokumentationscommit die vollständige ProjectOS-Suite noch einmal auf dem neuen Head prüfen. Wenn auch dieser Dokumentations-Head grün bleibt, ist der PR aus technischer Sicht bereit für einen Merge-Teststand.

Danach sollte zuerst ein manueller Smoke-Test auf `main` erfolgen, bevor weitere Offboarding-/Supersession-Funktionen aufgebaut werden.

## Manueller Smoke-Test nach Merge

Mindestens prüfen:

1. Projekt öffnen/speichern und Bundle-v4-Roundtrip;
2. Benutzer anlegen;
3. Benutzer deaktivieren und Rechtewirkung prüfen;
4. denselben Benutzer reaktivieren und Rechtewiederkehr prüfen;
5. direktes Recht zuweisen, widerrufen und Regrant mit neuer `assignment_id` prüfen;
6. Rechte-Undo/Redo prüfen;
7. Low-Risk-Rolle zuweisen/aktivieren/beenden;
8. High-Risk-Beendigung ohne zweite Freigabe blockiert prüfen;
9. High-Risk-Beendigung mit externer Freigabe wirksam prüfen;
10. Z_Cockpit-/Diagnoseansichten auf Konsistenz prüfen;
11. Audit-/Bus-Historie auf append-only Verhalten prüfen.

## Nächster Entwicklungsschritt nach dem Smoke-Test

Erst nach dem Merge-/Smoke-Test entscheiden, welcher Offboarding-Ausbau als nächster separater PR folgen soll. Offboarding-Supersession, Cross-User-Handover und Closure-Status gehören nicht mehr in diesen Merge-Kandidaten.
