# AP-0087 – Audit abgelehnter globaler Besetzungsfreigabeversuche

## Ziel

Abgelehnte Versuche, eine technische Freigabeentscheidung zur globalen Sicherheitsbesetzung zu speichern, werden in einer getrennten, nur anhängbaren SQLite-Historie protokolliert.

## Trennung

- `projectos_global_security_staffing_release_audit` enthält ausschließlich tatsächlich autorisierte fachliche Entscheidungen.
- `projectos_global_security_staffing_release_attempt_audit` enthält ausschließlich abgelehnte Autorisierungsversuche.

Ein Versuchsaudit kann daher niemals als Freigabe interpretiert werden.

## Ablauf

Bei fehlender Berechtigung, falscher handelnder Rolle oder nicht verfügbarer globaler Verantwortung wird genau ein Versuchseintrag gespeichert und anschließend die ursprüngliche Ausnahme erneut ausgelöst. Die Freigabehistorie bleibt unverändert.

Ist das Versuchsaudit am Service aktiviert, muss für den Aufruf eine eindeutige `attempt_id` angegeben werden.

## Daten

Gespeichert werden Versuchskennung, Zeitpunkt, ermittelte handelnde Person sofern vorhanden, angegebene Rolle, geprüfte Berechtigung, Ablehnungscode, Ablehnungsbegründung und Korrelationskennung.

## Fehlerkennungen

- `ERR-KICAD-0148` Versuchszeitpunkt ohne Zeitzone
- `ERR-KICAD-0149` Ablehnungscode fehlt
- `ERR-KICAD-0150` Ablehnungsbegründung fehlt
- `ERR-KICAD-0151` Versuchskennung bereits vorhanden
- `ERR-KICAD-0152` Versuch nicht gefunden
- `ERR-KICAD-0153` Versuchsaudit aktiviert, aber Versuchskennung fehlt
