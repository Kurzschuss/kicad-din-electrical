# AP-0039 – MCB- und RCCB-Codecs sowie persistente Repositories

**Status:** Abgeschlossen  
**Sprint:** 004 – Persistente Runtime und Projektintegration  
**Abhängigkeit:** AP-0038

## Ziel

MCB- und RCCB-Aggregate werden über explizite, nachvollziehbare JSON-Codecs in den SQLite-Adapter überführt. Die Domänenobjekte bleiben unabhängig von SQLite und JSON.

## Implementierung

Neu bereitgestellt werden:

- `encode_mcb()` und `decode_mcb()`
- `encode_rccb()` und `decode_rccb()`
- `create_mcb_sqlite_repository()`
- `create_rccb_sqlite_repository()`

Die beiden Repository-Fabriken verwenden dieselbe Tabelle, aber getrennte `entity_type`-Werte:

- `mcb`
- `rccb`

Dadurch können technische oder fachliche Kennungen in unterschiedlichen Domänen unabhängig vorkommen, während sie innerhalb einer Domäne eindeutig bleiben.

## Persistierte MCB-Daten

- technische und fachliche Kennung
- Hersteller und Produktbezeichnung
- Nennstrom
- Bemessungsspannung
- Schaltvermögen
- Polzahl
- Auslösecharakteristik

## Persistierte RCCB-Daten

- technische und fachliche Kennung
- Hersteller und Produktbezeichnung
- Bemessungsstrom
- Bemessungsdifferenzstrom
- Bemessungsspannung
- Polzahl
- RCCB-Typ

## Sicherheits- und Architekturregeln

- Kein `pickle` und keine dynamische Klassenerzeugung.
- Decoder erzeugen ausschließlich bekannte Domänenobjekte.
- Alle Wertobjekt-Invarianten werden beim Laden erneut ausgeführt.
- Ungültige oder manipulierte Daten werden nicht stillschweigend übernommen.
- Schemaänderungen an Nutzdaten benötigen künftig versionierte Migrationen.

## Tests

Die Tests prüfen:

- verlustfreie MCB-Roundtrips,
- verlustfreie RCCB-Roundtrips,
- getrennte Speicherung beider Domänen,
- erneutes Laden nach Schließen der Verbindung,
- Revisionserhöhung bei Änderungen.

## Definition of Done

- [x] MCB-Codec implementiert
- [x] RCCB-Codec implementiert
- [x] typisierte Repository-Fabriken implementiert
- [x] persistente Roundtrip-Tests ergänzt
- [x] Dokumentation aktualisiert
- [x] Arbeitsstand aktualisiert

## Nächster Schritt

AP-0040 – Persistenter Audit-Trail und atomare Speicherung von Geräten und Audit-Einträgen.
