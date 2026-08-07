# AP-0047 – Vertretungs- und Nachfolgeregeln

## Ziel

ProjectOS ermittelt für einen Projektzeitpunkt automatisch und nachvollziehbar die handlungsberechtigte Person.

## Verbindliche Priorität

1. aktiver und verfügbarer Projektleiter,
2. aktive und verfügbare Stellvertretung,
3. aktiver und verfügbarer Nachfolger.

Die Vertrauensperson besitzt eine beratende Funktion und wird nicht automatisch handlungsberechtigt.

## Komponenten

- `ProjectAuthorityService`
- `ProjectAuthorityResolution`

## Eingaben

- Projektkennung,
- Prüfzeitpunkt mit Zeitzonenbezug,
- explizite Menge derzeit nicht verfügbarer Benutzerkennungen.

## Ergebnis

Die Auflösung enthält:

- ausgewählten Benutzer,
- zugrunde liegende Projektfunktion,
- UTC-Prüfzeitpunkt,
- berücksichtigte Abwesenheiten,
- fachliche Entscheidungsbegründung.

## Fehlerverhalten

`ERR-PRJ-0004` wird ausgelöst, wenn weder Projektleiter noch Stellvertretung noch Nachfolger aktiv und verfügbar sind.

## Grenzen

AP-0047 modelliert keine Kalenderabwesenheiten, Krankmeldungen oder automatische Eskalationsfristen. Die Nichtverfügbarkeit wird dem Dienst explizit und damit reproduzierbar übergeben.

## Tests

Die Tests decken Priorität, Vertretung, Nachfolge, Ausschluss der Vertrauensperson und Zeitzonenvalidierung ab.
