# AP-0102 – Audit abgelehnter Bearbeitungsversuche für AP-0100-Alarme

## Ziel

Abgelehnte Bestätigungs- und Abschlussversuche der in AP-0100 eingeführten Alarmklasse werden getrennt von erfolgreichen Bearbeitungen unveränderlich protokolliert.

## Trennung der Historien

- `projectos_global_security_staffing_release_alert_attempt_action_attempt_alert_action_audit` enthält ausschließlich erfolgreiche autorisierte Bearbeitungen.
- `projectos_global_security_staffing_release_alert_attempt_action_attempt_alert_action_attempt_audit` enthält ausschließlich abgelehnte Autorisierungsversuche.

Ein abgelehnter Versuch ändert weder den Alarmstatus noch das Erfolgs-Audit.

## Gespeicherte Daten

Jeder Versuch enthält Versuchs- und Alarmkennung, Aktion, Zeitpunkt, die gegebenenfalls ermittelte Person, handelnde Rolle, geprüfte Berechtigung, Ablehnungscode, Ablehnungsbegründung und Korrelationskennung.

Ist das Versuchsaudit am Dienst aktiviert, ist eine eindeutige `attempt_id` verpflichtend. Eine allgemeine Benutzerfreigabe ersetzt weiterhin nicht die Prüfung der tatsächlich berechtigenden Rolle.

## Fehlerkennungen

- `ERR-KICAD-0257`: Versuchszeitpunkt ohne Zeitzone
- `ERR-KICAD-0258`: Ablehnungscode fehlt
- `ERR-KICAD-0259`: Ablehnungsbegründung fehlt
- `ERR-KICAD-0260`: Versuchskennung bereits vorhanden
- `ERR-KICAD-0261`: Bearbeitungsversuch nicht gefunden
- `ERR-KICAD-0262`: Versuchsaudit aktiviert, Versuchskennung fehlt

## Grenzen

Das Audit sperrt keine Benutzer, entzieht keine Rollen und verändert keine globale Sicherheitsverantwortung. Es dokumentiert ausschließlich den abgelehnten technischen Autorisierungsversuch.
