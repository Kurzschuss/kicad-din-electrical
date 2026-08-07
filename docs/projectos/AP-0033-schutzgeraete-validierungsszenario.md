# AP-0033 – Domänenübergreifendes Schutzgeräte-Validierungsszenario

**Status:** Abgeschlossen  
**Sprint:** 003 – Core Implementation  
**Paketversion:** 0.13.0

## Ziel

AP-0033 verbindet die ersten beiden fachlichen Domänen MCB und RCCB zu einem reproduzierbaren Schutzgeräte-Szenario. Beide Geräte werden zunächst in ihrer eigenen Domäne validiert. Anschließend werden ausschließlich domänenübergreifende Koordinationsbedingungen geprüft.

## Implementierte Objekte

- `ProtectionDevicePair`
- `ProtectionValidationResult`
- `validate_protection_pair()`

## Koordinationsregeln des Startprofils

| Kennung | Regel |
|---|---|
| `ERR-PROT-0001` | MCB und RCCB müssen dieselbe Bemessungsspannung besitzen. |
| `ERR-PROT-0002` | Der MCB-Nennstrom darf den RCCB-Bemessungsstrom nicht überschreiten. |
| `ERR-PROT-0003` | Die MCB-Polzahl darf die RCCB-Polzahl nicht überschreiten. |

Das Gesamtergebnis enthält zusätzlich sämtliche Meldungen der bestehenden MCB- und RCCB-Validierungsprofile.

## Architekturbezug

- Domain Ownership bleibt erhalten: MCB- und RCCB-Regeln werden nicht dupliziert.
- Die Koordination liegt in einem eigenen domänenübergreifenden Dienst.
- Das Ergebnis ist unveränderlich und maschinenlesbar.
- Korrelationskennungen können durchgängig weitergegeben werden.
- Das Szenario ist vollständig offline und deterministisch ausführbar.

## Grenzen

Das Startprofil bewertet keine Selektivität, Vorsicherung, Kurzschlussfestigkeit, Netzform, Leitungsauslegung, Herstellerkombination oder vollständige Normenkonformität. Diese Prüfungen benötigen eigene Anforderungen, Datenquellen und fachliche Freigaben.

## Tests

Die Tests prüfen:

- gültige Gerätekombination,
- Spannungsabweichung,
- Überschreitung des RCCB-Bemessungsstroms,
- unzureichende RCCB-Polzahl,
- Zusammenführung domänenspezifischer Fehler,
- Kennungsschema des Schutzgerätepaars,
- Weitergabe der Korrelationskennung.

## Repository-Dateien

```text
projectos/protection.py
tests/test_projectos_protection.py
docs/projectos/AP-0033-schutzgeraete-validierungsszenario.md
```

## Ergebnis

MCB und RCCB können nun als zusammengehöriges Schutzgeräte-Szenario geprüft werden, ohne die Zuständigkeiten ihrer jeweiligen Domänen aufzulösen.
