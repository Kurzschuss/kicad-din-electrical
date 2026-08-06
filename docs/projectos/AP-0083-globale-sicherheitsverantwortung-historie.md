# AP-0083 – Historie und Diagnose globaler Sicherheitsverantwortungen

## Ziel

Globale Sicherheitsverantwortungen werden zusätzlich zur operativen Zuordnung als unveränderliche Wechselhistorie gespeichert, durchsucht und diagnostiziert.

## Modell

`SQLiteTrackedGlobalSecurityResponsibilityRepository` erweitert die operative Zuordnung um `assign_tracked()`. Jeder Wechsel besitzt eine eindeutige Wechselkennung und speichert die vorherige Person.

Die Historientabelle lautet:

```text
projectos_global_security_responsibility_history
```

## Suche

Filterbar sind:

- Verantwortung `PRIMARY` oder `DEPUTY`,
- Benutzerkennung,
- einschließlich wirkender Zeitraum.

Die Ergebnisse sind stabil nach Zuweisungszeitpunkt und Wechselkennung sortiert und paginiert.

## Zustandsdiagnose

Die Diagnose zeigt:

- aktuelle Hauptverantwortung,
- aktuelle Stellvertretung,
- Aktivstatus beider Benutzer,
- vollständige und getrennte Besetzung,
- unzulängliche Doppelbesetzung durch dieselbe Person,
- Anzahl und letzten Zeitpunkt historisierter Änderungen.

Die Diagnose verändert keine Verantwortung und trifft keine automatische Personalentscheidung.

## Fehlerkennungen

```text
ERR-KICAD-0129  Zeitfilter ohne Zeitzone
ERR-KICAD-0130  Beginn nach Ende des Zeitraums
ERR-KICAD-0131  Wechselkennung bereits vorhanden
ERR-KICAD-0132  Verantwortungswechsel nicht gefunden
ERR-KICAD-0133  Ungültige Seitennummer
ERR-KICAD-0134  Ungültige Seitengröße
```

## Tests

Die Tests prüfen Wechsel mit Vorgängerbezug, kombinierte Filter, Pagination, vollständige getrennte Besetzung, Doppelbesetzung sowie ungültige Parameter.
