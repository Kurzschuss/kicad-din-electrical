# AP-0089 – Alarmbewertung globaler Besetzungsfreigabeversuche

## Ziel

Wiederholte abgelehnte Freigabeversuche werden innerhalb eines konfigurierbaren Zeitfensters rein beobachtend bewertet.

## Alarmstufen

- `CLEAR`
- `WARNING`
- `CRITICAL`

## Standardrichtlinie

- Zeitfenster: 24 Stunden
- Warnung ab 3 Versuchen
- kritisch ab 5 Versuchen
- Warnung je Benutzer ab 3, kritisch ab 5
- Warnung ohne ermittelte Person ab 1, kritisch ab 3
- Rollenschwellen standardmäßig deaktiviert

Zusätzlich können einzelne Ablehnungscodes unmittelbar als kritisch eingestuft werden.

## Grenzen

Die Bewertung sperrt keine Benutzer, verändert keine Rollen oder Verantwortungen und erzeugt keine Freigabeentscheidung.

## Meldungen

- `ERR-KICAD-0158` bis `ERR-KICAD-0167`
- `WARN-KICAD-0005` bis `WARN-KICAD-0008`
