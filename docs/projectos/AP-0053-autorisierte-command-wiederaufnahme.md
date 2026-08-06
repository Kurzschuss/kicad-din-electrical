# AP-0053 – Autorisierung und Auditierung administrativer Command-Wiederaufnahmen

## Ziel

Administrative Wiederaufnahmen abgelehnter Commands dürfen nur mit expliziter Berechtigung, aktiver Rolle und dauerhaftem Audit-Nachweis erfolgen.

## Berechtigung

`PERM-PROJECT-COMMAND-RECOVER`

## Ablauf

1. Zeitpunkt und Autorisierungskontext prüfen.
2. Berechtigung über das bestehende Authorization-Framework auswerten.
3. Aktive handelnde Rolle prüfen.
4. abgelehnten Command laden.
5. Command über `CommandAdministrationService` wiederaufnehmen.
6. verketteten Audit-Eintrag erzeugen.
7. Wiederaufnahme und Audit durch die umgebende `SQLiteUnitOfWork` gemeinsam bestätigen.

## Audit-Inhalt

Der Audit-Eintrag enthält Benutzer, Rolle, Berechtigung, Projekt, Command-ID, Command-Typ, bisherigen Status, Payload-Fingerabdruck, Meldungscodes, Wiederaufnahme-ID und den Status `READY_FOR_RETRY`.

## Transaktionalität

Schlägt die Audit-Speicherung fehl, werden die Wiederaufnahme und die Änderung der Command-Historie zurückgerollt. Ohne Berechtigung wird weder die Historie verändert noch ein Audit-Eintrag geschrieben.

## Öffentliche Komponenten

- `PERM_PROJECT_COMMAND_RECOVER`
- `AuthorizedCommandRecovery`
- `AuthorizedCommandAdministrationService`

## Grenzen

AP-0053 startet den Command nicht automatisch erneut. Die erneute Verarbeitung erfolgt bewusst über die idempotente Command-Pipeline und verwendet dieselbe Command-ID.
