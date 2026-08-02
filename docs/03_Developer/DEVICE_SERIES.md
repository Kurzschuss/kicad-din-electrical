# Geräteserien und Varianten

Mit `tools/generate_device_variants.py` können mehrere Gerätevarianten aus gemeinsamen Stammdaten erzeugt werden.

## Aufbau

Serienbeschreibungen liegen unter:

```text
data/device_series/
```

Eine Datei enthält:

- eine eindeutige `series_id`,
- gemeinsame Werte unter `defaults`,
- abweichende Werte je Eintrag unter `variants`.

Beispiel:

```yaml
{
  "series_id": "generic.mcb-1p-template-series",
  "defaults": {
    "manufacturer": "Generic",
    "series": "Template MCB 1P",
    "symbol": "Z_MCB:MCB",
    "footprint_policy": "optional"
  },
  "variants": [
    {"variant_id": "b10", "part_number": "MCB-1P-B10", "rated_current_a": 10},
    {"variant_id": "b16", "part_number": "MCB-1P-B16", "rated_current_a": 16}
  ]
}
```

## Erzeugen

```text
python tools/generate_device_variants.py
```

Die Einzelgeräte werden unter `data/devices/generated/` gespeichert und anschließend vom normalen Gerätekatalog-Validator geprüft.

## Aktualität prüfen

```text
python tools/generate_device_variants.py --check
```

Der Prüfmodus schlägt fehl, wenn eine erzeugte Gerätedatei fehlt, veraltet ist oder nicht mehr zur Serienbeschreibung gehört.

## Regeln

- `defaults` enthält alle gemeinsamen Gerätedaten.
- Varianten überschreiben nur die jeweils abweichenden Felder.
- `variant_id` muss innerhalb einer Serie eindeutig sein.
- Die Geräte-ID wird automatisch als `<series_id>.<variant_id>` gebildet.
- Herstellerdaten dürfen weiterhin nur mit dokumentierter Quelle als `verified` gekennzeichnet werden.

Die mitgelieferte Serie ist ausdrücklich eine herstellerneutrale Vorlage und keine Produktempfehlung.
