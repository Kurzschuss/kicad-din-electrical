# AP-0101 – Autorisierung und Bearbeitungsaudit

## Ziel

Bestätigung und Abschluss der in AP-0100 eingeführten Alarmklasse werden über die globale Sicherheitsverantwortung autorisiert und zusätzlich unveränderlich auditiert.

## Berechtigungen

- `PERM-KICAD-GLOBAL-SECURITY-STAFFING-RELEASE-ALERT-ATTEMPT-ACTION-ATTEMPT-ACKNOWLEDGE`
- `PERM-KICAD-GLOBAL-SECURITY-STAFFING-RELEASE-ALERT-ATTEMPT-ACTION-ATTEMPT-RESOLVE`

Beide Aktionen sind bewusst getrennt berechtigbar. Eine Benutzerberechtigung allein genügt nicht; die angegebene handelnde Rolle muss die jeweilige Berechtigung tatsächlich erteilen.

## Verantwortungsauflösung

Die globale Hauptverantwortung wird zuerst verwendet. Bei ausdrücklich dokumentierter Nichtverfügbarkeit übernimmt die Stellvertretung. Projektrollen oder künstliche Projektkennungen werden nicht verwendet.

## Bearbeitungsaudit

Erfolgreiche Aktionen werden nur anhängbar in `projectos_global_security_staffing_release_alert_attempt_action_attempt_alert_action_audit` gespeichert. Erfasst werden Aktions- und Alarmkennung, Aktion, Zeitpunkt, Person, Rolle, Berechtigung, verwendete Verantwortung, Begründung und Korrelationskennung.

## Ablehnungsverhalten

Fehlende Benutzerberechtigung oder eine unpassende Rolle führen zu `PermissionError`. Alarmstatus und Erfolgs-Audit bleiben unverändert.

## Fehlerkennungen

- `ERR-KICAD-0252`: Auditzeitpunkt ohne Zeitzone
- `ERR-KICAD-0253`: Auditbegründung fehlt
- `ERR-KICAD-0254`: Aktionskennung bereits vorhanden
- `ERR-KICAD-0255`: Benutzerautorisierung lehnt ab
- `ERR-KICAD-0256`: handelnde Rolle erteilt die Berechtigung nicht

## Grenzen

Die Autorisierung verändert keine Benutzer, Rollen oder Verantwortungen. Automatische Sperren und automatische Eskalationen sind nicht Bestandteil dieses Arbeitspakets.
