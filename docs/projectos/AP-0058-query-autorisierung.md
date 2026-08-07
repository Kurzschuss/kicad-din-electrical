# AP-0058 – Projektbezogene Leseberechtigungen und Query-Autorisierung

**Status:** Implementiert  
**Sprint:** SPRINT-004  
**Paketversion:** 0.36.0

## Ziel

Die standardisierte Query-Pipeline aus AP-0057 darf Command-Lebenszyklen, Suchergebnisse und Diagnosewerte nur nach einer nachvollziehbaren Berechtigungsprüfung ausgeben.

## Berechtigungen

| Query | Berechtigung |
|---|---|
| `project.command.lifecycle` | `PERM-PROJECT-COMMAND-LIFECYCLE-READ` |
| `project.command.search` | `PERM-PROJECT-COMMAND-SEARCH` |
| `project.command.diagnostic` | `PERM-PROJECT-COMMAND-DIAGNOSTIC-READ` |

## Ablauf

1. Query-Typ einer Berechtigung zuordnen.
2. Bei projektbezogenen Queries den Projektkontext prüfen.
3. Rollen, Blacklist, Whitelist und Ausnahmerechte über `AuthorizationService` auswerten.
4. Nur bei erfolgreicher Entscheidung die eigentliche `ProjectQueryPipeline` ausführen.
5. Autorisierungsentscheidung, verwendete Berechtigung und Query-Ergebnis gemeinsam zurückgeben.

## Projektabgrenzung

Lebenszyklus- und Suchabfragen benötigen:

- `AuthorizationContext.project_id`,
- den Query-Parameter `project_id`,
- Übereinstimmung beider Projektkennungen.

Damit kann ein berechtigter Benutzer nicht durch einen abweichenden Query-Parameter auf einen anderen Projektbereich wechseln.

Die globale Command-Diagnose benötigt keine Projektkennung, aber eine eigene Diagnoseberechtigung.

## Ergebnisvertrag

`AuthorizedProjectQueryResult` enthält:

- die vollständige `AuthorizationResult`,
- die verwendete Berechtigungskennung,
- das Ergebnis der standardisierten Query-Pipeline.

## Fehlerkennungen

| Kennung | Bedeutung |
|---|---|
| `ERR-PRJ-QRY-0003` | Für den Query-Typ ist keine Leseberechtigung konfiguriert. |
| `ERR-PRJ-QRY-0004` | Die Berechtigungsprüfung hat die Query abgelehnt. |
| `ERR-PRJ-QRY-0005` | Der notwendige Projektkontext fehlt. |
| `ERR-PRJ-QRY-0006` | Der Query-Parameter `project_id` fehlt oder ist ungültig. |
| `ERR-PRJ-QRY-0007` | Query-Projekt und Autorisierungskontext stimmen nicht überein. |

## Tests

Die Tests prüfen:

- autorisierte Lebenszyklusabfrage,
- autorisierte Suche,
- globale Diagnose ohne Projektkontext,
- Ablehnung ohne Leseberechtigung vor dem Handler-Aufruf,
- fehlenden Projektkontext,
- fehlenden Projektparameter,
- fremden Projektbereich,
- Query-Typ ohne konfigurierte Berechtigung.

## Grenzen

AP-0058 auditiert reine Lesezugriffe noch nicht persistent. Eine spätere Erweiterung kann sicherheitskritische oder besonders schützenswerte Abfragen in einen separaten Zugriffsnachweis aufnehmen.
