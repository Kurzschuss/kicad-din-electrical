# Automatische Fehlerberichte

Das Projekt kann fehlgeschlagene Prüfungen als ausführlichen, GitHub-tauglichen Markdown-Bericht dokumentieren.

## Befehl ausführen und automatisch dokumentieren

Der bevorzugte Weg führt den eigentlichen Prüfbefehl über den Ausführungshelfer aus:

```text
python -m tools.run_with_error_report \
  --title "Python-Syntaxprüfung" \
  --log build/LETZTER_TESTLAUF.log \
  --report build/FEHLERBERICHT.md \
  -- python -m compileall -q distributions tests tools
```

Die Konsolenausgabe bleibt dabei live sichtbar und wird gleichzeitig in der Logdatei gespeichert.

Bei erfolgreicher Prüfung entsteht nur das Protokoll. Bei einem Fehler wird zusätzlich automatisch erzeugt:

```text
build/FEHLERBERICHT.md
```

## Windows-Adapter

Für Batch-Dateien steht ein wiederverwendbarer Adapter zur Verfügung:

```text
tools\windows\run_with_error_report.bat ^
  "Python-Syntaxprüfung" ^
  "build\LETZTER_TESTLAUF.log" ^
  python -m compileall -q distributions tests tools
```

Der Adapter gibt bei einem Fehler den Pfad zum Bericht und zum vollständigen Konsolenprotokoll aus. Er soll im nächsten Schritt von `run_tests.bat` für die einzelnen Prüfungen verwendet werden.

## Bericht nachträglich erzeugen

Aus einer bereits vorhandenen Logdatei kann der Bericht auch separat erstellt werden:

```text
python -m tools.create_error_report \
  --title "Python-Syntaxprüfung" \
  --command "python -m compileall -q distributions tests tools" \
  --exit-code 1 \
  --log build/LETZTER_TESTLAUF.log
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
