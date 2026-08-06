# AP-0075 – Persistente und auditierbare KiCad-Freigabeentscheidungen

## Ziel

Technische Entscheidungen des KiCad-Quality-Gates werden gemeinsam mit menschlicher Verantwortung und Begründung unveränderlich gespeichert.

## Modell

`KiCadReleaseAuditRecord` enthält:

- Freigabeentscheidungskennung
- Projektkennung
- Kennung des bewerteten jüngsten Validierungslaufs, sofern vorhanden
- Entscheidung `APPROVED`, `REJECTED` oder `INSUFFICIENT_DATA`
- Entscheidungszeitpunkt mit Zeitzone
- handelnde Person
- aktive verantwortliche Rolle
- Korrelationskennung
- verpflichtende Begründung
- Finding-Codes des Quality-Gates

## Persistenz

Die SQLite-Tabelle `projectos_kicad_release_audit` ist nur anhängbar. Bereits verwendete Entscheidungskennungen dürfen nicht überschrieben werden. Projektbezogene Abfragen liefern die jüngste Entscheidung zuerst.

## Abgrenzung

Die gespeicherte Entscheidung dokumentiert eine technische Qualitätsbewertung. Sie ersetzt keine gesetzlich, normativ oder organisatorisch erforderliche Freigabe durch befugte Fachpersonen.

## Fehlerkennungen

- `ERR-KICAD-0074`: Entscheidungszeitpunkt ohne Zeitzone
- `ERR-KICAD-0075`: Begründung fehlt
- `ERR-KICAD-0076`: Entscheidungskennung bereits vorhanden
- `ERR-KICAD-0077`: Freigabeentscheidung nicht gefunden
