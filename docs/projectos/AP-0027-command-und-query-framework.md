# AP-0027 – Command- und Query-Framework

**Status:** Abgeschlossen  
**Version:** 1.0  
**Sprint:** 003 – Core Implementation

## Ziel

Dieses Arbeitspaket implementiert die erste ausführbare Grundlage der ProjectOS-Anwendungsschicht. Schreibende Befehle und lesende Abfragen werden klar getrennt, unveränderlich modelliert und über lokale Busse an genau einen registrierten Handler weitergeleitet.

## Implementierung

Neu eingeführt wurden:

- `Command`
- `Query`
- `CommandHandler`
- `QueryHandler`
- `LocalCommandBus`
- `LocalQueryBus`

## Regeln

- Befehle und Abfragen sind unveränderlich.
- Technische Typen folgen dem Schema `<domäne>.<objekt>.<aktion>`.
- Payloads und Parameter werden schreibgeschützt gespeichert.
- Zeitangaben benötigen einen Zeitzonenbezug und werden nach UTC normalisiert.
- Jeder Command- oder Query-Typ besitzt höchstens einen registrierten Handler.
- Fehlende Handler werden ausdrücklich gemeldet.
- Command Handler und Query Handler liefern strukturierte `Result`-Objekte.
- Abfragen und Befehle verwenden eine gemeinsame Korrelationskennung.
- Negative erwartete Revisionen sind unzulässig.

## Dateien

```text
projectos/application.py
tests/test_projectos_application.py
```

## Tests

Die Tests prüfen:

- Normalisierung technischer Typen,
- Unveränderlichkeit der Eingabedaten,
- Revisionsvalidierung,
- Handler-Registrierung,
- Schutz vor doppelten Handlern,
- Verhalten bei fehlenden Handlern,
- Weitergabe strukturierter Ergebnisse.

## Nicht Bestandteil

Noch nicht implementiert sind:

- Pipeline-Verhalten,
- Authentifizierung und Autorisierung,
- Transaktionssteuerung,
- Befehlsidempotenz,
- persistente Handler-Registries,
- Prozessmanager.

Diese Funktionen bauen in späteren Arbeitspaketen auf den jetzt festgelegten Verträgen auf.

## Ergebnis

AP-0027 ist abgeschlossen. ProjectOS besitzt damit eine minimale, typisierte und testbare Command-/Query-Infrastruktur.
