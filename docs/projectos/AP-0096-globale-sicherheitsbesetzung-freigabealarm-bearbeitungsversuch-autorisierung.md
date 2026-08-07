# AP-0096 – Autorisierung und Audit der Bearbeitung von Alarmen zu abgelehnten Alarmbearbeitungsversuchen

## Ziel

Bestätigung und Abschluss der mit AP-0095 eingeführten Alarmklasse werden über die globale Sicherheitsverantwortung autorisiert und zusätzlich unveränderlich auditiert.

## Berechtigungen

- `PERM-KICAD-GLOBAL-SECURITY-STAFFING-RELEASE-ALERT-ATTEMPT-ACKNOWLEDGE`
- `PERM-KICAD-GLOBAL-SECURITY-STAFFING-RELEASE-ALERT-ATTEMPT-RESOLVE`

Bestätigung und Abschluss sind bewusst getrennt berechtigbar. Die angegebene handelnde Rolle muss die jeweils geprüfte Berechtigung tatsächlich erteilen.

## Verantwortungsauflösung

Die aktuelle globale Hauptverantwortung wird zuerst verwendet. Ist sie ausdrücklich nicht verfügbar, kann die aktive Stellvertretung handeln.

## Bearbeitungsaudit

Die Tabelle `projectos_global_security_staffing_release_alert_attempt_action_audit` speichert nur erfolgreiche autorisierte Aktionen. Jeder Eintrag enthält Aktion, Zeitpunkt, Person, Rolle, Berechtigung, verwendete Verantwortung, Begründung und Korrelationskennung.

## Ablehnungsverhalten

Fehlende Benutzerberechtigung oder eine unpassende handelnde Rolle erzeugen eine `PermissionError`. Alarmstatus und Bearbeitungsaudit bleiben unverändert.

## Fehlerkennungen

- `ERR-KICAD-0215`: Auditzeitpunkt ohne Zeitzone
- `ERR-KICAD-0216`: Auditbegründung fehlt
- `ERR-KICAD-0217`: Aktionskennung bereits vorhanden
- `ERR-KICAD-0218`: Benutzerautorisierung lehnt ab
- `ERR-KICAD-0219`: Handelnde Rolle erteilt die Berechtigung nicht

Die Bearbeitung verändert keine Benutzer, Rollen, Verantwortungen oder fachlichen Freigabeentscheidungen.
