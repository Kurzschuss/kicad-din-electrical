# AP-0024 – Validation-Framework

**Status:** Abgeschlossen  
**Version:** 1.0  
**Sprint:** 003 – Core Implementation  
**Paketversion:** 0.4.0

## Ziel

Dieses Arbeitspaket implementiert die allgemeine Validierungsbasis für ProjectOS. Fachliche Regeln werden als eigenständige, testbare Objekte ausgeführt und liefern ausschließlich strukturierte Meldungen.

## Implementierte Bausteine

- `ValidationRule[T]` als Regelvertrag
- `ValidationProfile[T]` als geordnete und unveränderliche Regelmenge
- `Validator[T]` als deterministische Ausführungskomponente
- `ValidationResult` als strukturiertes Ergebnis
- Übergabe einer `CorrelationId`
- Abbruch bei kritischen Meldungen als konfigurierbares Profilverhalten

## Verbindliche Regeln

- Jedes Profil besitzt eine fachliche Kennung.
- Ein Profil enthält mindestens eine Regel.
- Eine Regel darf innerhalb eines Profils nur einmal vorkommen.
- Regeln werden exakt in der definierten Reihenfolge ausgeführt.
- Regeln liefern ausschließlich `ResultMessage`-Objekte.
- Warnungen machen ein Ergebnis nicht ungültig.
- Fehler und kritische Meldungen machen ein Ergebnis ungültig.
- Bei `stop_on_critical=True` werden nach einer kritischen Meldung keine weiteren Regeln ausgeführt.
- Das Ergebnis dokumentiert alle tatsächlich ausgeführten Regelkennungen.

## Beispiel

```python
profile = ValidationProfile(
    BusinessId("VAL-PROFILE-0001"),
    (PositiveRule(), WarningRule()),
)

result = Validator[int]().validate(
    16,
    profile,
    correlation_id=CorrelationId(42),
)

if result.is_valid:
    print("Validierung erfolgreich")
```

## Tests

Die Tests prüfen:

- erfolgreiche Validierung ohne Meldungen,
- Fehlerbehandlung,
- Warnungen ohne Ungültigkeit,
- Abbruch bei kritischen Meldungen,
- Weiterlaufen bei deaktiviertem Abbruch,
- Übernahme der Korrelationskennung,
- Abweisung leerer Profile,
- Abweisung doppelter Regeln,
- Unveränderlichkeit des Ergebnisses.

## Repository-Dateien

```text
projectos/validation.py
tests/test_projectos_validation.py
projectos/__init__.py
```

## Definition of Done

- Validierungsverträge implementiert
- deterministische Regelausführung implementiert
- strukturierte Ergebnisse implementiert
- Unit-Tests ergänzt
- öffentliche Paket-API aktualisiert
- Dokumentation und Arbeitsstand aktualisiert

## Nächster Schritt

**AP-0025 – Event-Framework**
