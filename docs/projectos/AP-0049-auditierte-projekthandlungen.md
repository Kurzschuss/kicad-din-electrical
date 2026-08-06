# AP-0049 – Auditierte projektbezogene Autorisierungsentscheidungen und Handlungsausführungen

## Ziel

Projektbezogene Handlungen müssen nicht nur autorisiert, sondern auch vollständig nachvollziehbar ausgeführt werden. AP-0049 verbindet deshalb die projektbezogene Autorisierung aus AP-0048 mit dem persistenten, verketteten Audit-Trail.

## Implementierte Komponenten

- `AuditedProjectActionResult[T]`
- `AuditedProjectActionService`

## Verbindlicher Ablauf

1. Projektbezogene Handlungsvollmacht und Benutzerautorisierung prüfen.
2. Die Entscheidung mit Projektfunktion, Benutzer, Berechtigung und Begründung in einen Audit-Eintrag überführen.
3. Den Audit-Eintrag an die bestehende SHA-256-Kette anhängen.
4. Nur bei erlaubter Entscheidung die fachliche Operation ausführen.
5. Audit und fachliche Nebenwirkung über dieselbe `SQLiteUnitOfWork` gemeinsam bestätigen oder zurückrollen.

## Audit-Inhalt

Jeder Eintrag enthält mindestens:

- Projektkennung und technisches Projektobjekt,
- ermittelte handlungsberechtigte Person,
- zugrunde liegende Projektfunktion,
- geprüfte Berechtigung,
- Autorisierungsentscheidung und Begründung,
- Treffer der projektbezogenen Handlungsvollmacht,
- Ausführungsstatus `EXECUTED` oder `DENIED`,
- Korrelationskennung,
- vorherigen Audit-Hash.

Auch abgelehnte Entscheidungen werden persistiert. Die fachliche Operation wird in diesem Fall nicht aufgerufen.

## Transaktionsverhalten

Der Dienst setzt eine umgebende `SQLiteUnitOfWork` voraus. Wirft die fachliche Operation eine Ausnahme, wird auch der zuvor geschriebene Audit-Eintrag zurückgerollt. Dadurch kann kein Audit-Eintrag eine erfolgreich ausgeführte Handlung behaupten, wenn die fachliche Änderung tatsächlich fehlgeschlagen ist.

## Grenzen

AP-0049 führt noch keine allgemeine Command-Pipeline für beliebige Projektaktionen ein. Die konkrete fachliche Operation wird als synchroner Callback übergeben. Eine standardisierte projektbezogene Command-Orchestrierung folgt in einem späteren Arbeitspaket.

## Tests

Die Tests decken ab:

- erlaubte Handlung mit persistentem Audit-Eintrag,
- abgelehnte Handlung ohne Aufruf der Operation,
- Auditierung einer Ablehnung,
- gemeinsamen Rollback bei fachlicher Ausnahme,
- Zeitzonenvalidierung.
