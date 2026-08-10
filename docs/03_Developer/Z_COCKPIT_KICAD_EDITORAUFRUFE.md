# Z_Cockpit – direkte KiCad-Editoraufrufe

## Ziel

Das lokale Z_Cockpit kann aus der Geräte- und Bibliotheksansicht direkt zu den zugehörigen KiCad-Editoren wechseln, ohne eine zweite Bibliotheksdatenquelle einzuführen.

Die HTML-Datei selbst startet keine Prozesse. Sie erzeugt ausschließlich lokale Links mit dem URI-Schema:

```text
kicad-z:
```

Der Windows-Starter `tools/windows/open_z_cockpit.bat` registriert dieses Schema beim Start im aktuellen Benutzerprofil.

## Bedienung

Nach Auswahl eines Geräts oder Bibliothekssymbols erscheinen im bestehenden Eigenschaftenbereich:

- `Symbol-Editor öffnen`;
- `Footprint direkt öffnen`, sofern ein Repository-Footprint zugeordnet ist.

Die bestehende Bibliotheksarbeitslogik, der feste rechte Inspektor und der separate Geräte-ID-Scrollbereich werden nicht verändert.

## Footprint-Editor

Ein zugeordneter Footprint wird auf den festen Repositorypfad aufgelöst:

```text
footprints/<Footprint>.pretty/<Footprint>.kicad_mod
```

Anschließend startet der lokale Handler KiCad mit dem Footprint-Editor-Frame und genau dieser Datei:

```text
kicad.exe -f fpedit <datei.kicad_mod>
```

Der Dateipfad kommt nicht aus dem Browser. Der Browser übergibt nur den technischen Footprintnamen; der Handler bildet daraus selbst den erlaubten Repositorypfad und prüft dessen Existenz.

## Symbol-Editor

Für Symbole wird eine technische Referenz im Format

```text
<Bibliothek>:<Symbol>
```

übergeben. Der Handler prüft:

1. sichere Zeichenmenge der beiden IDs;
2. vorhandene Datei `symbols/<Bibliothek>.kicad_sym`;
3. vorhandenes Top-Level-Symbol in dieser Bibliothek.

KiCad stellt derzeit keinen stabilen öffentlichen Kommandozeilenaufruf bereit, der eine konkrete `Bibliothek:Symbol`-ID direkt im Symbol-Editor selektiert. Deshalb wird die geprüfte Referenz in die Windows-Zwischenablage gelegt und der Symbol-Editor über den KiCad-Manager-Hotkey `Ctrl+L` geöffnet.

Damit ist der Editoraufruf direkt, die konkrete Symbol-ID bleibt aber bewusst eine Such-/Auswahlhilfe und wird nicht durch fragile interne KiCad-Schnittstellen erzwungen.

## Windows-Protokoll

Registrierung:

```text
tools/windows/register_z_kicad_protocol.ps1
```

Handler:

```text
tools/windows/open_kicad_from_cockpit.ps1
```

Die Registrierung erfolgt ausschließlich unter:

```text
HKCU:\Software\Classes\kicad-z
```

Es werden keine Administratorrechte und keine `HKLM`-Änderungen benötigt.

## Sicherheitsgrenze

Der Protokollhandler akzeptiert nur die Aktionen:

```text
kicad-z://symbol?reference=...
kicad-z://footprint?name=...
```

Nicht akzeptiert werden:

- beliebige lokale Dateipfade aus der URL;
- Pfadseparatoren in technischen IDs;
- `..`-Traversal;
- frei übergebene Executables;
- Shell-Befehle;
- `Invoke-Expression` oder vergleichbare dynamische Befehlsauswertung.

Alle geöffneten Dateien werden ausschließlich aus festen Repositorypfaden konstruiert.

## KiCad-Erkennung

Der Handler sucht `kicad.exe` in dieser Reihenfolge:

1. `PATH`;
2. neben einem gefundenen `kicad-cli.exe`;
3. üblichen KiCad-Installationsordnern unter `Program Files` und `Program Files (x86)`.

Fehlt KiCad, wird kein Ersatzprogramm gestartet.

## Verhalten ohne Protokollregistrierung

Wird `docs/site/z-cockpit.html` direkt geöffnet, ohne vorher `tools/windows/open_z_cockpit.bat` zu verwenden, kann der Browser das lokale `kicad-z:`-Schema möglicherweise nicht auflösen. Das Cockpit bleibt ansonsten vollständig nutzbar.

Die Protokollregistrierung ist im Windows-Starter absichtlich nicht blockierend: Ein Registrierungsfehler verhindert weder die Cockpit-Erzeugung noch die übrigen read-only Funktionen.

## Tests

`tests/test_kicad_editor_links.py` prüft unter anderem:

- Einbindung in Geräte- und Bibliotheksinspektor;
- unveränderte Bibliotheks-Scrollarchitektur;
- HKCU-only Registrierung;
- erlaubte Aktionen und ID-Validierung;
- Repositorypfad-Auflösung;
- Verbot dynamischer Shell-Auswertung;
- direkten `fpedit`-Aufruf;
- Symbol-Editor-Aufruf und Zwischenablageübergabe.
