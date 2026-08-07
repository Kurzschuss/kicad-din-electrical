# AP-0112 – Separates Audit abgelehnter Alarmbearbeitungsversuche

## Ziel

Abgelehnte `ACKNOWLEDGE`- und `RESOLVE`-Versuche der in AP-0110 eingeführten Alarmklasse werden getrennt vom Erfolgs-Audit protokolliert.

## Regeln

- Das Audit ist ausschließlich anhängbar.
- Fehlende Berechtigung, eine unpassende Rolle und fehlende globale Verantwortung werden erfasst.
- Bei fehlender Verantwortung bleibt `actor_id` leer.
- Bei einer Ablehnung bleiben Alarmstatus und Erfolgs-Audit unverändert.
- Die ursprüngliche Ausnahme wird nach erfolgreicher Protokollierung erneut ausgelöst.
- Ist das Versuchsaudit aktiviert, ist `attempt_id` verpflichtend.

## Persistenz

Tabelle: `projectos_global_security_staffing_release_alert_attempt_action_attempt_alert_action_attempt_alert_action_attempt_alert_action_attempt_audit`

Gespeichert werden Versuchskennung, Alarmkennung, Aktion, Zeitpunkt, optionale Person, handelnde Rolle, geprüfte Berechtigung, Ablehnungscode, Ablehnungsbegründung und Korrelationskennung.

## Fehlerkennungen

- `ERR-KICAD-0331`: Versuchszeitpunkt ohne Zeitzone
- `ERR-KICAD-0332`: Ablehnungscode fehlt
- `ERR-KICAD-0333`: Ablehnungsbegründung fehlt
- `ERR-KICAD-0334`: Versuchskennung bereits vorhanden
- `ERR-KICAD-0335`: Versuchsaudit aktiviert, aber Versuchskennung fehlt
