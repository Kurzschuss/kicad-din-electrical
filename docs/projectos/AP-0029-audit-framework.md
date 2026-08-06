# AP-0029 – Audit-Framework

**Status:** Abgeschlossen  
**Sprint:** 003 – Core Implementation  
**Paketversion:** 0.9.0

## Ziel

AP-0029 implementiert einen unveränderlichen, ausschließlich ergänzbaren Audit-Trail für fachlich und sicherheitsrelevante Änderungen.

## Implementierte Bausteine

- `AuditEntry`
- `InMemoryAuditRepository`
- Vorher- und Nachher-Werte
- Benutzer-, Rollen- und Berechtigungsbezug
- UTC-Zeitstempel
- Korrelationskennung
- SHA-256-Prüfsummen
- Verkettung über `previous_hash`
- Filterung nach betroffenem Objekt
- vollständige Integritätsprüfung

## Verbindliche Regeln

1. Audit-Einträge sind nach ihrer Erzeugung unveränderlich.
2. Ein Eintrag benötigt eine Aktion und einen Änderungsgrund.
3. Zeitstempel müssen einen Zeitzonenbezug besitzen und werden in UTC geführt.
4. Der Speicher ist ausschließlich ergänzend; reguläre Änderungen und Löschungen existieren nicht.
5. Jeder neue Eintrag verweist auf die Prüfsumme seines Vorgängers.
6. Doppelte Audit-Kennungen werden abgewiesen.
7. Eine inkonsistente Prüfsummenkette wird abgewiesen oder bei der Prüfung erkannt.
8. Vorher- und Nachher-Werte werden schreibgeschützt bereitgestellt.

## Fehlerkennungen

- `ERR-AUD-0001` – Audit-Kennung bereits vorhanden
- `ERR-AUD-0002` – Audit-Kette nicht konsistent

## Dateien

```text
projectos/audit.py
tests/test_projectos_audit.py
docs/projectos/AP-0029-audit-framework.md
```

## Noch nicht enthalten

- dauerhafter Audit-Speicher,
- Signatur- und Schlüsselverwaltung,
- Aufbewahrungs- und Anonymisierungsregeln,
- rollenbasierter Audit-Export.

Diese Funktionen bauen auf dem nun stabilen Audit-Vertrag auf.
