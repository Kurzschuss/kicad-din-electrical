# AP-0081 – Autorisierung und Auditierung der KiCad-Sicherheitsalarmbearbeitung

## Ziel

Die Bestätigung und der Abschluss persistierter KiCad-Sicherheitsalarme werden mit der vorhandenen projektbezogenen Vollmachts- und Rollenautorisierung verbunden. Jede erfolgreich autorisierte Statusänderung erhält zusätzlich einen unveränderlichen Bearbeitungs-Auditeintrag.

## Berechtigungen

- `PERM-KICAD-SECURITY-ALERT-ACKNOWLEDGE`: offenen Alarm bestätigen
- `PERM-KICAD-SECURITY-ALERT-RESOLVE`: bestätigten Alarm abschließen

Projektvollmacht und Benutzerautorisierung müssen beide wirksam sein. Die angegebene handelnde Rolle muss die jeweils geprüfte Berechtigung tatsächlich erteilen.

## Ablauf

1. Alarm und Projektbezug laden.
2. handlungsberechtigte Projektperson deterministisch ermitteln,
3. Projektvollmacht für die Aktion prüfen,
4. Benutzer- und Rollenberechtigung prüfen,
5. Alarmstatus ändern,
6. unveränderlichen Bearbeitungs-Auditeintrag speichern.

Abgelehnte Aktionen verändern weder den Alarmstatus noch das Bearbeitungsaudit.

## Projektlose Alarme

Ein Alarm ohne Projektkennung kann nicht über die projektbezogene Autorisierung bearbeitet werden. Dafür ist später ein ausdrücklich globaler Sicherheitsverantwortungs-Vertrag erforderlich; ProjectOS leitet keine globale Vollmacht aus einer Projektrolle ab.

## Bearbeitungsaudit

Die Tabelle `projectos_kicad_security_alert_action_audit` speichert:

- Aktionskennung,
- Alarm- und Projektkennung,
- Aktion `ACKNOWLEDGE` oder `RESOLVE`,
- Zeitpunkt,
- handelnde Person,
- tatsächlich verwendete Rolle,
- geprüfte Berechtigung,
- Begründung,
- Korrelationskennung.

Die Einträge sind nur anhängbar und chronologisch je Alarm abrufbar.

## Fehlerkennungen

- `ERR-KICAD-0110`: Auditzeitpunkt ohne Zeitzone
- `ERR-KICAD-0111`: Auditbegründung fehlt
- `ERR-KICAD-0112`: Alarmbearbeitungskennung bereits vorhanden
- `ERR-KICAD-0113`: Alarmbearbeitungs-Auditeintrag nicht gefunden
- `ERR-KICAD-0114`: projektloser Alarm kann nicht projektbezogen autorisiert werden
- `ERR-KICAD-0115`: Projektvollmacht oder Benutzerautorisierung lehnt ab
- `ERR-KICAD-0116`: handelnde Rolle erteilt die erforderliche Berechtigung nicht

## Grenzen

Die Bearbeitung sperrt keine Benutzer, entzieht keine Rollen und verändert keine KiCad-Freigabeentscheidung. Sie dokumentiert ausschließlich die autorisierte Behandlung eines beobachteten Sicherheitsalarms.
