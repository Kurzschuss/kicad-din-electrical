# Repositoryprüfung vor GitHub-Meldungen

Vor einer GitHub-Issue-Vorschau werden Aktualität, Herkunft und Unverändertheit des lokalen Repositorys geprüft.

## Normalbetrieb

Eine Meldung wird nur freigegeben, wenn alle Bedingungen erfüllt sind:

1. `origin` zeigt auf `Kurzschuss/kicad-din-electrical`.
2. `git fetch origin main` war erfolgreich.
3. Lokales `HEAD` entspricht exakt `origin/main`.
4. `git status --porcelain --untracked-files=normal` liefert keine Änderungen.

Forks, lokale Commits, geänderte Dateien und nicht verfolgte Dateien sperren die Meldung. So können Fehler aus angepassten Benutzerständen nicht automatisch dem Originalprojekt zugeordnet werden.

## Entwicklermodus

Der Entwicklermodus ist für freigegebene Projektentwickler vorgesehen. Er wird lokal gesetzt:

```text
set KICAD_DIN_DEVELOPER_MODE=1
```

Der Schalter allein reicht nicht. Zusätzlich müssen alle Bedingungen erfüllt sein:

- `origin` ist das offizielle Repository,
- der Branch ist nicht hinter `origin/main`,
- GitHub CLI (`gh`) ist angemeldet,
- `gh api user --jq .login` liefert einen Benutzer aus `config/authorized_developers.json`.

Ist eine Bedingung nicht erfüllt, bleibt die Meldung gesperrt.

## Geschützte Whitelist

Die freigegebenen GitHub-Benutzer stehen in:

```text
config/authorized_developers.json
```

`CODEOWNERS` ordnet Änderungen an Whitelist, Prüfskript und `CODEOWNERS` selbst dem Projektinhaber `@Kurzschuss` zu. Damit dies technisch erzwungen wird, muss für `main` in den GitHub-Branch-Regeln zusätzlich eine erforderliche Code-Owner-Prüfung aktiviert sein.

Eine lokale Änderung der Whitelist hilft einem normalen Benutzer nicht: Sie macht den Arbeitsbaum unsauber und sperrt den Normalbetrieb. Im Entwicklermodus wird außerdem ein tatsächlich über `gh` authentifizierter Whitelist-Benutzer verlangt.

## Reihenfolge

1. Remote-Herkunft prüfen.
2. `origin/main` abrufen.
3. Rückstand gegenüber `origin/main` prüfen.
4. Originalzustand des Arbeitsbaums prüfen.
5. Nur bei Bedarf den doppelt abgesicherten Entwicklermodus prüfen.
6. Ergebnis unter `build/VERSIONSPRUEFUNG.json` speichern.
7. Nur bei Freigabe die lokale Issue-Vorschau erzeugen.

Die Prüfung führt kein `git pull`, keinen Merge und keine automatische GitHub-Veröffentlichung aus.

## Statuswerte

- `original_aktuell`: unveränderte aktuelle Originalversion.
- `entwickler_freigegeben`: authentifizierter Whitelist-Entwickler im Entwicklermodus.
- `nicht_offizielles_repository`: Fork oder anderes Remote.
- `veraltet`: lokaler Stand liegt hinter `origin/main`.
- `lokal_veraendert`: lokale Dateien oder Commits weichen vom Original ab.
- `entwicklermodus_nicht_autorisiert`: Entwicklermodus ohne gültige Whitelist-Authentifizierung.
- `unbekannt`: sichere Prüfung nicht möglich.

## Manuelle Ausführung

```text
python -m tools.check_repository_version
```
