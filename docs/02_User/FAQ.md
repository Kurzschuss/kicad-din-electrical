# Häufig gestellte Fragen

Diese Seite beantwortet typische Fragen zur Installation, Nutzung und Pflege der KiCad-DIN-Electrical-Bibliotheken.

## Muss ich alle Symbolbibliotheken installieren?

Nein. Es können nur die Bibliotheken eingebunden werden, die tatsächlich benötigt werden. Für einen einfachen Test genügt beispielsweise eine einzelne `.kicad_sym`-Datei zusammen mit dem gleichnamigen `.pretty`-Ordner.

## Muss zu jeder Symbolbibliothek eine Footprintbibliothek eingebunden werden?

Für die vollständige Nutzung ist das empfohlen. Zu jeder Symbolbibliotheksdatei existiert unter `footprints/` ein gleichnamiger `.pretty`-Ordner.

Beispiel:

```text
symbols/DIN_Electrical_Symbols/Z_DIN_Control.kicad_sym
footprints/Z_DIN_Control.pretty/
```

## Darf eine `.pretty`-Bibliothek mehrere Footprints enthalten?

Ja. Eine `.pretty`-Bibliothek darf mehrere `.kicad_mod`-Dateien enthalten. Das ist sinnvoll, wenn eine Symbolbibliothek mehrere Symbole oder mehrere passende Bauformen umfasst.

## Warum beginnen die Bibliotheksnamen mit `Z_`?

Das Präfix sorgt dafür, dass die projektinternen Bibliotheken in KiCad eindeutig erkennbar und alphabetisch gebündelt sind.

## Soll ich die Bibliotheken global oder projektbezogen einbinden?

Für die regelmäßige Nutzung sind globale Bibliotheken sinnvoll. Für Tests, portable Projekte oder unterschiedliche Bibliotheksstände eignen sich projektbezogene Bibliotheken.

Weitere Einzelheiten stehen in [INSTALL.md](INSTALL.md).

## Was passiert nach einem Update mit GitHub Desktop?

Solange der lokale Repositoryordner nicht verschoben wird, bleiben die in KiCad gespeicherten Pfade normalerweise gültig. KiCad verwendet anschließend automatisch die aktualisierten Dateien.

## Was passiert, wenn ich den Repositoryordner verschiebe?

Dann stimmen die gespeicherten Bibliothekspfade nicht mehr. Die betroffenen Symbol- und Footprintbibliotheken müssen in KiCad auf den neuen Speicherort umgestellt oder erneut registriert werden.

## Warum findet KiCad ein Symbol oder einen Footprint nicht?

Typische Ursachen sind:

- der Bibliothekspfad ist falsch,
- eine Datei oder ein `.pretty`-Ordner wurde verschoben,
- das Projekt verwendet einen veralteten Bibliotheksnamen,
- der Name links oder rechts vom Doppelpunkt einer Bibliotheks-ID ist falsch.

Eine Footprint-ID hat das Format:

```text
<Bibliothek>:<Footprint>
```

## Was bedeutet eine ID wie `Z_DIN_Module_18mm:Z_DIN_Module_18mm`?

Links vom Doppelpunkt steht der Name der `.pretty`-Bibliothek ohne Endung. Rechts steht der interne Name des Footprints.

## Warum dürfen die Namen links und rechts vom Doppelpunkt unterschiedlich sein?

Weil eine `.pretty`-Bibliothek mehrere Footprints enthalten darf. Der Bibliotheksname beschreibt den Ordner, während der Footprintname eine einzelne `.kicad_mod`-Datei bezeichnet.

## Wie starte ich die Tests unter Windows?

Im Repositoryordner `run_tests.bat` doppelklicken und im Menü die gewünschte Prüfung auswählen. Mit **0 – Programm verlassen** wird das Menü beendet.

Ausführliche Hinweise stehen in [TESTING.md](TESTING.md).

## Was ist `.venv` und muss ich sie verwenden?

`.venv` ist eine lokale Python-Umgebung für dieses Repository. Sie hält die benötigten Python-Pakete von anderen Projekten getrennt. Ihre Verwendung wird empfohlen, ist für das Testmenü aber nicht zwingend erforderlich.

## Verändern die Tests meine Bibliotheksdateien?

Nein. Die vorhandenen Tests lesen und prüfen die Dateien. Sie kontrollieren unter anderem Struktur, Dateinamen, interne Namen und Referenzen.

## Wo beginne ich als KiCad-Einsteiger?

Am besten mit [QUICKSTART.md](QUICKSTART.md). Die ausführlichere Einrichtung und Fehlerbehebung stehen in [INSTALL.md](INSTALL.md).

## Wo werden neue Ideen gesammelt?

Neue und langfristige Vorschläge werden in der [Ideensammlung](../01_Roadmap/IDEAS.md) dokumentiert. Getroffene Architekturentscheidungen stehen in [DECISIONS.md](../01_Roadmap/DECISIONS.md).
