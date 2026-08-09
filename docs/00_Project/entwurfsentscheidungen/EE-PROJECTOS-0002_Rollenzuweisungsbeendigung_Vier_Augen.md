# EE-PROJECTOS-0002 – Vier-Augen-Vertrag für administrative Rollenzuweisungs-Beendigungen

Stand: 2026-08-09  
Status: beschlossen  
Geltungsbereich: ProjectOS-Benutzerverwaltung auf PR #159

## Ausgangslage

`ProjectOSProjectRoleAssignmentTermination` beendet eine persistierte `ProjectOSUserProjectRole`, ohne Rollenzuweisung, Aktivierungen oder Freigaben historisch zu löschen.

Die Beendigung der **Rollenzuweisung selbst** ist nicht identisch mit `ProjectOSProjectRoleDeactivation`, das lediglich eine konkrete Aktivierung beendet. Deshalb darf die vorhandene Vier-Augen-Regel einer Aktivierungs-Deaktivierung nicht still als Regel der administrativen Zuweisungsbeendigung interpretiert werden.

## Entscheidung

### 1. Vorhandenen Approval-Vertrag erweitern, keine zweite State Machine

Administrative Rollenzuweisungs-Beendigungen verwenden den bestehenden `ProjectOSRoleActionApproval`-Vertrag mit dem expliziten Action-Typ:

`role_assignment_termination`

Der Freigabe-Target wird als

`role_assignment_termination:<termination_id>`

referenziert.

Es entsteht keine zweite Approval-State-Machine.

### 2. Risikoklasse ist Configuration before Code

Die Risikoklasse wird ausschließlich aus der konfigurierten `role_risk_class_map` des betreffenden `role_type` bestimmt.

Fehlt diese Konfiguration, wird **nicht** implizit `low` angenommen. Der Zustand lautet `risk_not_configured`; die Beendigung bleibt fail-closed ohne Rechtewirkung.

### 3. Low/Medium

Für `low` und `medium` ist keine zweite Person erforderlich. Ab `ended_at` darf die Beendigung wirksam werden.

### 4. High/Critical

Für `high` und `critical` gilt:

- ohne Approval-Request: `approval_missing`, keine Rechtewirkung;
- mit ausstehendem Request: `pending_approval`, keine Rechtewirkung;
- Selbstfreigabe wird ignoriert;
- fremde Freigabe: `approved`, Beendigung wirkt ab `ended_at`;
- fremde Ablehnung: `rejected`, keine Rechtewirkung.

Eine gespeicherte High-/Critical-Beendigung ist daher noch keine wirksame Rechtebeendigung.

### 5. Notfall

Ein `emergency=True`-Approval-Request nutzt den bestehenden Status `emergency_pending_review`.

Die Beendigung darf vorläufig wirksam werden, bleibt aber als `post_review_required` sichtbar. Die bestehende Nachprüfungslogik bleibt die einzige Quelle der nachträglichen Notfallbewertung.

### 6. Rechtewirkung

`ProjectOSApprovedRoleAssignmentTerminationEvaluator` ist die zentrale read-only Quelle dafür, welche Rollenzuweisungs-Beendigungen tatsächlich wirksam sind.

Nur diese wirksamen Beendigungen dürfen:

- genehmigte Rollenaktivierungen aus der Rechtewirkung nehmen;
- rollenabgeleitete Command-Rechte entfernen;
- in nachgelagerten Deaktivierungs-/Lifecycle-Auswertungen als beendet gelten;
- in der Command-Diagnostik als `terminated_granting_role_count` erscheinen.

Pending, abgelehnte oder nicht konfigurierte Beendigungen dürfen keine bestehende Rechtewirkung vorzeitig entfernen.

### 7. Konservativer Aktivierungs-Guard

Sobald eine Rollenzuweisungs-Beendigung als fachliches Objekt angelegt wurde, erzeugt die bestehende Command-Grenze keine neue Aktivierung derselben historischen Zuweisung mehr.

Das ist bewusst konservativer als die Rechtewirkung: vorhandene Aktivierungen behalten bei High/Critical ihre Rechte bis zur wirksamen Freigabe; neue Aktivierungszyklen werden nach angelegter administrativer Beendigung nicht mehr eröffnet.

### 8. Z_Cockpit / Simulation First

`ZCockpitRoleAssignmentTerminationView` zeigt read-only:

- vorhandene Beendigungs- und Approval-Zustände;
- `risk_not_configured`, pending, approved, rejected und Notfall-Nachprüfung;
- eine Vorab-Simulation für eine geplante Beendigung;
- die potenziell verlorenen rollenabgeleiteten Rechte;
- ob eine zweite Freigabe erforderlich wäre;
- den nächsten erforderlichen Schritt.

Die Simulation mutiert keinen Domainzustand und wird nicht persistiert.

## Sicherheitsinvarianten

- `DENY` bleibt vor `ALLOW`.
- Benutzergewichtung beeinflusst Autorisierung nicht.
- Audit und Bus bleiben append-only.
- Historische Rollenzuweisungen, Aktivierungen, Freigaben und Beendigungen werden nicht gelöscht.
- Fehlende Risikokonfiguration ist fail-closed.
- High/Critical-Rechtewirkung endet nicht vor wirksamer zweiter Person.
- Notfallwirkung bleibt nachprüfungspflichtig.
- Z_Cockpit bleibt read-only und keine zweite Wahrheit.

## Bestätigung

ProjectOS complete test suite **Run #356** ist vollständig erfolgreich und bestätigt den integrierten Vertrag einschließlich Repository-Health, kompletter Pytest-Suite, Z_-Qualitätsprofil, KiCad-Prüfungen und Z_Cockpit-Generierung.
