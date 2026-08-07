# AP-0063 – Herstellerprodukte und externe Produktkennungen

## Ziel

AP-0063 ergänzt den generischen Gerätekatalog und das Hersteller-/Serienmodell um konkrete Herstellerprodukte. Preise, Lieferanten, Lagerbestände und Beschaffung bleiben außerhalb dieses Arbeitspakets.

## Domänenobjekte

- `ManufacturerProduct`: konkretes Produkt eines Herstellers, optional innerhalb einer Produktserie
- `ProductIdentifier`: unveränderliche Produktkennung
- `ProductIdentifierType`: Herstellerartikelnummer, GTIN, EAN, UPC oder sonstiges Schema
- `ProductStatus`: `DRAFT`, `ACTIVE`, `DISCONTINUED`

## Invarianten

- Ein Produkt benötigt einen Namen, ein Kataloggerät und einen aktiven Hersteller.
- Eine zugeordnete Serie muss aktiv sein und zum Hersteller gehören.
- Handelskennungen werden auf Ziffern und zulässige Längen geprüft.
- Sonstige Kennungen benötigen ein benanntes Schema.
- Ein Kennungstyp darf pro Produkt nur einmal vorkommen.
- Ein aktives Produkt benötigt mindestens eine Kennung.
- Die letzte Kennung eines aktiven Produkts darf nicht entfernt werden.
- Ein abgekündigtes Produkt darf nicht reaktiviert werden.
- Externe Kennungen dürfen produktübergreifend nicht doppelt vergeben werden.

## Fehlerkennungen

- `ERR-PRD-0001`: Produktkennung leer
- `ERR-PRD-0002`: Handelskennung formal ungültig
- `ERR-PRD-0003`: Sonstige Kennung ohne Schema
- `ERR-PRD-0004`: Produktname fehlt
- `ERR-PRD-0005`: Hersteller oder Serie nicht aktiv
- `ERR-PRD-0006`: Serie gehört zu anderem Hersteller
- `ERR-PRD-0007`: Abgekündigtes Produkt darf nicht reaktiviert werden
- `ERR-PRD-0008`: Aktives Produkt ohne Kennung
- `ERR-PRD-0009`: Kennung nicht gefunden
- `ERR-PRD-0010`: Letzte Kennung eines aktiven Produkts
- `ERR-PRD-0011`: Produktkennung bereits vergeben
- `ERR-PRD-0012`: Kennungstyp innerhalb des Produkts doppelt

## Abgrenzung

Nicht enthalten sind Lieferantenartikelnummern, Preise, Währungen, Lagerorte, Verfügbarkeiten, Beschaffungsquellen oder historische Preislisten.
