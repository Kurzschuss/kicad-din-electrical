# AP-0038 – SQLite-Persistenzadapter und transaktionale Unit of Work

**Status:** Abgeschlossen  
**Sprint:** 004 – Persistente Runtime und Projektintegration

## Ziel

ProjectOS erhält einen lokalen SQLite-Adapter, der den vorhandenen Repository-Vertrag ergänzt und vollständige Transaktionen ohne Netzwerkverbindung ermöglicht.

## Implementierung

- `SQLiteUnitOfWork` öffnet eine explizite Transaktion mit `BEGIN IMMEDIATE`.
- Erfolgreiche Kontextausführung führt zu `COMMIT`.
- Ausnahmen führen zu `ROLLBACK`.
- `SQLiteJsonRepository[T]` speichert typisierte Entitäten mit expliziten JSON-Codecs.
- Technische und fachliche Kennungen bleiben je Entitätstyp eindeutig.
- Revisionen beginnen bei 1 und werden optimistisch geprüft.
- Die In-Memory-Repositories bleiben für Tests und Simulationen erhalten.

## Sicherheitsentscheidung

Es wird kein `pickle` verwendet. Jede Domäne stellt explizite Encoder- und Decoder-Funktionen bereit. Dadurch werden gespeicherte Daten nachvollziehbar und es wird keine beliebige Codeausführung beim Laden ermöglicht.

## Tabelle

`projectos_entities` enthält:

- `entity_type`
- `object_id`
- `business_id`
- `revision`
- `payload`

## Fehlerverhalten

Die bestehenden Repository-Fehlerkennungen werden beibehalten:

- `ERR-REP-0001` – technische Kennung bereits vorhanden
- `ERR-REP-0002` – fachliche Kennung bereits vorhanden
- `ERR-REP-0003` – Objekt nicht gefunden
- `ERR-REP-0004` – Revisionskonflikt

## Tests

Die Tests prüfen Commit, Rollback, Laden nach erneutem Öffnen, Eindeutigkeit und optimistische Revisionskontrolle.

## Grenzen

Noch nicht enthalten sind domänenspezifische MCB-/RCCB-Codecs, Migrationstabellen, Outbox, Audit-Persistenz, Sicherung und Wiederherstellung. Diese folgen in weiteren Arbeitspaketen.

## Definition of Done

- SQLite-Unit-of-Work implementiert
- generischer JSON-Repository-Adapter implementiert
- Transaktions-Rollback getestet
- Revisionskonflikte getestet
- Dokumentation und öffentliche API aktualisiert
