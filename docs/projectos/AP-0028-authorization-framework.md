# AP-0028 – Authorization-Framework

**Status:** Abgeschlossen  
**Version:** 1.0  
**Sprint:** 003 – Core Implementation

## Ziel

AP-0028 implementiert die erste ausführbare Berechtigungsprüfung für ProjectOS.

## Implementierte Bausteine

- `Role`
- `ExceptionRight`
- `AuthorizationContext`
- `AuthorizationResult`
- `AuthorizationService`

## Prüfreihenfolge

Die Implementierung verwendet folgende verbindliche Reihenfolge:

1. Blacklist
2. Rollenberechtigungen
3. Whitelist
4. aktive Ausnahmerechte
5. Ablehnung

Eine Blacklist-Sperre besitzt Vorrang vor allen normalen Freigaben.

## Rollen

Eine Rolle besitzt eine stabile fachliche Kennung und eine unveränderliche Menge von Berechtigungen.

## Whitelist und Blacklist

Whitelist und Blacklist werden benutzerbezogen ausgewertet. Die Blacklist ist eine ausdrückliche Sperre. Die Whitelist kann eine Berechtigung erteilen, wenn keine Sperre und keine passende Rollenberechtigung vorliegt.

## Ausnahmerechte

Ausnahmerechte sind:

- benutzerbezogen,
- berechtigungsbezogen,
- optional projektbezogen,
- zeitlich befristet,
- begründungspflichtig.

Zeitpunkte werden intern nach UTC normalisiert.

## Ergebnis

`AuthorizationResult` dokumentiert:

- Freigabe oder Ablehnung,
- Begründung,
- passende Rollen,
- verwendetes Ausnahmerecht,
- Whitelist-Treffer,
- Blacklist-Treffer.

Damit kann eine spätere Audit-Schicht die Entscheidung nachvollziehbar protokollieren.

## Tests

Die Tests prüfen:

- Rollenfreigaben,
- Vorrang der Blacklist,
- Whitelist-Freigaben,
- aktive projektbezogene Ausnahmerechte,
- abgelaufene Ausnahmerechte,
- ungültige Zeiträume,
- verpflichtende Zeitzonen.

## Nicht Bestandteil

Noch nicht implementiert sind:

- Benutzerkonten und Authentifizierung,
- Stellvertretungs- und Nachfolgerprozesse,
- persistente Rollenverwaltung,
- Audit-Persistenz,
- Wildcard- oder Ressourcenhierarchien.

## Repository-Dateien

```text
projectos/authorization.py
tests/test_projectos_authorization.py
docs/projectos/AP-0028-authorization-framework.md
```

## Nächster Schritt

AP-0029 – Audit-Framework.
