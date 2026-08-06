# AP-0066 – KiCad-Anschluss- und Pinzuordnung

## Ziel

Fachliche Geräteanschlüsse werden eindeutig mit Pins aktiver KiCad-Symbole verbunden.

## Grundsatz

ProjectOS hält sich grundsätzlich an die KiCad-Daten- und Bibliotheksverträge. Abweichungen sind nur zulässig, wenn sie ausdrücklich als Ausnahme markiert und fachlich begründet werden.

## Domänenobjekte

- `DeviceTerminal`: fachlicher Anschluss eines Kataloggeräts oder Herstellerprodukts
- `KiCadSymbolPin`: Pinnummer, Pinname, elektrische Art und Symboleinheit gemäß KiCad
- `TerminalPinAssignment`: eindeutige Verbindung zwischen Anschluss und Symbolpin

## KiCad-Pintypen

Unterstützt werden `INPUT`, `OUTPUT`, `BIDIRECTIONAL`, `TRI_STATE`, `PASSIVE`, `FREE`, `UNSPECIFIED`, `POWER_INPUT`, `POWER_OUTPUT`, `OPEN_COLLECTOR`, `OPEN_EMITTER` und `NO_CONNECT`.

## Konformität

- `STANDARD`: reguläre, KiCad-konforme Zuordnung ohne Ausnahmegrund
- `EXCEPTION`: begründete Abweichung vom KiCad-Standard

Eine Ausnahme ohne Begründung wird abgelehnt. Ein Standardeintrag darf keinen Ausnahmegrund enthalten.

## Invarianten

- Zuordnungen verwenden ausschließlich aktive KiCad-Symbole.
- Anschluss und Symbol müssen dasselbe Zielobjekt referenzieren.
- Ein Anschluss darf einem Symbol nur einmal zugeordnet werden.
- Eine Kombination aus Symboleinheit und Pinnummer darf je Symbol nur einmal verwendet werden.
- Erforderliche, noch nicht zugeordnete Anschlüsse können deterministisch ermittelt werden.

## Fehlerkennungen

- `ERR-KICAD-0008`: Anschlussbezeichnung fehlt
- `ERR-KICAD-0009`: Pinnummer fehlt
- `ERR-KICAD-0010`: ungültige Symboleinheit
- `ERR-KICAD-0011`: Zuordnung verwendet kein Symbol
- `ERR-KICAD-0012`: Symbol ist nicht aktiv
- `ERR-KICAD-0013`: Anschluss und Symbol gehören zu unterschiedlichen Zielen
- `ERR-KICAD-0014`: Anschluss ist bereits zugeordnet
- `ERR-KICAD-0015`: Symbolpin ist bereits belegt
- `ERR-KICAD-0016`: Ausnahmegrund fehlt
- `ERR-KICAD-0017`: Standardeintrag enthält einen Ausnahmegrund

## Abgrenzung

Nicht Bestandteil sind das Parsen nativer KiCad-Dateien, automatische Symbolerzeugung, ERC-Ausführung und elektrische Berechnungen. Diese Funktionen bauen später auf diesem Modell auf.
