# Bibliotheken in KiCad einbinden

Diese Anleitung beschreibt die Einbindung der Symbol- und Footprintbibliotheken in eine vorhandene KiCad-Installation. Sie richtet sich ausdrücklich auch an Einsteiger.

## 1. Repository herunterladen

Das Repository kann mit GitHub Desktop geklont oder als ZIP-Datei heruntergeladen werden.

Wichtig ist, dass der Projektordner dauerhaft an seinem Speicherort bleibt. Wird er später verschoben, müssen die Bibliothekspfade in KiCad angepasst werden.

Beispiel unter Windows:

```text
C:\Users\<Benutzername>\Documents\GitHub\kicad-din-electrical
```

## 2. Symbolbibliotheken einbinden

1. KiCad starten.
2. **Symbol-Editor** öffnen.
3. **Einstellungen → Symbolbibliotheken verwalten** wählen.
4. Entscheiden, ob die Bibliotheken global oder nur für ein Projekt gelten sollen.
5. Auf **Vorhandene Bibliothek hinzufügen** klicken.
6. Zum Ordner wechseln:

```text
symbols/DIN_Electrical_Symbols/
```

7. Die gewünschten Dateien mit der Endung `.kicad_sym` auswählen.
8. Als Bibliotheksnamen jeweils den Dateinamen ohne `.kicad_sym` verwenden.

Beispiel:

```text
Datei: Z_DIN_Control.kicad_sym
Bibliotheksname in KiCad: Z_DIN_Control
```

## 3. Footprintbibliotheken einbinden

1. Den **Footprint-Editor** öffnen.
2. **Einstellungen → Footprintbibliotheken verwalten** wählen.
3. Wieder zwischen globaler und projektbezogener Tabelle entscheiden.
4. Auf **Vorhandene Bibliothek hinzufügen** klicken.
5. Zum Ordner `footprints/` wechseln.
6. Die gewünschten Ordner mit der Endung `.pretty` auswählen.

Beispiel:

```text
footprints/Z_DIN_Control.pretty/
```

Der in KiCad angezeigte Bibliotheksname lautet dann:

```text
Z_DIN_Control
```

Eine `.pretty`-Bibliothek kann mehrere `.kicad_mod`-Dateien enthalten.

## 4. Global oder nur für ein Projekt?

### Globale Bibliothek

Die Bibliothek steht anschließend in allen KiCad-Projekten dieses Computers zur Verfügung.

Das ist sinnvoll, wenn die Bibliotheken regelmäßig genutzt werden.

### Projektbezogene Bibliothek

Die Bibliothek gilt nur für das gerade geöffnete Projekt.

Das ist sinnvoll für Tests, portable Projekte oder wenn verschiedene Bibliotheksstände parallel verwendet werden sollen.

## 5. Funktion prüfen

### Symbole prüfen

1. Ein Schaltplanprojekt öffnen.
2. **Symbol hinzufügen** wählen.
3. Nach einem Bibliotheksnamen mit Präfix `Z_` suchen.
4. Ein Symbol platzieren.

### Footprints prüfen

1. Im Symbol die Footprint-Zuordnung öffnen oder den Footprint-Browser starten.
2. Nach einer Bibliothek mit Präfix `Z_` suchen.
3. Prüfen, ob die enthaltenen Footprints angezeigt werden.

## 6. Nach einer Aktualisierung

Wenn das Repository mit GitHub Desktop aktualisiert wird, bleiben die Pfade normalerweise unverändert. KiCad verwendet dann automatisch die aktualisierten Dateien.

Wurden Bibliotheksdateien oder Ordner umbenannt, kann eine erneute Registrierung nötig sein.

## 7. Häufige Probleme

### Bibliothek wird nicht angezeigt

- Pfad in der Bibliothekstabelle prüfen.
- Kontrollieren, ob die Datei oder der `.pretty`-Ordner noch existiert.
- KiCad nach größeren Änderungen neu starten.

### Fragezeichen oder fehlende Symbole

Das Projekt verweist möglicherweise auf einen alten Bibliotheksnamen. Die aktuelle Struktur verwendet Bibliotheksnamen mit dem Präfix `Z_`.

### Footprint wird nicht gefunden

Eine qualifizierte Footprint-ID hat das Format:

```text
<Bibliothek>:<Footprint>
```

Beispiel:

```text
Z_DIN_Control:Z_DIN_Pushbutton
```

Der Name links vom Doppelpunkt ist der `.pretty`-Ordner ohne Endung. Der Name rechts ist der interne Name des Footprints.

## 8. Tests ausführen

Unter Windows kann anschließend `run_tests.bat` per Doppelklick gestartet werden. Das Menü prüft unter anderem Bibliotheksstruktur, Namen und Referenzen.

Weitere Einzelheiten stehen in [TESTING.md](TESTING.md).
