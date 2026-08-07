# AP-0086 – Autorisierung globaler Sicherheitsbesetzungs-Freigaben

## Ziel

Freigabeentscheidungen zur globalen Sicherheitsbesetzung dürfen nur durch die aktuell ermittelte globale Sicherheitsverantwortung oder deren Stellvertretung und nur mit einer tatsächlich berechtigenden Rolle gespeichert werden.

## Berechtigung

`PERM-KICAD-GLOBAL-SECURITY-STAFFING-RELEASE-DECIDE`

## Ablauf

1. Hauptverantwortung oder Stellvertretung zum Entscheidungszeitpunkt ermitteln.
2. Benutzerkontext ohne künstlichen Projektbezug laden.
3. Benutzerautorisierung für die Freigabeberechtigung prüfen.
4. Sicherstellen, dass die angegebene handelnde Rolle zu den tatsächlich berechtigenden Rollen gehört.
5. Erst danach die unveränderliche Freigabeentscheidung aus AP-0085 speichern.

## Stellvertretung

Ist die Hauptverantwortung ausdrücklich nicht verfügbar, wird die globale Stellvertretung deterministisch verwendet. Sind beide nicht verfügbar, wird keine Entscheidung gespeichert.

## Ablehnungsverhalten

Bei fehlender Benutzerberechtigung, unpassender handelnder Rolle oder fehlender verfügbarer Verantwortung wird keine Freigabeentscheidung erzeugt. Die bestehende Freigabehistorie bleibt unverändert.

## Fehlerkennungen

- `ERR-KICAD-0146`: Benutzerautorisierung lehnt die Besetzungsfreigabe ab.
- `ERR-KICAD-0147`: Die handelnde Rolle erteilt die Besetzungsfreigabe nicht.

## Grenzen

Die technische Freigabe ersetzt keine organisatorische, arbeitsrechtliche oder gesetzliche Verantwortungsübertragung. Der Dienst verändert weder Benutzer noch Rollen oder Verantwortungszuordnungen.
