# AP-0071 – Projektweite KiCad-Validierungspipeline

**Status:** Implementiert

## Ziel

AP-0071 führt die bisher getrennten KiCad-Prüfungen in einer deterministischen Projektpipeline zusammen. Grundlage bleiben native KiCad-Tabellen, native Bibliotheksdateien und das Prinzip `kicad_standard_first`.

## Ablauf

1. Vollständigen lokalen Snapshot aus `sym-lib-table`, `fp-lib-table` und expliziten 3D-Quellen aufbauen.
2. Jedes Validierungsziel eindeutig prüfen.
3. Zielzugehörigkeit aller Artefakte und Anschlüsse prüfen.
4. Artefaktanforderungen `REQUIRED`, `OPTIONAL` und `NOT_APPLICABLE` auswerten.
5. Referenzen, Prüfsummen und Symbolpins gegen den Snapshot validieren.
6. Fehlende Zuordnungen erforderlicher Anschlüsse melden.
7. Dokumentierte Abweichungen vom KiCad-Standard als sichtbare Informationen ausgeben.

## Optionale Artefakte

Ein Symbol erzeugt keine automatische Pflicht für Footprint oder 3D-Modell. Eine reine Symbolkonfiguration bleibt gültig, solange die Zielanforderungen Footprints oder 3D-Modelle nicht als `REQUIRED` kennzeichnen.

## Neue Komponenten

- `KiCadProjectValidationTarget`
- `KiCadProjectValidationResult`
- `KiCadProjectValidationPipeline`

## Ergebnisvertrag

Das Ergebnis enthält:

- den erzeugten vollständigen Snapshot oder `None` bei einem Aufbaufehler,
- alle sortierten Findings,
- die Anzahl geprüfter Ziele,
- `valid`,
- `exception_count`.

Dokumentierte Ausnahmen verwenden `INFO-KICAD-0001`. Sie machen das Ergebnis nicht ungültig, bleiben aber vollständig sichtbar.

## Neue Meldungskennungen

- `ERR-KICAD-0051`: Validierungsziel doppelt vorhanden
- `ERR-KICAD-0052`: Artefakt gehört nicht zum Validierungsziel
- `ERR-KICAD-0053`: Anschluss gehört nicht zum Validierungsziel
- `ERR-KICAD-0054`: Erforderlicher Anschluss ist keinem Symbolpin zugeordnet
- `INFO-KICAD-0001`: Dokumentierte Abweichung vom KiCad-Standard

## Grenzen

Die Pipeline verändert keine KiCad-Dateien und greift nicht selbstständig auf Dateisystem oder Netzwerk zu. Alle Tabellen, Dateien und Variablenkontexte werden explizit bereitgestellt.
