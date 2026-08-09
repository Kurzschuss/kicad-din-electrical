# EE-PROJECTOS-0004 – Read-only Offboarding-/Verantwortungsdiagnostik

Stand: 2026-08-09  
Status: beschlossen  
Geltungsbereich: erster separater ProjectOS-Folgeschritt nach PR #159

## Ausgangslage

PR #159 hat den Benutzer-, Rechte- und Rollen-Lifecycle bis zu Deaktivierung/Reaktivierung, Rechtewiderruf/Regrant sowie freigabegesteuerter Rollenzuweisungs-Beendigung konsolidiert. Historische Tatsachen bleiben append-only und werden weder durch Deaktivierung noch durch Undo/Redo gelöscht.

Eine Benutzer-Deaktivierung beendet deshalb bewusst **nicht** automatisch die fachlichen Verantwortungsbezüge dieses Benutzers. Direkte Rechtezuweisungen und Rollenzuweisungen bleiben historisch erhalten und können bei einer späteren Reaktivierung wieder wirksam werden, sofern ihr eigener Lifecycle nicht beendet wurde.

Vor einem Handover- oder Closure-Modell wird daher zuerst eine rein lesende Diagnose eingeführt.

## Entscheidung

`ProjectOSOffboardingResponsibilityDiagnostic` materialisiert für genau eine `user_id` den aktuell noch aufzulösenden Offboarding-Bestand. Die Diagnose ist **read-only**, **Simulation First** und erzeugt keinen neuen Domainzustand.

Sie betrachtet zum Auswertungszeitpunkt insbesondere:

- noch nicht widerrufene, zeitlich aktive persistierte `ALLOW`-Rechtezuweisungen des Benutzers; rollenabgeleitete Runtime-Rechte werden nicht als zweiter Persistenzbestand gezählt;
- noch nicht wirksam beendete Projektrollenzuweisungen;
- bereits angelegte, aber wegen fehlender/ausstehender/abgelehnter Freigabe noch nicht wirksame Rollenzuweisungs-Beendigungen;
- geplante zukünftige Rollenzuweisungs-Beendigungen;
- bei Notfall-Beendigungen noch offene Nachprüfungszustände, soweit sie aus dem bestehenden Rollen-Beendigungs-Evaluator hervorgehen;
- fehlende Risikokonfiguration für noch offene Rollenzuweisungen als fail-closed Diagnosehinweis.

Die bestehende Vier-Augen- und Risikosemantik wird nicht dupliziert. Für die Wirksamkeit einer Rollenzuweisungs-Beendigung ist ausschließlich `ProjectOSApprovedRoleAssignmentTerminationEvaluator` maßgeblich.

## Auflösungsstatus

Die Diagnose liefert `resolution_required=True`, solange mindestens einer der folgenden Punkte besteht:

- eine fortbestehende persistierte `ALLOW`-Rechtezuweisung;
- eine noch nicht wirksam beendete Projektrollenzuweisung;
- eine noch offene Nachprüfung einer bereits wirksamen Notfall-Beendigung.

Eine Benutzer-Deaktivierung allein setzt `resolution_required` ausdrücklich **nicht** auf `False`.

`resolution_required=False` bedeutet nur: Aus Sicht dieses Diagnosevertrags sind keine der oben genannten Verantwortungsbezüge mehr offen. Es ist **keine** fachliche Offboarding-Closure und keine Löschfreigabe.

## Architekturgrenzen

Die Diagnose:

- verändert weder Benutzerverwaltung noch Projektzustand;
- erzeugt keine Commands;
- erzeugt keine Audit-, Bus- oder Command-History-Einträge;
- führt keinen Rechtewiderruf und keine Rollenbeendigung aus;
- erzeugt keinen Approval-Auftrag und keine Freigabe;
- erzeugt keinen Nachprüfungsentscheid;
- überträgt keine Verantwortung auf einen anderen Benutzer;
- supersediert keine bestehende Freigabe;
- führt keinen Closure-Status ein;
- führt keinen neuen Persistenzbestand ein.

Äußeres ProjectOS-Bundle **v4** und Benutzerverwaltungs-Persistenz **v4** bleiben unverändert.

## Z_Cockpit

`ZCockpitOffboardingResponsibilityView` projiziert denselben Diagnosezustand read-only für UI-/Diagnosezwecke. Die Sicht markiert offene Verantwortungen als `attention_required`, führt aber keinerlei Aktion aus.

## Ausdrücklich nicht Bestandteil dieses Schritts

- Cross-User-Rollen-Handover;
- Handover-Plan oder Nachfolgerzuordnung;
- Approval-Supersession;
- Offboarding-Resolution-/Closure-Workflow;
- automatische Rechtewiderrufe oder Rollenbeendigungen;
- Benutzerverwaltungs-Persistenz v5;
- generisches Undo/Redo von `user_created`.

Diese Funktionen benötigen eigene nachfolgende Architekturentscheidungen und separate PRs.