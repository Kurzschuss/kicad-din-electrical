# AP-0048 – Projektbezogene Handlungsvollmachten

## Ziel

Die in AP-0047 ermittelte handlungsberechtigte Projektperson wird mit projektbezogenen Vollmachten und dem bestehenden Authorization-Framework verbunden.

## Komponenten

- `SQLiteProjectAuthorityPolicyRepository`
- `ProjectActionAuthorizationService`
- `ProjectActionAuthorizationResult`

## Verbindliche Prüfreihenfolge

1. Handlungsberechtigte Projektperson ermitteln.
2. Prüfen, ob deren aktuelle Projektfunktion die angeforderte Berechtigung besitzt.
3. Benutzerkontext für das konkrete Projekt aufbauen.
4. Rollen, Blacklist, Whitelist und Ausnahmerechte über `AuthorizationService` prüfen.
5. Strukturiertes und nachvollziehbares Ergebnis zurückgeben.

Eine Handlung ist nur erlaubt, wenn sowohl die Projektfunktion als auch die Benutzerautorisierung zustimmen.

## Persistenz

Die Tabelle `projectos_project_authority_permissions` speichert die Berechtigungen je Projekt und Projektfunktion. `set_permissions()` ersetzt die vollständige Berechtigungsmenge deterministisch.

## Sicherheitsregeln

- Die Blacklist behält ihren Vorrang.
- Eine Projektfunktion allein umgeht keine Benutzersperre.
- Eine Benutzerrolle allein ersetzt keine projektbezogene Handlungsvollmacht.
- Die Vertrauensperson wird weiterhin nicht automatisch als handlungsberechtigt aufgelöst.
- Alle Prüfzeitpunkte werden nach UTC normalisiert.

## Tests

Die Tests decken Projektleiter, Stellvertretung, fehlende Projektvollmacht, Blacklist-Vorrang und ungültige Zeitangaben ab.

## Ergebnis

ProjectOS kann eine konkrete Projektberechtigung jetzt entlang von Verantwortung, Vertretung und allgemeiner Benutzerautorisierung vollständig prüfen.
