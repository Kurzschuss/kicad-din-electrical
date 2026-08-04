# Lokale GitHub-Issue-Vorschau

Aus einem vorhandenen Fehlerbericht kann eine lokale, bereinigte GitHub-Issue-Vorschau erzeugt werden:

```text
python -m tools.create_github_issue_preview
```

Voraussetzung:

```text
build/FEHLERBERICHT.md
```

Erzeugte Dateien:

```text
build/GITHUB_ISSUE_TITEL.txt
build/GITHUB_ISSUE_VORSCHAU.md
```

## Datenschutzfilter

Vor der Vorschauerzeugung werden derzeit automatisch maskiert:

- Benutzername in Windows-Pfaden unter `C:\Users\...`
- Werte typischer Zugangsdaten wie `TOKEN`, `API_KEY`, `SECRET` und `PASSWORD`

Die erzeugte Vorschau muss trotzdem vollständig gelesen und geprüft werden.

## Sicherheitsregel

Der Generator erzeugt ausschließlich lokale Dateien. Er öffnet kein GitHub-Issue und überträgt keine Daten ins Internet. Eine spätere Veröffentlichung muss immer getrennt und ausdrücklich bestätigt werden.
