# AP-0026 – Repository-Framework

**Status:** Abgeschlossen  
**Version:** 1.0  
**Sprint:** 003 – Core Implementation  
**Paketversion:** 0.6.0

## Ziel

Dieses Arbeitspaket implementiert den technologieunabhängigen Repository-Vertrag und eine deterministische In-Memory-Referenzimplementierung für Tests und Simulationen.

## Implementierte Bausteine

- `RepositoryEntity`
- `RepositoryRecord[T]`
- `Repository[T]`
- `InMemoryRepository[T]`

## Repository-Operationen

- Laden über `ObjectId`
- Laden über `BusinessId`
- erstmaliges Hinzufügen
- Speichern mit erwarteter Revision
- Löschen mit erwarteter Revision
- deterministische Auflistung aller Einträge

## Revisionskontrolle

Neue Datensätze beginnen mit Revision 1. Jede erfolgreiche Speicherung erhöht die Revision um genau eins. Eine abweichende erwartete Revision führt zu `ERR-REP-0004` und verhindert das Überschreiben neuerer Änderungen.

## Eindeutigkeit

Der Speicher erzwingt Eindeutigkeit für:

- technische Objektkennungen,
- fachliche Kennungen.

Doppelte technische Kennungen erzeugen `ERR-REP-0001`, doppelte fachliche Kennungen `ERR-REP-0002`.

## Referenzimplementierung

`InMemoryRepository` ist für folgende Zwecke vorgesehen:

- Unit-Tests,
- Simulationen,
- frühe Anwendungsfall-Prototypen,
- Vertragstests späterer persistenter Adapter.

Es ersetzt keinen dauerhaften Offline-Datenspeicher.

## Tests

Die Tests prüfen:

- Hinzufügen und Laden über beide Kennungen,
- doppelte Kennungen,
- Revisionserhöhung,
- Revisionskonflikte,
- Löschen und Indexbereinigung,
- deterministische Einfügereihenfolge.

## Dateien

```text
projectos/repositories.py
tests/test_projectos_repositories.py
```

## Nächster Schritt

AP-0027 – Command- und Query-Framework.
