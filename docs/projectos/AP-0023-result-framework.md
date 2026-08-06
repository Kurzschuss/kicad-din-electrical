# AP-0023 – Result-Framework

**Status:** Abgeschlossen  
**Version:** 1.0  
**Sprint:** 003 – Core Implementation  
**Abhängigkeiten:** AP-0007, AP-0013, AP-0021, AP-0022

## Ziel

Dieses Arbeitspaket implementiert strukturierte Ergebnisobjekte für erwartbare fachliche Abläufe.

Fachliche Ablehnungen werden nicht als Exceptions behandelt, sondern als unveränderliche `Result`-Objekte mit stabilen Meldungskennungen, Schweregraden und optionaler Korrelationskennung zurückgegeben.

## Implementierte Bausteine

- `MessageSeverity`
- `ResultMessage`
- `Result[T]`
- `Result.success(...)`
- `Result.failure(...)`
- gefilterte Zugriffe über `errors` und `warnings`

## Invarianten

- Ein erfolgreiches Ergebnis darf keine Meldung mit `ERROR` oder `CRITICAL` enthalten.
- Ein fehlgeschlagenes Ergebnis benötigt mindestens eine Fehlermeldung.
- Ein fehlgeschlagenes Ergebnis darf keinen fachlich gültigen Wert enthalten.
- Meldungstexte dürfen nicht leer sein.
- Ergebnisobjekte und Meldungen sind unveränderlich.
- Meldungsparameter werden schreibgeschützt bereitgestellt.

## Verwendung

```python
from projectos import BusinessId, MessageSeverity, Result, ResultMessage

meldung = ResultMessage(
    code=BusinessId("ERR-MCB-0001"),
    severity=MessageSeverity.ERROR,
    text="Der Nennstrom ist nicht zulässig.",
)

ergebnis = Result.failure(meldung)
```

## Abgrenzung

Das Result-Framework behandelt erwartbare fachliche Ergebnisse. Unerwartete technische Fehler dürfen weiterhin Exceptions auslösen und werden an den definierten Schichtgrenzen übersetzt.

## Tests

Die Tests prüfen:

- erfolgreiche Ergebnisse mit Wert,
- fehlgeschlagene Ergebnisse mit Fehlern,
- Abweisung widersprüchlicher Zustände,
- Korrelationskennungen,
- Unveränderlichkeit,
- schreibgeschützte Parameter,
- Normalisierung von Meldungstexten.

## Repository-Dateien

```text
projectos/results.py
tests/test_projectos_results.py
docs/projectos/AP-0023-result-framework.md
```

## Status

**AP-0023 abgeschlossen**

Nächster Schritt: **AP-0024 – Validation-Framework**.
