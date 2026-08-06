# AP-0059 – Persistente Auditierung sicherheitsrelevanter Query-Zugriffe

**Status:** Implementiert  
**Sprint:** SPRINT-004  
**Paketversion:** 0.37.0

## Ziel

Sicherheitsrelevante Lesezugriffe müssen ebenso nachvollziehbar sein wie schreibende Aktionen. Erfolgreiche und abgelehnte ProjectOS-Queries werden deshalb dauerhaft und manipulationsgeschützt im bestehenden SQLite-Audit-Trail dokumentiert.

## Umsetzung

Neu eingeführt wurden:

- `AuditedProjectQueryPipeline`
- `AuditedProjectQueryResult`
- `PERM_PROJECT_QUERY_UNMAPPED`
- stabile technische Query-Objektkennungen auf Basis von UUIDv5

Die Pipeline umschließt die autorisierte Query-Pipeline aus AP-0058. Dadurch bleibt die Reihenfolge verbindlich:

1. handelnde Rolle prüfen,
2. Projektbereich und Leseberechtigung prüfen,
3. Query ausführen oder ablehnen,
4. Ergebnis als verketteten Audit-Eintrag speichern,
5. strukturiertes Result zurückgeben.

## Audit-Inhalt

Jeder Eintrag enthält mindestens:

- Benutzerkennung,
- aktive handelnde Rolle,
- geprüfte Berechtigung,
- Query-ID und Query-Typ,
- Projektkennung, soweit vorhanden,
- Ergebnis `allowed=true|false`,
- Meldungscodes einer Ablehnung,
- Korrelationskennung,
- fachliche Begründung,
- vorherigen Audit-Hash.

Erfolgreiche Zugriffe verwenden die Aktion `project_query_accessed`. Abgelehnte Zugriffe verwenden `project_query_denied`.

## Sicherheitsregeln

- Eine nicht aktive handelnde Rolle verhindert Query-Ausführung und Audit-Erzeugung.
- Eine leere Begründung ist nicht zulässig.
- Auch fehlende Berechtigungen und Projektbereichsverletzungen werden auditiert.
- Query-Parameter werden nicht vollständig in den Audit-Trail kopiert, um unnötige oder vertrauliche Nutzdaten zu vermeiden.
- Nicht zugeordnete Query-Typen erhalten die technische Berechtigung `PERM-PROJECT-QUERY-UNMAPPED`.
- Die bestehende SHA-256-Hashkette des Audit-Trails bleibt verbindlich.

## Tests

Die Tests decken ab:

- erfolgreichen auditierten Lesezugriff,
- auditierten abgelehnten Zugriff,
- persistente Audit-Integrität,
- Hash-Verkettung mehrerer Zugriffe,
- Ablehnung einer inaktiven handelnden Rolle,
- Ablehnung einer leeren Begründung.

## Ergebnis

ProjectOS besitzt damit einen durchgängigen Sicherheitsnachweis für schreibende und lesende Vorgänge. Abgelehnte Leseversuche gehen nicht mehr verloren und können später projekt-, benutzer- und korrelationsbezogen untersucht werden.
