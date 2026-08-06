# AP-0050 – Standardisierte projektbezogene Command-Pipeline

## Status

Implementiert.

## Ziel

Projektbezogene Commands werden über einen einheitlichen Ablauf registriert, autorisiert, auditiert und ausgeführt. Fachliche Handler müssen die Sicherheits- und Nachweislogik nicht erneut implementieren.

## Komponenten

- `ProjectCommandDefinition`
- `ProjectCommandExecutionResult[T]`
- `ProjectCommandPipeline`

## Verbindlicher Ablauf

1. Command-Definition und Handler ermitteln.
2. Begründung prüfen.
3. handlungsberechtigte Projektperson ermitteln.
4. projektbezogene Handlungsvollmacht prüfen.
5. allgemeine Benutzerautorisierung prüfen.
6. Entscheidung persistent auditieren.
7. erlaubten Handler ausführen.
8. strukturiertes `Result` mit derselben Korrelationskennung liefern.

## Registrierung

Jeder Command-Typ besitzt höchstens eine Definition und einen Handler. Eine Definition bindet den Command-Typ an eine Berechtigung und eine Audit-Aktion.

```python
pipeline.register(
    ProjectCommandDefinition(
        "project.setting.change",
        BusinessId("PERM-PROJECT-CHANGE"),
        "project_setting_changed",
    ),
    handler,
)
```

## Ergebnisvertrag

Erfolgreiche Ausführungen liefern `Result[ProjectCommandExecutionResult]`. Ablehnungen und fehlende Registrierungen liefern strukturierte Fehlermeldungen und behalten die Korrelationskennung des Commands bei.

## Fehlerkennungen

- `ERR-PRJ-CMD-0001`: Kein Handler registriert.
- `ERR-PRJ-CMD-0002`: Begründung fehlt.
- `ERR-PRJ-CMD-0003`: Projektbezogene Autorisierung lehnt ab.

## Transaktionsgrenze

Die aufrufende `SQLiteUnitOfWork` bleibt die Transaktionsgrenze. Audit-Eintrag und fachliche Änderung werden gemeinsam bestätigt oder zurückgerollt.

## Qualitätsnachweis

Die Tests prüfen erfolgreiche Ausführung, strukturierte Ablehnung mit Audit-Nachweis, fehlende Registrierung und doppelte Registrierung.
