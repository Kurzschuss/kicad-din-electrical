# AP-0069 – KiCad-Bibliothekstabellen und Pfadauflösung

**Status:** Implementiert  
**Sprint:** SPRINT-005 – Engineering Domain

## Ziel

ProjectOS liest die nativen KiCad-Bibliothekstabellen `sym-lib-table` und
`fp-lib-table` ausschließlich lesend ein. Die Tabellen bleiben die führende
Quelle für Bibliotheksnamen, Plugin-Typen, URIs, Optionen und Beschreibungen.

## KiCad-Standard zuerst

ProjectOS führt kein abweichendes Tabellenformat ein. Es übernimmt die nativen
KiCad-Felder:

- `name`,
- `type`,
- `uri`,
- `options`,
- `descr`.

Symbol- und Footprinttabellen bleiben vollständig getrennt. Eine vorhandene
Symbolbibliothek erfordert weder eine Footprinttabelle noch einen passenden
Footprint.

## Komponenten

- `KiCadLibraryTableType`
- `KiCadVariableContext`
- `KiCadLibraryTableEntry`
- `KiCadLibraryTable`
- `KiCadLibraryTableParser`

## Pfadauflösung

Variablen werden ausschließlich aus einem ausdrücklich übergebenen Kontext
aufgelöst. Typische Einträge sind:

```text
${KIPRJMOD}
${KICAD9_SYMBOL_DIR}
${KICAD9_FOOTPRINT_DIR}
```

ProjectOS liest keine beliebigen Prozessumgebungsvariablen. Dadurch bleibt die
Auflösung deterministisch, offlinefähig und reproduzierbar.

Relative URIs werden gegen `KIPRJMOD` aufgelöst. Absolute oder durch Variablen
erzeugte Pfade müssen innerhalb mindestens eines erlaubten Wurzelverzeichnisses
liegen.

## Sicherheitsregeln

- nur lokale URIs oder `file://`-URIs,
- unbekannte Variablen werden abgelehnt,
- relative Pfade benötigen `KIPRJMOD`,
- Pfade außerhalb erlaubter Wurzeln werden abgelehnt,
- aufsteigende Pfade dürfen ihre Wurzel nicht verlassen,
- Bibliotheksnamen sind innerhalb einer Tabelle ohne Beachtung der
  Groß-/Kleinschreibung eindeutig.

## Fehlerkennungen

| Kennung | Bedeutung |
|---|---|
| `ERR-KICAD-0032` | Variablenname fehlt |
| `ERR-KICAD-0033` | Variable besitzt keinen Pfad |
| `ERR-KICAD-0034` | Erlaubte Wurzel fehlt |
| `ERR-KICAD-0035` | Bibliotheksname fehlt |
| `ERR-KICAD-0036` | Plugin-Typ fehlt |
| `ERR-KICAD-0037` | URI fehlt |
| `ERR-KICAD-0038` | Falscher Bibliothekstabellentyp |
| `ERR-KICAD-0039` | Doppelter Bibliotheksname |
| `ERR-KICAD-0040` | Nicht lokale URI |
| `ERR-KICAD-0041` | Unbekannte Variable |
| `ERR-KICAD-0042` | Relativer Pfad ohne `KIPRJMOD` |
| `ERR-KICAD-0043` | Pfad außerhalb erlaubter Wurzeln |
| `ERR-KICAD-0044` | Pfad verlässt seine Wurzel |

## Tests

Die Tests prüfen:

- native Symboltabellen,
- native Footprinttabellen,
- Erhaltung aller KiCad-Felder,
- projektrelative Pfade,
- globale KiCad-Verzeichnisse,
- unabhängige Symbol- und Footprinttabellen,
- unbekannte Variablen,
- Pfade außerhalb erlaubter Wurzeln,
- doppelte Bibliotheksnamen,
- falsche Tabellenarten,
- nicht lokale URIs.

## Abgrenzung

AP-0069 liest und validiert Tabellenverträge. Das tatsächliche Laden der durch
die Tabellen referenzierten Dateien und der gemeinsame Snapshot-Aufbau werden
im folgenden Arbeitspaket verbunden.
