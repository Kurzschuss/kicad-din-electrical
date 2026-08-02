# Schnellstart: erstes Symbol in KiCad verwenden

Diese Kurzanleitung zeigt den kürzesten Weg vom heruntergeladenen Repository bis zu einem platzierten Symbol. Für ausführliche Erklärungen und Fehlerbehebung siehe [INSTALL.md](INSTALL.md).

## Voraussetzungen

- KiCad ist installiert.
- Das Repository `kicad-din-electrical` wurde mit GitHub Desktop geklont oder als ZIP-Datei entpackt.
- Der Repositoryordner bleibt dauerhaft an diesem Speicherort.

## 1. Symbolbibliothek hinzufügen

1. KiCad starten.
2. Den **Symbol-Editor** öffnen.
3. **Einstellungen → Symbolbibliotheken verwalten** wählen.
4. Für eine dauerhafte Einrichtung die Registerkarte **Globale Bibliotheken** verwenden.
5. Auf **Vorhandene Bibliothek hinzufügen** klicken.
6. Im Repository diesen Ordner öffnen:

```text
symbols/DIN_Electrical_Symbols/
```

7. Eine gewünschte Datei mit der Endung `.kicad_sym` auswählen, zum Beispiel:

```text
Z_DIN_Control.kicad_sym
```

8. Als Bibliotheksnamen den Dateinamen ohne Endung verwenden:

```text
Z_DIN_Control
```

9. Mit **OK** bestätigen.

## 2. Passende Footprintbibliothek hinzufügen

1. Den **Footprint-Editor** öffnen.
2. **Einstellungen → Footprintbibliotheken verwalten** wählen.
3. Wieder **Globale Bibliotheken** auswählen.
4. Auf **Vorhandene Bibliothek hinzufügen** klicken.
5. Im Repository den passenden `.pretty`-Ordner auswählen, zum Beispiel:

```text
footprints/Z_DIN_Control.pretty/
```

6. Als Bibliotheksnamen den Ordnernamen ohne `.pretty` verwenden:

```text
Z_DIN_Control
```

7. Mit **OK** bestätigen.

## 3. Erstes Symbol platzieren

1. Ein KiCad-Projekt öffnen oder ein neues Projekt anlegen.
2. Den **Schaltplaneditor** öffnen.
3. **Symbol hinzufügen** wählen oder die Taste `A` drücken.
4. Nach `Z_` oder dem Bibliotheksnamen suchen.
5. Ein Symbol auswählen und im Schaltplan platzieren.

## 4. Footprint prüfen

1. Das platzierte Symbol markieren.
2. Die Symboleigenschaften öffnen.
3. Das Feld **Footprint** prüfen oder die Footprint-Zuordnung öffnen.
4. Nach der passenden `Z_`-Bibliothek suchen.

Eine qualifizierte Footprint-ID hat dieses Format:

```text
<Bibliothek>:<Footprint>
```

Beispiel:

```text
Z_DIN_Module_18mm:Z_DIN_Module_18mm
```

## 5. Kurze Funktionskontrolle

Die Einrichtung ist erfolgreich, wenn:

- die Bibliothek im Symbol-Auswahldialog erscheint,
- sich ein Symbol platzieren lässt,
- die passende Footprintbibliothek angezeigt wird,
- und keine Meldung über eine fehlende Bibliothek erscheint.

## 6. Lokale Tests starten

Unter Windows:

1. Im Repositoryordner `run_tests.bat` doppelklicken.
2. Im Menü **1 – Schneller Testlauf** wählen.
3. Nach erfolgreichem Lauf mit **0 – Programm verlassen** beenden.

Weitere Testoptionen erklärt [TESTING.md](TESTING.md).

## Wenn etwas nicht funktioniert

Siehe die ausführliche [Installationsanleitung](INSTALL.md). Dort werden unter anderem globale und projektbezogene Bibliotheken, Pfadprobleme, fehlende Symbole und nicht gefundene Footprints erklärt.
