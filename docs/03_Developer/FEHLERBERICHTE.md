# Automatische Fehlerberichte

Das Projekt kann fehlgeschlagene Prüfungen als ausführlichen, GitHub-tauglichen Markdown-Bericht dokumentieren.

## Bericht erzeugen

```text
python -m tools.create_error_report \
  --title "Python-Syntaxprüfung" \
  --command "python -m compileall -q distributions tests tools" \
  --exit-code 1 \
  --log build/LETZTER_FEHLER.log
```

Standardausgabe:

```text
build/FEHLERBERICHT.md
```

Der Bericht enthält:

- Name der fehlgeschlagenen Prüfung,
- ausgeführten Befehl,
- Fehlercode und Zeitpunkt,
- Betriebssystem und Python-Version,
- Git-Branch, Commit und Arbeitsstatus,
- vollständige erfasste Konsolenausgabe,
- Schritte zum Nachstellen,
- erwartetes und tatsächliches Ergebnis.

## Verwendung für GitHub

Die erzeugte Markdown-Datei kann als Text für ein GitHub-Issue verwendet werden. Ein Issue soll lokal nicht ungefragt erstellt werden. Die spätere Einbindung in `run_tests.bat` fragt deshalb vor einer Übertragung ausdrücklich nach.

Damit werden unnötige oder doppelte Issues vermieden, während die vollständige technische Fehlerbeschreibung automatisch vorbereitet wird.

## Datenschutz und Kontrolle

Vor dem Veröffentlichen sollte der Bericht kurz geprüft werden. Lokale Pfade, Branch-Namen und Konsolenausgaben können Informationen enthalten, die nicht öffentlich veröffentlicht werden sollen.
