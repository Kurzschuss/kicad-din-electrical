# Notfallplan für den Repository-Schutz

Dieses Dokument beschreibt das Vorgehen, falls der Schutz des Branches `main` unbeabsichtigt die normale Projektarbeit blockiert.

## Grundsatz

Das Ruleset wird erst aktiviert, wenn ein Administrator sicher bestätigen kann, dass er es im Notfall bearbeiten oder deaktivieren darf.

## Typische Störungen

- erforderlicher CI-Statuscheck wurde umbenannt,
- CI startet nicht oder bleibt dauerhaft hängen,
- CODEOWNERS verlangt eine nicht verfügbare Freigabe,
- Pull Requests können trotz erfolgreicher Prüfung nicht gemergt werden,
- die Ruleset-Vorlage passt nicht mehr zu den aktuellen GitHub-Einstellungen.

## Sicheres Vorgehen

1. Keine Schutzdateien oder Prüfungen übereilt löschen.
2. Unter **Settings → Rules → Rulesets** das Ruleset `Main-Branch-Schutz` öffnen.
3. Zuerst den konkreten blockierenden Eintrag prüfen.
4. Falls nötig, das Ruleset vorübergehend auf `Evaluate` oder `Disabled` stellen.
5. Fehlerursache über einen separaten Branch korrigieren.
6. CI und Pull-Request-Ablauf erneut testen.
7. Ruleset erst anschließend wieder auf `Active` stellen.

## Häufigster Sonderfall: umbenannter Statuscheck

Wenn der Workflow oder Job umbenannt wurde, muss der Eintrag unter `required_status_checks` angepasst werden. Die aktuell vorbereitete Vorlage erwartet:

```text
pytest
```

## Schutz der Sicherheitsdateien

Diese Dateien werden über `.github/CODEOWNERS` dem Projektinhaber zugeordnet:

```text
config/authorized_developers.json
tools/check_repository_version.py
.github/CODEOWNERS
```

## Keine automatische Notfallumgehung

Im Projekt wird kein geheimer Schalter und kein fest eingebauter Bypass hinterlegt. Änderungen an der GitHub-Schutzkonfiguration erfolgen bewusst in den Repository-Einstellungen und werden anschließend dokumentiert.

## Nach einem Notfall

- Ursache dokumentieren,
- Ruleset-Vorlage aktualisieren,
- Tests ergänzen,
- erneute Aktivierung kontrolliert durchführen.
