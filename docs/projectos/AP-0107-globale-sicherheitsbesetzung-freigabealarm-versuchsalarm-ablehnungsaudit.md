# AP-0107 – Audit abgelehnter Alarmbearbeitungsversuche

AP-0107 ergänzt für die in AP-0105 eingeführte Alarmklasse ein separates, ausschließlich anhängbares Audit abgelehnter `ACKNOWLEDGE`- und `RESOLVE`-Versuche.

## Trennung

Erfolgreiche Bearbeitungen verbleiben im Erfolgs-Audit aus AP-0106. Abgelehnte Versuche werden ausschließlich in `projectos_global_security_staffing_release_alert_attempt_action_attempt_alert_action_attempt_alert_action_attempt_audit` gespeichert.

## Regeln

- Aktiviertes Versuchsaudit verlangt eine eindeutige `attempt_id`.
- Fehlende Berechtigung, falsche Rolle und fehlende globale Verantwortung werden protokolliert.
- Ist keine Person auflösbar, bleibt `actor_id` leer.
- Nach Speicherung wird die ursprüngliche Ausnahme erneut ausgelöst.
- Alarmstatus und Erfolgs-Audit bleiben bei Ablehnungen unverändert.

## Fehlerkennungen

- `ERR-KICAD-0294`: Versuchszeitpunkt ohne Zeitzone
- `ERR-KICAD-0295`: Ablehnungscode fehlt
- `ERR-KICAD-0296`: Ablehnungsbegründung fehlt
- `ERR-KICAD-0297`: Versuchskennung bereits vorhanden
- `ERR-KICAD-0299`: Versuchsaudit aktiv, Versuchskennung fehlt
