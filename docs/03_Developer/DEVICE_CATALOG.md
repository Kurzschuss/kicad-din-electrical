# Gerätekatalog

Der Gerätekatalog beschreibt ein Gerät als fachliche Einheit. Symbol, optionaler Footprint, technische Merkmale und später Herstellerdaten werden dadurch miteinander verknüpft.

## Speicherort

```text
data/devices/
```

Herstellerneutrale Vorlagen liegen unter:

```text
data/devices/generic/
```

Herstellerdaten werden erst aufgenommen, wenn die Angaben anhand einer belastbaren Quelle geprüft wurden.

## Dateiformat

Gerätedateien tragen die Endung `.yaml`, verwenden in Phase 1 jedoch bewusst JSON-kompatible YAML-Syntax. Dadurch können sie ohne zusätzliche Python-Pakete gelesen und validiert werden.

Beispiel:

```yaml
{
  "id": "generic.mcb-1p-b16-template",
  "manufacturer": "Generic",
  "series": "Template",
  "part_number": "MCB-1P-B16",
  "device_type": "Leitungsschutzschalter",
  "function_group": "Schutzgeräte/Leitungsschutzschalter",
  "symbol": "Z_MCB:MCB",
  "footprint_policy": "optional",
  "source_status": "template"
}
```

## Footprint-Richtlinie

Die Regeln entsprechen den Symbolbibliotheken:

- `required`: Ein existierender Footprint muss angegeben sein.
- `optional`: Der Footprint darf fehlen.
- `none`: Für dieses Gerät ist ausdrücklich kein Footprint vorgesehen.

## Quellenstatus

- `template`: herstellerneutrale Vorlage oder Strukturbeispiel
- `verified`: technische Angaben wurden anhand einer dokumentierten Quelle geprüft
- `unverified`: Angaben sind noch nicht abschließend geprüft

Hersteller- und Produktdaten sollen grundsätzlich nicht stillschweigend als `verified` eingetragen werden.

## Validierung

```text
python tools/validate_device_catalog.py
```

Geprüft werden unter anderem:

- Pflichtfelder und zulässige Feldnamen
- eindeutige Geräte-IDs
- qualifizierte Symbol- und Footprint-IDs
- Existenz referenzierter Symbole und Footprints
- Widersprüche zur Footprint-Richtlinie
- positive Zahlenwerte für Pole, Nennstrom, Ausschaltvermögen und Modulbreite

Das formale Schema befindet sich unter `data/devices/schema/device.schema.json`.
