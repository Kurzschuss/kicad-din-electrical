# AP-0077 – Auditierung abgelehnter KiCad-Freigabeversuche

## Ziel

Abgelehnte Versuche, eine technische KiCad-Freigabeentscheidung zu erzeugen, werden unveränderlich und projektbezogen protokolliert. Dabei entsteht ausdrücklich keine fachliche Freigabeentscheidung.

## Trennung der Historien

- `projectos_kicad_release_audit`: tatsächlich autorisierte technische Freigabeentscheidungen
- `projectos_kicad_release_attempt_audit`: ausschließlich abgelehnte Autorisierungsversuche

Damit kann ein abgelehnter Zugriff niemals als Freigabe missverstanden werden.

## Gespeicherte Daten

Jeder abgelehnte Versuch enthält:

- Versuchskennung
- Projektkennung
- Zeitpunkt mit Zeitzone
- ermittelte handelnde Person
- angegebene handelnde Rolle
- geprüfte Berechtigung
- Ablehnungscode
- Ablehnungsbegründung
- Korrelationskennung

## Autorisierungsablauf

`AuthorizedKiCadReleaseService` kann mit einem `SQLiteKiCadReleaseAttemptAuditRepository` konfiguriert werden. Bei `ERR-KICAD-0078` oder `ERR-KICAD-0079` wird der Versuch vor dem Auslösen des `PermissionError` gespeichert. Die fachliche Freigabehistorie bleibt unverändert.

Ist das Versuchsaudit aktiviert, benötigt jeder abgelehnte Aufruf eine eindeutige `attempt_id`.

## Fehlerkennungen

- `ERR-KICAD-0080`: Versuchszeitpunkt besitzt keine Zeitzone
- `ERR-KICAD-0081`: Ablehnungscode fehlt
- `ERR-KICAD-0082`: Ablehnungsbegründung fehlt
- `ERR-KICAD-0083`: Freigabeversuchskennung ist bereits vorhanden
- `ERR-KICAD-0084`: Freigabeversuch wurde nicht gefunden
- `ERR-KICAD-0085`: Versuchsaudit ist aktiviert, aber die Versuchskennung fehlt

## Grenzen

Das Versuchsaudit dokumentiert Autorisierungsablehnungen. Es ersetzt weder eine allgemeine Angriffserkennung noch eine zentrale SIEM- oder Alarmierungsplattform.
