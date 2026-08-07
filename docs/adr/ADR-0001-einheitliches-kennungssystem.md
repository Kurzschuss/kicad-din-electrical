# ADR-0001 – Einheitliches Kennungssystem

**Status:** Angenommen

## Kontext

ProjectOS benötigt stabile und maschinenlesbare Referenzen zwischen Anforderungen, Arbeitspaketen, Tests, Fehlern, Verbesserungen und Architekturentscheidungen.

## Entscheidung

Alle relevanten Artefakte erhalten eine eindeutige, unveränderliche Kennung. Kennungen werden niemals wiederverwendet.

## Kennungstypen

| Artefakt | Präfix | Beispiel |
|---|---|---|
| Arbeitspaket | AP | AP-0015 |
| ADR | ADR | ADR-0001 |
| Anforderung | REQ | REQ-MCB-0001 |
| Testfall | TEST | TEST-MCB-0001 |
| Fehler | ERR | ERR-VAL-0001 |
| Verbesserung | IMP | IMP-000001 |
| Änderungsantrag | CR | CR-0001 |
| Repository-Migration | RM | RM-0001 |
| Meilenstein | MS | MS-0001 |
| Audit-Eintrag | AUD | AUD-MCB-000001 |
| Befehl | CMD | CMD-00000421 |
| Abfrage | QRY | QRY-00001982 |

## Konsequenzen

- Referenzen erfolgen über Kennungen statt über Dateipfade.
- Umbenennungen ändern die Kennung nicht.
- Gelöschte Kennungen bleiben reserviert.
- Register und Validatoren können die Eindeutigkeit automatisiert prüfen.
