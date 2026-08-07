# AP-0056 – Projektweite Command-Suche, Filterung und Pagination

## Ziel

ProjectOS stellt eine einheitliche Diagnoseansicht über aktuelle und archivierte Command-Ausführungen bereit. Die Ansicht verwendet den vollständigen Lebenszyklus aus AP-0055 und bleibt vollständig offlinefähig.

## Implementierung

Neue Komponenten:

- `CommandSearchFilter`
- `CommandSearchItem`
- `CommandSearchPage`
- `CommandSearchService`

## Durchsuchte Daten

Die Suche berücksichtigt Command-IDs aus:

- `projectos_command_executions`
- `projectos_command_execution_archive`

Für jeden Treffer wird die vollständige Lebenszyklusansicht geladen. Dadurch bleiben auch administrativ wiederaufgenommene Commands auffindbar, deren ursprünglicher Historieneintrag bereits archiviert wurde.

## Filter

Filter sind frei kombinierbar:

- Projektkennung
- exakter Command-Typ
- Lebenszyklusstatus
- frühester Verarbeitungszeitpunkt
- spätester Verarbeitungszeitpunkt
- Freitext über Command-ID, Command-Typ, Projektkennung und Korrelationskennung

Zeitfilter sind einschließlich ihrer Grenzwerte. Alle Zeitangaben werden nach UTC normalisiert.

## Pagination

- Seitennummer beginnt bei 1.
- Seitengröße liegt zwischen 1 und 200.
- Standards seitengröße: 50.
- Sortierung: neuester Verarbeitungszeitpunkt zuerst, danach Command-ID.
- Das Ergebnis enthält Gesamtzahl, Seitenzahl sowie `has_previous` und `has_next`.

## Verträge

- Die Suche verändert keine produktiven Tabellen.
- Die Ausgabe ist für denselben Datenstand deterministisch.
- Leere Ergebnismengen besitzen `total_pages = 0`.
- Eine Seite außerhalb der vorhandenen Daten liefert eine leere Elementmenge, behält aber die angeforderte Seitennummer.
- Ungültige Zeiträume und Paginationwerte werden früh abgelehnt.

## Tests

Die Tests prüfen:

- stabile Sortierung und Seitengrenzen,
- kombinierte Filter,
- einschließlich wirkende Zeitgrenzen,
- Validierung von Seitennummer, Seitengröße und Zeitzonenbezug.

## Ergebnis

AP-0056 schafft das projektweite Lesemodell für administrative Diagnoseoberflächen und spätere Query-Handler.

## Nächster Schritt

AP-0057 – standardisierte Query-Pipeline für Command-Lebenszyklus, Suche und Diagnose.
