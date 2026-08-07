# AP-0097 – Audit abgelehnter Bearbeitungsversuche

## Ziel

Abgelehnte Bestätigungs- und Abschlussversuche für die in AP-0095 eingeführte Alarmklasse werden getrennt vom erfolgreichen Bearbeitungsaudit unveränderlich gespeichert.

## Trennung

- `projectos_global_security_staffing_release_alert_attempt_action_audit`: ausschließlich erfolgreiche Bearbeitungen.
- `projectos_global_security_staffing_release_alert_attempt_action_attempt_audit`: ausschließlich abgelehnte Autorisierungsversuche.

## Gespeicherte Daten

Versuchskennung, Alarmkennung, Aktion, Zeitpunkt, ermittelte Person sofern vorhanden, angegebene Rolle, geprüfte Berechtigung, Ablehnungscode, Ablehnungsbegründung und Korrelationskennung.

## Verhalten

Bei fehlender Berechtigung, unpassender Rolle oder fehlender verfügbarer globaler Sicherheitsverantwortung wird genau ein Versuchseintrag angehängt. Alarmstatus und erfolgreiches Bearbeitungsaudit bleiben unverändert. Ist das Versuchsaudit aktiviert, ist eine eindeutige `attempt_id` verpflichtend.

## Fehlerkennungen

- `ERR-KICAD-0220`: Versuchszeitpunkt ohne Zeitzone
- `ERR-KICAD-0221`: Ablehnungscode fehlt
- `ERR-KICAD-0222`: Ablehnungsbegründung fehlt
- `ERR-KICAD-0223`: Versuchskennung bereits vorhanden
- `ERR-KICAD-0224`: Bearbeitungsversuch nicht gefunden
- `ERR-KICAD-0225`: Versuchsaudit aktiviert, Versuchskennung fehlt
