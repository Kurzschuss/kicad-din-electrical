# AP-0060 – Query-Zugriffsdiagnose und Audit-Auswertung

**Status:** Implementiert  
**Sprint:** SPRINT-004  
**Datum:** 2026-08-06

## Ziel

Sicherheitsrelevante Query-Zugriffe müssen projektbezogen, filterbar, paginiert und statistisch auswertbar sein. Grundlage bleibt der unveränderliche, verkettete SQLite-Audit-Trail aus AP-0059.

## Umsetzung

`QueryAuditSearchService` liest ausschließlich Audit-Aktionen `project_query_accessed` und `project_query_denied`. Andere fachliche Audit-Einträge werden nicht in die Query-Diagnose aufgenommen.

### Modelle

- `QueryAuditFilter`
- `QueryAuditItem`
- `QueryAuditPage`
- `QueryAuditStatistics`
- `QueryAuditSearchService`

### Filter

- Projektkennung
- Benutzerkennung
- handelnde Rolle
- Berechtigung
- Query-Typ
- erlaubt oder abgelehnt
- einschließlich wirkender UTC-Zeitraum

Alle Filter sind kombinierbar.

### Pagination

- Seitennummer ab 1
- Seitengröße 1 bis 200
- Standardgröße 50
- stabile Sortierung: neuester Audit-Eintrag zuerst

### Statistik

Die Statistik enthält Gesamtzahl, erfolgreiche und abgelehnte Zugriffe, Ablehnungsquote sowie jeweils die zehn häufigsten Query-Typen, Benutzer, Rollen und Berechtigungen.

## Fehlerverträge

- `ERR-PRJ-QRY-0008`: ungültiger Zeitraum oder fehlender Zeitzonenbezug
- `ERR-PRJ-QRY-0009`: ungültige Seitengröße
- `ERR-PRJ-QRY-0010`: ungültige Seitennummer

## Datenschutz und Integrität

Die Auswertung liest nur die bereits in AP-0059 bewusst reduzierte Audit-Sicht. Vollständige Query-Parameter werden nicht nachträglich rekonstruiert oder dupliziert. Der zugrunde liegende Audit-Trail bleibt append-only und hashverkettet.

## Tests

Geprüft werden kombinierte Filter, stabile Sortierung, Pagination, Statistik, einschließlich wirkende Zeitgrenzen, ungültige Parameter und das Ignorieren fremder Audit-Aktionen.

## Ergebnis

Mit AP-0060 sind Ausführung, Autorisierung, Auditierung und Diagnose der ProjectOS-Query-Infrastruktur vollständig miteinander verbunden. AP-0060 bildet den fachlichen Abschluss von Sprint 004; die CI-Bestätigung erfolgt durch den nach den Änderungen ausgelösten vollständigen Testlauf.
