# GitHub-Ruleset für den Main-Branch

Diese Vorlage ist für das Repository `Kurzschuss/kicad-din-electrical` vorbereitet, aber noch nicht zur sofortigen Aktivierung freigegeben.

## Vorlage

```text
.github/rulesets/main-branch-protection-v1.json
```

Die Vorlage schützt den Standard-Branch und verlangt:

- Änderungen über Pull Requests,
- eine Freigabe,
- Freigabe durch Code Owner für geschützte Dateien,
- erfolgreiche CI-Prüfung `pytest`,
- Auflösung offener Review-Unterhaltungen,
- lineare Historie und Squash-Merges,
- Schutz vor Löschen und Force-Push,
- einen aktuellen Branch vor dem Merge.

## Noch nicht importieren

Die Datei darf erst importiert werden, wenn die Bereitschaftsprüfung vollständig bestanden ist.

## Bereitschaftsprüfung

- [ ] CI läuft über einen längeren Zeitraum stabil.
- [ ] Der erforderliche Statuscheck heißt weiterhin `pytest`.
- [ ] `.github/CODEOWNERS` ist vorhanden und geprüft.
- [ ] `config/authorized_developers.json` ist geprüft.
- [ ] Versions- und Originalitätsprüfung wurden lokal getestet.
- [ ] Der Entwicklermodus wurde mit einem zugelassenen und einem nicht zugelassenen Benutzer getestet.
- [ ] Die Sperre bei Forks, lokalen Änderungen und veralteten Ständen wurde getestet.
- [ ] Eine Notfallanleitung ist vorhanden.
- [ ] Die importierte Vorschau wurde vor dem Speichern gemeinsam kontrolliert.

## Sichere Einführung

1. Vorlage in GitHub unter **Settings → Rules → Rulesets** importieren.
2. Vor dem Speichern alle Regeln noch einmal kontrollieren.
3. Zunächst sicherstellen, dass ein Repository-Administrator das Ruleset im Notfall bearbeiten oder deaktivieren kann.
4. Ruleset aktivieren.
5. Einen Test-Pull-Request erstellen.
6. Prüfen, ob CI, Review und CODEOWNERS korrekt greifen.
7. Erst danach den Schutz als produktiv dokumentieren.

## Wichtig

Die JSON-Datei ist eine versionierte Projektvorlage. GitHub-Einstellungen können sich ändern. Vor jeder späteren Verwendung muss die Vorlage erneut mit den aktuellen Repository-Einstellungen und Workflow-Namen abgeglichen werden.
