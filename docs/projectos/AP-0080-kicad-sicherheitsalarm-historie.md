# AP-0080 – Persistente KiCad-Sicherheitsalarme

## Ziel

Alarmbewertungen aus AP-0079 werden als eigenständige, nachvollziehbare Sicherheitsereignisse gespeichert und dokumentiert bearbeitet.

## Lebenszyklus

```text
OPEN → ACKNOWLEDGED → RESOLVED
```

- `OPEN`: Alarm wurde erzeugt und noch nicht übernommen.
- `ACKNOWLEDGED`: Eine verantwortliche Person hat den Alarm geprüft und übernommen.
- `RESOLVED`: Die Bearbeitung wurde mit einer dokumentierten Maßnahme abgeschlossen.

Ein `CLEAR`-Ergebnis wird nicht gespeichert, weil kein Alarm vorliegt.

## Persistierte Daten

- Alarmkennung
- optionaler Projektbezug
- Alarmstufe `WARNING` oder `CRITICAL`
- Status
- Erzeugungszeitpunkt und ausgewertetes Zeitfenster
- Anzahl beobachteter Ablehnungen
- ausgelöste Meldungscodes
- Korrelationskennung
- bestätigende Person, Zeitpunkt und Begründung
- abschließende Person, Zeitpunkt und Begründung

## Regeln

- Alle Zeitpunkte benötigen einen Zeitzonenbezug.
- Nur offene Alarme können bestätigt werden.
- Nur bestätigte Alarme können abgeschlossen werden.
- Bestätigung und Abschluss dürfen nicht vor dem jeweils vorherigen Ereignis liegen.
- Jede Bearbeitung benötigt eine konkrete Begründung.
- Der Alarm-Lebenszyklus verändert keine Benutzer, Rollen, Projektvollmachten oder Freigaben.

## SQLite

Tabelle: `projectos_kicad_security_alerts`

## Fehlerkennungen

- `ERR-KICAD-0100`: CLEAR-Ergebnis darf nicht gespeichert werden
- `ERR-KICAD-0101`: Alarmzeitpunkte ohne Zeitzone
- `ERR-KICAD-0102`: Alarmkennung bereits vorhanden
- `ERR-KICAD-0103`: Alarm kann nicht bestätigt werden
- `ERR-KICAD-0104`: Bestätigung liegt vor Alarmerzeugung
- `ERR-KICAD-0105`: Alarm kann nicht abgeschlossen werden
- `ERR-KICAD-0106`: Abschluss liegt vor Bestätigung
- `ERR-KICAD-0107`: Alarm nicht gefunden
- `ERR-KICAD-0108`: Bearbeitungszeitpunkt ohne Zeitzone
- `ERR-KICAD-0109`: Bearbeitungsbegründung fehlt

## Abgrenzung

AP-0080 stellt ausschließlich Persistenz und dokumentierten Statuswechsel bereit. Autorisierung der Alarmbearbeitung und Benachrichtigungswege folgen in späteren Arbeitspaketen.
