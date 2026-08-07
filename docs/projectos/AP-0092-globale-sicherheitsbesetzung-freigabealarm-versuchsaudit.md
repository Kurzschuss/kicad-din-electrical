# AP-0092 – Audit abgelehnter Bearbeitungsversuche globaler Sicherheitsbesetzungs-Freigabealarme

## Ziel

Abgelehnte Bestätigungs- und Abschlussversuche werden unveränderlich protokolliert, ohne den Alarmstatus oder das Audit erfolgreicher Bearbeitungen zu verändern.

## Trennung

- `projectos_global_security_staffing_release_alert_action_audit`: ausschließlich autorisierte erfolgreiche Bearbeitungen.
- `projectos_global_security_staffing_release_alert_action_attempt_audit`: ausschließlich abgelehnte Autorisierungsversuche.

## Gespeicherte Daten

Versuchskennung, Alarmkennung, Aktion, Zeitpunkt, optional ermittelte Person, angegebene Rolle, geprüfte Berechtigung, Ablehnungscode, Ablehnungsbegründung und Korrelationskennung.

Bei vollständig fehlender Verfügbarkeit globaler Hauptverantwortung und Stellvertretung bleibt `actor_id` leer.

## Verhalten

Bei einer Ablehnung wird zuerst der Versuchseintrag gespeichert und anschließend die ursprüngliche `PermissionError` oder `LookupError` erneut ausgelöst. Alarmstatus und erfolgreiches Bearbeitungsaudit bleiben unverändert.

Ist das Versuchsaudit aktiviert, ist eine eindeutige `attempt_id` verpflichtend.

## Fehlerkennungen

- `ERR-KICAD-0183`: Versuchszeitpunkt ohne Zeitzone
- `ERR-KICAD-0184`: Ablehnungscode fehlt
- `ERR-KICAD-0185`: Ablehnungsbegründung fehlt
- `ERR-KICAD-0186`: Versuchskennung bereits vorhanden
- `ERR-KICAD-0187`: Bearbeitungsversuch nicht gefunden
- `ERR-KICAD-0188`: Versuchsaudit aktiviert, Versuchskennung fehlt

## Sicherheitsgrenze

Das Audit sperrt keine Benutzer, ändert keine Rollen oder Verantwortungen und verändert keine Alarm- oder Freigabeentscheidung.
