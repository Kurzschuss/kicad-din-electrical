# Versionsprüfung vor GitHub-Meldungen

Vor dem Erzeugen einer GitHub-Issue-Vorschau wird geprüft, ob der lokale Arbeitsstand den aktuellen Stand von `origin/main` vollständig enthält.

## Zweck

Fehler sollen nicht aus einem veralteten Softwarestand gemeldet werden, wenn sie in einer neueren Version möglicherweise bereits behoben wurden.

## Ablauf

1. `git fetch --quiet origin main` aktualisiert ausschließlich die Informationen über den entfernten Stand.
2. Lokales `HEAD` und `origin/main` werden ermittelt.
3. Die Anzahl voraus- und zurückliegender Commits wird bestimmt.
4. Es wird geprüft, ob `origin/main` ein Vorfahr des lokalen `HEAD` ist.
5. Das Ergebnis wird unter `build/VERSIONSPRUEFUNG.json` gespeichert.

Die Prüfung verändert keine lokalen Dateien und führt weder `git pull` noch einen automatischen Merge aus.

## Zulässige Zustände

### Aktuell

Lokales `HEAD` und `origin/main` sind identisch.

### Aktuell mit lokalen Änderungen

Ein Feature-Branch enthält den aktuellen Stand von `origin/main` vollständig und besitzt zusätzliche lokale Commits. Dieser Zustand ist für eine Fehleranalyse zulässig.

## Gesperrte Zustände

### Veraltet

Der aktuelle Stand von `origin/main` ist im lokalen Branch nicht vollständig enthalten. Die Issue-Vorschau bleibt gesperrt. Zuerst muss aktualisiert und anschließend erneut getestet werden.

### Unbekannt

Die Aktualität kann nicht sicher bestätigt werden, beispielsweise weil GitHub nicht erreichbar ist, `origin/main` fehlt oder Git nicht ausgeführt werden kann. Auch dann bleibt die Issue-Vorschau gesperrt.

## Sicherheitsregel

Eine GitHub-Meldung darf nur vorbereitet oder später veröffentlicht werden, wenn die Versionsprüfung den Status `aktuell` oder `aktuell_mit_lokalen_aenderungen` bestätigt.

Der aktuelle Workflow erzeugt weiterhin ausschließlich eine lokale Vorschau. Eine automatische Veröffentlichung ist nicht enthalten.

## Manuelle Ausführung

```text
python -m tools.check_repository_version
```

Ergebnisdatei:

```text
build/VERSIONSPRUEFUNG.json
```
