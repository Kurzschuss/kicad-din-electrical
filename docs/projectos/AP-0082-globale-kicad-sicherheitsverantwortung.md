# AP-0082 – Globale KiCad-Sicherheitsverantwortung

## Ziel

Projektlose KiCad-Sicherheitsalarme erhalten eine eigenständige globale Verantwortungs- und Autorisierungskette. Projektrollen und künstliche Projektkennungen werden dafür nicht verwendet.

## Verantwortungen

- `PRIMARY`: globale Sicherheitsverantwortung
- `DEPUTY`: globale Sicherheitsstellvertretung

Die Hauptverantwortung wird zuerst geprüft. Ist sie ausdrücklich nicht verfügbar, übernimmt die Stellvertretung. Beide Benutzer müssen aktiv sein.

## Autorisierung

Für die Bearbeitung gelten weiterhin die getrennten Berechtigungen:

- `PERM-KICAD-SECURITY-ALERT-ACKNOWLEDGE`
- `PERM-KICAD-SECURITY-ALERT-RESOLVE`

Die ermittelte Person muss die Berechtigung über die angegebene aktive Rolle erhalten. Whitelist oder Ausnahmerecht allein legitimieren keine protokollierte handelnde Rolle.

## Strikte Trennung

- Projektloser Alarm: ausschließlich globale Sicherheitsverantwortung.
- Projektbezogener Alarm: ausschließlich projektbezogene Autorisierung aus AP-0081.
- Globale Vollmacht ist keine Projektvollmacht.
- Projektvollmacht ist keine globale Sicherheitsvollmacht.

## Persistenz

Globale Verantwortungen werden in `projectos_global_security_responsibilities` gespeichert.

Autorisierte Bearbeitungsschritte projektloser Alarme werden unveränderlich in `projectos_kicad_global_security_alert_action_audit` protokolliert.

## Fehlerkennungen

- `ERR-KICAD-0117`: Zuweisungszeitpunkt ohne Zeitzone
- `ERR-KICAD-0118`: Begründung der Verantwortung fehlt
- `ERR-KICAD-0119`: unbekannter Benutzer
- `ERR-KICAD-0120`: inaktiver Benutzer
- `ERR-KICAD-0121`: Auflösungszeitpunkt ohne Zeitzone
- `ERR-KICAD-0122`: keine verfügbare globale Verantwortung
- `ERR-KICAD-0123`: globaler Auditzeitpunkt ohne Zeitzone
- `ERR-KICAD-0124`: globale Auditbegründung fehlt
- `ERR-KICAD-0125`: globale Aktionskennung doppelt
- `ERR-KICAD-0126`: projektbezogener Alarm darf nicht global autorisiert werden
- `ERR-KICAD-0127`: Benutzerautorisierung lehnt ab
- `ERR-KICAD-0128`: handelnde Rolle erteilt die Berechtigung nicht

## Grenzen

Die globale Alarmbearbeitung sperrt keine Benutzer, entzieht keine Rollen und verändert keine Freigabeentscheidung. Sie dokumentiert ausschließlich verantwortete Alarmstatusänderungen.
