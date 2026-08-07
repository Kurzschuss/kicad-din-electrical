# AP-0040 – Persistenter Audit-Trail und atomare Speicherung

## Ziel

Geräteänderungen und zugehörige Audit-Einträge werden innerhalb derselben SQLite-Transaktion gespeichert. Ein Teilzustand darf nicht dauerhaft werden.

## Umsetzung

- `SQLiteAuditRepository` als append-only Audit-Speicher
- unveränderte Nutzung des bestehenden `AuditEntry`-Vertrags
- persistente Hash-Verkettung über `previous_hash` und `entry_hash`
- Lesen aller Einträge und Filtern nach Objektkennung
- vollständige Integritätsprüfung der gespeicherten Kette
- `add_with_audit()` für atomare Entitäts- und Audit-Speicherung

## Transaktionsverhalten

Die Funktion arbeitet innerhalb einer geöffneten `SQLiteUnitOfWork`. Schlägt die Audit-Erzeugung oder das Anhängen fehl, wird die gesamte Unit of Work zurückgerollt. Dadurch bleibt weder ein Gerät ohne Audit-Nachweis noch ein Audit-Eintrag ohne fachliche Änderung bestehen.

## Fehlerfälle

- doppelte Audit-Kennung oder Prüfsumme: `ERR-AUD-0001`
- inkonsistente Hash-Kette: `ERR-AUD-0002`
- Repository-Fehler werden unverändert als strukturierte Ergebnisse weitergegeben

## Tests

Die Tests prüfen:

- gemeinsame Persistenz von Gerät und Audit-Eintrag,
- vollständigen Rollback bei fehlerhafter Audit-Kette,
- Integrität mehrerer verketteter Einträge,
- Wiederherstellung nach erneutem Öffnen der Datenbank.

## Grenzen

AP-0040 enthält noch keine Outbox, keine Ereigniswiederholung und keine kryptografische Signatur mit externem Schlüssel. Diese Erweiterungen folgen in späteren Arbeitspaketen.
