# AP-0064 – Normen-, Regelwerks- und Konformitätsreferenzmodell

## Ziel

AP-0064 stellt ein neutrales Referenzmodell für Normen, Ausgaben und Konformitätsbezüge bereit. Es speichert keine urheberrechtlich geschützten Normtexte und trifft keine rechtliche Aussage über die tatsächliche Gültigkeit oder Anwendbarkeit einer Norm.

## Domänenobjekte

- `StandardReference`: Herausgeber, Bezeichnung, Titel, Ausgabe, Veröffentlichungsdatum und Status.
- `ConformityReference`: Bezug eines Kataloggeräts oder Herstellerprodukts auf eine aktive Normausgabe.

## Herausgeber

`IEC`, `DIN`, `VDE`, `EN`, `ISO` und `OTHER`.

## Lebenszyklen

Normen: `DRAFT → ACTIVE → WITHDRAWN`.

Konformität: `CLAIMED`, `VERIFIED`, `REJECTED`, `EXPIRED`.

Eine zurückgezogene Norm wird nicht reaktiviert. Eine verifizierte Konformität benötigt eine Nachweisreferenz.

## Invarianten

- Normbezeichnung, Titel und Ausgabe sind verpflichtend.
- Kombination aus Herausgeber, Bezeichnung und Ausgabe ist eindeutig.
- Konformitätsreferenzen dürfen nur auf aktive Normen verweisen.
- Das Ende eines Gültigkeitszeitraums darf nicht vor dessen Beginn liegen.
- Konformität kann auf ein generisches Kataloggerät oder ein konkretes Herstellerprodukt zeigen.

## Fehlerkennungen

- `ERR-STD-0001`: Normbezeichnung fehlt.
- `ERR-STD-0002`: Normtitel fehlt.
- `ERR-STD-0003`: Normausgabe fehlt.
- `ERR-STD-0004`: Zurückgezogene Norm darf nicht reaktiviert werden.
- `ERR-STD-0005`: Verifizierte Konformität benötigt einen Nachweis.
- `ERR-STD-0006`: Ungültiger Gültigkeitszeitraum.
- `ERR-STD-0007`: Konformität verweist nicht auf eine aktive Norm.
- `ERR-STD-0008`: Normausgabe ist bereits vorhanden.

## Abgrenzung

Nicht enthalten sind Normtexte, Lizenzverwaltung, automatische Rechtsgültigkeitsprüfung, länderspezifische Anwendungsregeln und fachliche Konformitätsbewertung. Diese Funktionen benötigen eigene Arbeitspakete und verlässliche Datenquellen.
