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

Persistiert sind insbesondere Rechte-/Rollenzuweisungen, Widerrufe, Rollenzuweisungs-Beendigungen, Aktivierungen/Deaktivierungen, Approval-Requests, Approvals und Nachprüfungen.

Regrant-/Neu-Zuweisungs-Lineage nutzt die bereits persistierten `metadata` der neuen Assignment-Objekte. Es gibt dafür keinen Schema-Bump und keinen zweiten Wahrheitsbestand.

## Vier-Augen-Vertrag für administrative Rollenzuweisungs-Beendigungen

Der vorhandene Approval-Vertrag nutzt den Action-Typ `role_assignment_termination`. Maßgeblich ist `EE-PROJECTOS-0002_Rollenzuweisungsbeendigung_Vier_Augen.md`.

Fehlende `role_risk_class_map`-Konfiguration bleibt `risk_not_configured` und fail-closed. High/Critical wirken erst nach fremder Freigabe; Selbstfreigabe wird ignoriert; Ablehnung bleibt wirkungslos; Notfall bleibt vorläufig wirksam und nachprüfungspflichtig.

## Regrant und Rollen-Neu-Zuweisung mit neuen Identitäten

Umgesetzt sind:

- `permission_regranted` mit neuer `assignment_id` und Lineage zur widerrufenen Vorgänger-Zuweisung;
- `project_role_reassigned` mit neuer `role_assignment_id` und Lineage zur beendeten Vorgänger-Rolle;
- produktive High-/Critical-Rollen-Neu-Zuweisung nur auf Basis einer zeitlich und approval-wirksamen alten Beendigung;
- `ZCockpitUserManagementLineageView` für read-only Vorgänger→Lifecycle→Nachfolger-Ketten;
- Bundle-Roundtrip der Lineage ohne Persistenz-Schema-Bump.

Produktive Rechte:

- `project.user_management.permission.regrant`;
- `project.user_management.role.reassign`.

Alte IDs werden niemals wiederbelebt.

## Identitätswechselndes Rechte-Undo/Redo

`permission_assigned` und `permission_regranted` sind kompensierbar.

Undo erzeugt einen neuen `permission_revoked`-Command und benötigt `project.user_management.permission.undo_assign`.

Redo entfernt den Widerruf nicht, sondern erzeugt einen neuen `permission_regranted`-Command mit neuer `assignment_id` und benötigt `project.user_management.permission.redo_assign`.

Wiederholte Zyklen bilden eine lineare Kette neuer Assignment- und Widerrufsidentitäten. Ein normaler manueller `permission_revoked` bleibt nicht reversibel.

## Rollen-Kompensationsplan – Simulation First umgesetzt

Neu sind:

- `distributions/projectos_role_compensation_plan.py`;
- `distributions/z_cockpit_role_compensation_plan.py`;
- `distributions/test_projectos_role_compensation_plan.py`.

`ProjectOSRoleCompensationPlanner` bewertet für eine konkrete Rollenzuweisung read-only:

1. Autorisierung des Akteurs für `project.user_management.role.terminate`;
2. Risikoklasse aus `role_risk_class_map`;
3. Vier-Augen-Bedarf;
4. vorhandenen Termination-/Approval-Status;
5. offene Notfall-Nachprüfung;
6. synchrone vs. mehrstufige Kompensation;
7. effektive rollenabgeleitete Rechte, die durch die Ziel-Beendigung verloren gehen bzw. gegangen sind;
8. Möglichkeit einer späteren Neu-Zuweisung mit neuer `role_assignment_id`.

Der Rechteverlust wird gegen einen hypothetischen read-only Zustand ohne die Ziel-Beendigung bestimmt. Dadurch bleibt auch nach bereits wirksamer Beendigung nachvollziehbar, welche Rechte durch diese Beendigung entfernt wurden.

Fehlt die Risikokonfiguration, wird die Impact-Auswertung nicht mit einem impliziten `low` approximiert, sondern als unvollständig/fail-closed markiert.

`ZCockpitRoleCompensationPlanView` materialisiert denselben Plan read-only. Planung erzeugt keinerlei Domain-, Audit-, Bus- oder History-Mutation.

### Beschlossene Rollen-Undo-Grenze

`project_role_assigned`, `project_role_assignment_terminated` und `project_role_reassigned` bleiben **außerhalb des generischen synchronen Undo/Redo**.

- Low/Medium kann über einen normalen autorisierten Termination-Command synchron kompensierbar sein.
- High/Critical bleibt ein expliziter mehrstufiger Approval-/ggf. Nachprüfungs-Lifecycle.
- `undo_latest()` darf diesen Workflow nicht als synchronen Einzelschritt vortäuschen.

Maßgeblich ist `EE-PROJECTOS-0003_Regrant_Lineage_Kompensation.md`.

## Reversibilitätsmatrix

Aktuell vollständig kompensierbar:

- `user_weight_changed`;
- `permission_assigned`;
- `permission_regranted`.

Nicht generisch reversibel bleiben normale Widerrufe, Rollen-Lifecycle-, Approval- und Nachprüfungsereignisse sowie aktuell `user_created`.

## Bestätigte vollständige Teststände

- Run #360 – Vier-Augen-/Risikovertrag vollständig grün;
- Run #367 – Regrant/Rollen-Neu-Zuweisung und Lineage vollständig grün;
- Run #373 – identitätswechselndes Rechte-Undo/Redo vollständig grün;
- Run #375 – Dokumentations-Head vollständig grün;
- **Run #378 – read-only Rollen-Kompensationsplan vollständig grün.**

Die `ProjectOS complete test suite` umfasst Repository Health, komplette Pytest-Suite, Z_-Qualitätsprofil, KiCad-Prüfungen und Z_Cockpit-Generierung.

PR #159 bleibt bewusst **Draft**.

## Unmittelbar nächster Umsetzungsschritt

Als nächstes einen **Benutzer-Deaktivierungs-Lifecycle statt Benutzer-Löschung** modellieren.

Ziel: Benutzeridentität und sämtliche historische Rechte-/Rollen-/Auditbezüge bleiben erhalten; ein deaktivierter Benutzer darf ab Wirksamkeitszeitpunkt jedoch keine direkten oder rollenabgeleiteten Rechte mehr ausüben.

Nächste Schritte:

1. `ProjectOSUserDeactivation` als eigenes persistiertes Lifecycle-Objekt mit `deactivation_id`, `project_id`, `user_id`, `deactivated_at`, Akteur, Grund und optionaler Quellreferenz definieren;
2. Benutzerverwaltungs-Persistenz rückwärtskompatibel erweitern; Bundle v4 unverändert lassen;
3. allgemeine und produktive Autorisierung zeitabhängig auf Benutzer-Deaktivierung reagieren lassen;
4. atomaren/gesicherten Command `user_deactivated` mit eigenem Recht, Audit/Bus und Z_Cockpit ergänzen;
5. Benutzer, Rechtezuweisungen, Rollen und deren historische Lifecycle-Tatsachen niemals löschen;
6. `user_created` noch nicht reversibel schalten, solange kein expliziter Reaktivierungsvertrag existiert;
7. danach Reaktivierung derselben `user_id` als eigenen historischen Lifecycle prüfen.

## Starttext für einen neuen Chat

> Wir setzen `kicad-din-electrical / ProjectOS` fort. Lies `docs/handover/PROJECTOS_ZWISCHENSTAND_2026-08-09.md` auf Branch `test/load-failure-preserves-state` und prüfe PR #159. Der letzte vollständig grüne Code-Stand ist ProjectOS complete test suite Run #378. Regrant/Rollen-Neu-Zuweisung mit neuen IDs und Lineage sowie identitätswechselndes Rechte-Undo/Redo sind umgesetzt. Der read-only Rollen-Kompensationsplan ist grün und Rollen bleiben außerhalb generischen synchronen Undo/Redo. Fahre mit einem persistierten Benutzer-Deaktivierungs-Lifecycle statt Benutzer-Löschung fort. Alles auf Deutsch. Architecture Freeze 1.0, Single Source of Truth, Configuration before Code, DENY-Vorrang und append-only Audit-/Bus-Historie nicht verletzen.
