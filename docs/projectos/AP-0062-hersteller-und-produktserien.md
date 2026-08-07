# AP-0062 – Hersteller-, Produktserien- und Herstellerreferenzmodell

## Ziel

AP-0062 ergänzt den generischen Gerätekatalog aus AP-0061 um Hersteller und Produktserien, ohne Artikelnummern, Lieferanten oder Preise vorwegzunehmen.

## Domänenobjekte

- `Manufacturer`: Hersteller mit Name, Kurzname, Ländercode, Webadressen, Status und Revision.
- `ProductSeries`: Produktserie mit eindeutiger Zuordnung zu genau einem Hersteller.
- `ManufacturerReference`: Verbindung eines Kataloggeräts mit einem aktiven Hersteller und optional einer aktiven Produktserie.

## Invarianten

- Hersteller benötigen einen Namen.
- Ländercodes verwenden ISO-3166-Alpha-2.
- Webadressen müssen vollständige HTTP- oder HTTPS-URLs sein.
- Seriennamen sind innerhalb eines Herstellers ohne Beachtung der Groß-/Kleinschreibung eindeutig.
- Eine Produktserie kann nicht einem anderen Hersteller zugeordnet werden.
- Herstellerreferenzen dürfen nur aktive Hersteller und aktive Serien verwenden.
- Änderungen erzeugen neue unveränderliche Objekte und erhöhen die Revision.

## Fehlerkennungen

- `ERR-MAN-0001`: Herstellername fehlt.
- `ERR-MAN-0002`: Produktserie gehört zu einem anderen Hersteller.
- `ERR-MAN-0003`: Herstellerreferenz verwendet inaktive oder ungültige Stammdaten.
- `ERR-MAN-0004`: Serienname ist beim Hersteller bereits vorhanden.

## Abgrenzung

Nicht Bestandteil dieses Arbeitspakets sind Herstellerartikelnummern, GTIN/EAN, Lieferanten, Preise, Lagerbestände, Normen und KiCad-Artefakte.

## Verifikation

Die Tests prüfen Normalisierung, URL- und Ländercodevalidierung, Revisionen, Statuswechsel, Seriennamens-Eindeutigkeit und Herstellerreferenzen.
