# AP-0110 – Persistente Alarmereignisse

## Ziel

Die in AP-0109 ermittelten Warn- und Kritisch-Ergebnisse werden als eigenständige SQLite-Alarmereignisse gespeichert und kontrolliert bearbeitet.

## Lebenszyklus

`OPEN → ACKNOWLEDGED → RESOLVED`

Ein direkter Abschluss eines offenen Alarms ist nicht zulässig.

## Persistierte Daten

Gespeichert werden Alarmkennung, Alarmstufe, Status, Bewertungszeitraum, Gesamt- und Aktionszähler, Versuche ohne ermittelte Person, Finding-Codes, Korrelationskennung sowie dokumentierte Bestätigung und dokumentierter Abschluss.

## Regeln

- `CLEAR` wird nicht gespeichert.
- Alle Zeitpunkte benötigen einen Zeitzonenbezug.
- Bestätigung und Abschluss benötigen jeweils Person und Begründung.
- Die Zeitreihenfolge muss konsistent sein.
- Die Bearbeitung verändert keine Benutzer, Rollen, Verantwortungen, Freigaben oder zugrunde liegenden Auditereignisse.

## Fehlerkennungen

- `ERR-KICAD-0316` bis `ERR-KICAD-0325`

## Abgrenzung

Autorisierung und unveränderliches Bearbeitungsaudit folgen in AP-0111.
