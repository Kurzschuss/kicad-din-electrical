# AP-0022 – Identifier-Framework

**Status:** Abgeschlossen  
**Version:** 1.0  
**Sprint:** 003 – Core Implementation  
**Abhängigkeiten:** ADR-0001, ADR-0008, AP-0013, AP-0021

## Ziel

AP-0022 implementiert die ersten produktiv nutzbaren Wertobjekte des ProjectOS-Kernmodells:

- `ObjectId`
- `BusinessId`
- `CorrelationId`

Alle drei Typen sind unveränderlich, validieren ihren Zustand bei der Erzeugung und besitzen eine stabile Textdarstellung.

## ObjectId

`ObjectId` ist die technische Identität einer Entität.

Eigenschaften:

- basiert auf `UUID`,
- wird über `ObjectId.new()` erzeugt,
- kann über `ObjectId.parse()` aus Text gelesen werden,
- weist leere Werte und die Null-UUID ab,
- ist unabhängig von fachlichen Daten.

## BusinessId

`BusinessId` ist die menschenlesbare fachliche Kennung gemäß ADR-0001.

Eigenschaften:

- normalisiert Eingaben auf Großbuchstaben,
- entfernt führende und nachfolgende Leerzeichen,
- erlaubt Großbuchstaben, Ziffern und Bindestriche,
- weist Leerzeichen, Unterstriche und unvollständige Segmente ab,
- ist unabhängig vom Dateinamen und Speicherort.

Beispiele:

```text
AP-0022
MCB-000123
REQ-MCB-0007
ERR-VAL-0012
```

## CorrelationId

`CorrelationId` verbindet zusammengehörige Befehle, Ereignisse, Audit- und Protokolleinträge.

Format:

```text
COR-00000045
```

Eigenschaften:

- deterministische Erzeugung aus einer positiven Sequenz,
- achtstellige Nummerndarstellung,
- Wertebereich 1 bis 99.999.999,
- Normalisierung auf Großbuchstaben,
- Sequenz 0 ist unzulässig.

## Fehlerverhalten

- Falsche Datentypen lösen `TypeError` aus.
- Fachlich ungültige Werte lösen `ValueError` aus.
- Es werden keine teilweise gültigen Kennungsobjekte erzeugt.

## Tests

Die Tests prüfen:

- UUID-Erzeugung und Eindeutigkeit,
- Abweisung der Null-UUID,
- Normalisierung fachlicher Kennungen,
- Abweisung ungültiger Zeichen und Formate,
- deterministische Korrelationskennungen,
- Grenzwerte der Sequenzen,
- Unveränderlichkeit aller Wertobjekte.

## Repository-Dateien

```text
projectos/identifiers.py
tests/test_projectos_identifiers.py
projectos/__init__.py
```

## Definition of Done

- [x] `ObjectId` implementiert
- [x] `BusinessId` implementiert
- [x] `CorrelationId` implementiert
- [x] öffentliche Paketexporte ergänzt
- [x] Unit-Tests ergänzt
- [x] Dokumentation erstellt

## Nächster Schritt

AP-0023 implementiert das Result-Framework mit strukturierten Erfolgs- und Fehlermeldungen.
