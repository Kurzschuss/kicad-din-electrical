# AP-0078 – Suche und Sicherheitsdiagnose abgelehnter KiCad-Freigabeversuche

## Ziel

Abgelehnte KiCad-Freigabeversuche werden gezielt suchbar und statistisch auswertbar, ohne die fachliche Freigabehistorie zu vermischen.

## Komponenten

- `KiCadReleaseAttemptSearchFilter`
- `KiCadReleaseAttemptSearchPage`
- `KiCadReleaseAttemptSecurityDiagnostic`
- `KiCadReleaseAttemptSearchService`

## Filter

Kombinierbar sind Projekt, Benutzer, handelnde Rolle, Berechtigung, Ablehnungscode und Zeitraum. Zeitangaben benötigen einen Zeitzonenbezug.

## Pagination

- Seitennummer ab 1
- Seitengröße 1 bis 200
- Standardgröße 50
- neueste Versuche zuerst

## Sicherheitsdiagnose

Die Diagnose liefert Gesamtzahl, unterschiedliche Projekte, Benutzer und Rollen, die zehn häufigsten Ablehnungscodes, Benutzer und Rollen sowie ersten und letzten Versuchszeitpunkt.

Die Auswertung beschreibt beobachtete Sicherheitsereignisse. Sie bewertet weder Absicht noch Schuld und erzeugt keine fachliche Freigabeentscheidung.

## Fehlerkennungen

- `ERR-KICAD-0086`: Zeitfilter ohne Zeitzonenbezug
- `ERR-KICAD-0087`: Beginn nach Ende des Zeitraums
- `ERR-KICAD-0088`: ungültige Seitennummer
- `ERR-KICAD-0089`: ungültige Seitengröße

## Dateien

- `projectos/kicad_release_attempt_search.py`
- `tests/test_projectos_kicad_release_attempt_search.py`
