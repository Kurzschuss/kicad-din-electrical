# AP-0079 – Sicherheitsgrenzen und Alarmbewertung für KiCad-Freigabeversuche

## Ziel

Wiederholte abgelehnte KiCad-Freigabeversuche werden innerhalb eines konfigurierbaren Zeitfensters deterministisch bewertet. Die Bewertung ist ausschließlich beobachtend und erzeugt weder eine Sperre noch eine Freigabeentscheidung.

## Modell

- `KiCadReleaseAttemptAlertPolicy`
- `KiCadReleaseAttemptAlertService`
- `KiCadReleaseAttemptAlertResult`
- `KiCadSecurityAlertFinding`
- `KiCadSecurityAlertLevel`

Alarmstufen:

- `CLEAR`
- `WARNING`
- `CRITICAL`

## Konfigurierbare Grenzen

- Zeitfenster
- Warn- und kritische Gesamtzahl
- Warn- und kritische Anzahl je Benutzer
- Warn- und kritische Anzahl je Rolle
- ausdrücklich kritische Ablehnungscodes

Die Standardrichtlinie betrachtet 24 Stunden, warnt ab drei und bewertet ab fünf Versuchen als kritisch. Benutzerbezogene Grenzen verwenden dieselben Standardwerte; rollenbezogene Grenzen sind standardmäßig deaktiviert.

## Sicherheitsprinzip

Die Alarmbewertung:

- ändert keine Benutzerkonten,
- sperrt keine Rollen,
- verändert keine Projektvollmachten,
- erzeugt keine technische Freigabe,
- bewertet keine Absicht oder Schuld.

Sie liefert ausschließlich strukturierte Beobachtungen für nachgelagerte, autorisierte Prozesse.

## Meldungen

- `WARN-KICAD-0002`: Gesamtwarnschwelle erreicht
- `WARN-KICAD-0003`: Benutzerwarnschwelle erreicht
- `WARN-KICAD-0004`: Rollenwarnschwelle erreicht
- `ERR-KICAD-0090`: ungültiges Zeitfenster
- `ERR-KICAD-0091`: ungültige Gesamtschwelle
- `ERR-KICAD-0092`: kritische Gesamtschwelle unter Warnschwelle
- `ERR-KICAD-0093`: ungültige optionale Schwelle
- `ERR-KICAD-0094`: kritische optionale Schwelle unter Warnschwelle
- `ERR-KICAD-0095`: Bewertungszeitpunkt ohne Zeitzone
- `ERR-KICAD-0096`: kritische Gesamtzahl erreicht
- `ERR-KICAD-0097`: kritische Benutzerzahl erreicht
- `ERR-KICAD-0098`: kritische Rollenzahl erreicht
- `ERR-KICAD-0099`: kritischer Ablehnungscode beobachtet

## Tests

Die Tests prüfen leere Historien, Warn- und kritische Schwellen, kritische Einzelcodes, Zeitfenster sowie ungültige Richtlinien und Zeitpunkte.
