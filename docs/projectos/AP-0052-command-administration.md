# AP-0052 – Command-Statusabfragen, Diagnose und Wiederaufnahme

## Ziel

ProjectOS stellt administrative Statusabfragen für die persistente Command-Historie bereit und erlaubt eine kontrollierte Wiederaufnahme ausschließlich abgelehnter Commands.

## Komponenten

- `CommandExecutionDiagnostic`
- `CommandRecoveryRecord`
- `CommandAdministrationService`

## Diagnose

Die Diagnose liefert Gesamtzahl sowie Anzahl erfolgreicher und abgelehnter Commands. Zusätzlich können Einträge nach `SUCCEEDED` oder `REJECTED` gefiltert werden.

## Wiederaufnahme

Eine Wiederaufnahme ist nur für einen vorhandenen Eintrag mit Status `REJECTED` zulässig. Sie erfordert eine eindeutige Wiederaufnahme-ID, einen handelnden Benutzer, eine Begründung und einen UTC-fähigen Zeitpunkt.

Der abgelehnte Historieneintrag wird entfernt, damit dieselbe Command-ID erneut über die idempotente Pipeline verarbeitet werden kann. Der administrative Vorgang bleibt dauerhaft in `projectos_command_recoveries` dokumentiert.

Erfolgreiche Commands bleiben unveränderlich und können nicht erneut freigegeben werden.

## Fehlerkennungen

- `ERR-PRJ-CMD-0006`: Command nicht gefunden
- `ERR-PRJ-CMD-0007`: Command ist nicht abgelehnt
- `ERR-PRJ-CMD-0008`: Wiederaufnahme-ID bereits verwendet

## Tests

Die Tests prüfen Diagnose, Statusfilter, persistente Wiederaufnahme sowie den Schutz erfolgreicher Commands.
