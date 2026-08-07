# AP-0091 – Autorisierung globaler Sicherheitsbesetzungs-Freigabealarme

## Ziel

Bestätigung und Abschluss der in AP-0090 gespeicherten Alarme werden über die globale Sicherheitsverantwortung und getrennte Rollenberechtigungen autorisiert. Jede erfolgreiche Statusänderung wird zusätzlich in einem nur anhängbaren Bearbeitungsaudit gespeichert.

## Berechtigungen

- `PERM-KICAD-GLOBAL-SECURITY-STAFFING-RELEASE-ALERT-ACKNOWLEDGE`
- `PERM-KICAD-GLOBAL-SECURITY-STAFFING-RELEASE-ALERT-RESOLVE`

Die angegebene handelnde Rolle muss die jeweilige Berechtigung tatsächlich erteilen. Benutzerbezogene Ausnahmen oder andere Rollen reichen nicht aus.

## Verantwortungsauflösung

Die globale Hauptverantwortung wird zuerst verwendet. Ist sie ausdrücklich nicht verfügbar, übernimmt die aktive Stellvertretung. Projektrollen werden nicht herangezogen.

## Bearbeitungsaudit

Tabelle: `projectos_global_security_staffing_release_alert_action_audit`

Gespeichert werden Aktionskennung, Alarmkennung, Aktion, Zeitpunkt, Person, Rolle, Berechtigung, verwendete Verantwortung, Begründung und Korrelationskennung.

## Ablehnungen

Fehlende Berechtigung oder eine unpassende Rolle führen zu `PermissionError`. Alarmstatus und Bearbeitungsaudit bleiben unverändert.

## Fehlerkennungen

- `ERR-KICAD-0178` Auditzeitpunkt ohne Zeitzone
- `ERR-KICAD-0179` Auditbegründung fehlt
- `ERR-KICAD-0180` Aktionskennung bereits vorhanden
- `ERR-KICAD-0181` Benutzerautorisierung lehnt ab
- `ERR-KICAD-0182` Handelnde Rolle erteilt die Berechtigung nicht

Die Bearbeitung löst keine automatische Sperre, Rollenänderung oder Verantwortungsänderung aus.
