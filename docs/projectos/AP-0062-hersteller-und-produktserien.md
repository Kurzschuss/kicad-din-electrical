# AP-0062 – Hersteller-, Produktserien- und Herstellerreferenzmodell

## Ziel

AP-0062 ergänzt den generischen Gerätekatalog aus AP-0061 um Hersteller und Produktserien, ohne Artikelnummern, Lieferanten oder Preise vorwegzunehmen.

## Domänenobjekte

- `Manufacturer`: Hersteller mit Name, Kurzname, Ländercode, Webadressen, Status und Revision.
- `ProductSeries`: Produktserie mit eindeutiger Zuordnung zu genau einem Hersteller.
- `ManufacturerReference`: Verbindung eines Kataloggeräts mit einem aktiven Hersteller und optional einer aktiven Produktserie.
- `ManufacturerRegistryEntry`: dateibasierter Stammdateneintrag mit stabilem Katalognamen, Suchaliasen und offizieller Prüfquelle.

## Kanonische Hersteller-Stammdaten

Die verifizierte Ausgangsliste liegt unter:

`data/manufacturers/manufacturers.json`

Sie enthält zunächst folgende Hersteller beziehungsweise historische Herstellerkennung:

- ABB
- Siemens
- Hager
- Eaton
- Schneider Electric
- Doepke
- Siedle
- Shelly
- Theben
- Eltako
- Klöckner-Moeller
- LCN / Issendorff KG
- Phoenix Contact
- WAGO
- Weidmüller
- Pollmann Elektrotechnik

Jeder Eintrag besitzt eine stabile `manufacturer_id`, eine technische `object_id`, einen `catalog_name`, den Firmen-/Rechtsnamen, optional einen Kurzname, Ländercode, Website, Status, Suchaliase und eine offizielle Prüfquelle. Der `catalog_name` ist der bevorzugte Wert für das Feld `manufacturer` im technischen Gerätekatalog.

`Klöckner-Moeller` bleibt als historische Hersteller-/Markenkennung erhalten und ist im Stammdatenregister `INACTIVE`: Eaton dokumentiert die Umbenennung zu Moeller GmbH im Jahr 1999 und die Übernahme der Moeller-Gruppe im Jahr 2008. Alte Bestandsgeräte können damit weiterhin eindeutig zugeordnet werden, ohne Klöckner-Moeller als aktuellen Hersteller darzustellen.

Für `LCN` ist `Issendorff KG` der Firmenname. Schreibweisen wie `LCN Issendorf` werden nur als Suchalias aufgenommen; die offizielle Schreibweise bleibt `Issendorff` mit zwei `f`.

## Z_Cockpit

Die Herstellerseite führt das Stammdatenregister mit den real vorhandenen Zuordnungen aus dem technischen Gerätekatalog zusammen. Dadurch gilt:

- Hersteller sind bereits sichtbar, bevor ein konkretes Gerät oder eine Produktserie eingepflegt wurde;
- vorhandene Geräte werden weiterhin ausschließlich aus dem Gerätekatalog aggregiert;
- ein Hersteller kann daher zunächst `0` Serien und `0` Geräte besitzen;
- Stammdatenstatus, Land, Firmenname, Hersteller-ID, Aliase, Website und offizielle Prüfquelle werden im Inspector angezeigt;
- historische/inaktive Hersteller bleiben sichtbar und eindeutig gekennzeichnet.

Es entsteht keine zweite Pflege der Gerätezuordnungen: Das Stammdatenregister beschreibt den Hersteller, der Gerätekatalog beschreibt die Geräte.

## Invarianten

- Hersteller benötigen einen Namen.
- Ländercodes verwenden ISO-3166-Alpha-2.
- Webadressen müssen vollständige HTTP- oder HTTPS-URLs sein.
- `manufacturer_id` und `catalog_name` sind im Stammdatenregister eindeutig.
- Katalogname, Kurzname, Firmenname und Suchaliase dürfen nicht widersprüchlich mehreren Herstellern zugeordnet werden.
- Seriennamen sind innerhalb eines Herstellers ohne Beachtung der Groß-/Kleinschreibung eindeutig.
- Eine Produktserie kann nicht einem anderen Hersteller zugeordnet werden.
- Herstellerreferenzen dürfen nur aktive Hersteller und aktive Serien verwenden.
- Änderungen erzeugen neue unveränderliche Objekte und erhöhen die Revision.
- Hersteller-Stammdaten mit `source_status: verified` müssen eine offizielle Prüfquelle besitzen.

## Fehlerkennungen

- `ERR-MAN-0001`: Herstellername fehlt.
- `ERR-MAN-0002`: Produktserie gehört zu einem anderen Hersteller.
- `ERR-MAN-0003`: Herstellerreferenz verwendet inaktive oder ungültige Stammdaten.
- `ERR-MAN-0004`: Serienname ist beim Hersteller bereits vorhanden.

## Abgrenzung

Nicht Bestandteil dieses Arbeitspakets sind Herstellerartikelnummern, GTIN/EAN, Lieferanten, Preise, Lagerbestände, Normen und KiCad-Artefakte. Konkrete Produktserien und Artikel werden schrittweise je Gerätefamilie ergänzt und müssen auf Herstellerquellen zurückgeführt werden.

## Verifikation

Die Tests prüfen Normalisierung, URL- und Ländercodevalidierung, Revisionen, Statuswechsel, Seriennamens-Eindeutigkeit, Herstellerreferenzen sowie Eindeutigkeit und Aliasauflösung des dateibasierten Herstellerregisters. Die Z_Cockpit-Tests stellen zusätzlich sicher, dass registrierte Hersteller auch ohne Gerätezuordnung sichtbar bleiben.
