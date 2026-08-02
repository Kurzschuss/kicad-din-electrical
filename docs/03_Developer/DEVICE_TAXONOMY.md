# Gerätefamilien und Funktionsgruppen

Der Gerätekatalog verwendet eine zentrale Taxonomie unter:

```text
data/taxonomy/device_families.json
```

Jede Gerätefamilie besitzt eine stabile technische ID sowie deutsche Anzeigenamen für Hauptgruppe und Familie.

Beispiel:

```json
{"id": "protection.mcb", "group": "Schutzgeräte", "name": "Leitungsschutzschalter"}
```

In Gerätedateien wird ausschließlich die stabile ID gespeichert:

```json
"function_group": "protection.mcb"
```

## Warum stabile IDs?

Freie Texte führen leicht zu mehreren Bezeichnungen für dieselbe Funktion, etwa `FI`, `RCD` oder `Fehlerstromschutz`. Die kontrollierte Taxonomie verhindert solche Dubletten und ermöglicht später zuverlässige Filter, Übersetzungen und Auswertungen.

## Aktuelle Hauptgruppen

- Schutzgeräte
- Schalten
- Steuern
- Melden
- Messen
- Verteilen
- Versorgen
- Dokumentation

## Neue Familie ergänzen

1. In `data/taxonomy/device_families.json` eine eindeutige ID ergänzen.
2. Einen deutschen Hauptgruppen- und Familiennamen angeben.
3. Betroffene Gerätedateien auf die neue ID umstellen.
4. `python tools/validate_device_catalog.py` ausführen.
5. Die vollständige Testsuite starten.

IDs werden klein geschrieben und nach dem Muster `hauptgruppe.familie` aufgebaut. Bestehende IDs dürfen nicht ohne Migration umbenannt werden, weil sie Teil der dauerhaft gespeicherten Gerätedaten sind.

## Validierung

Der Gerätekatalog-Validator prüft:

- gültige Syntax jeder Familien-ID,
- eindeutige IDs in der Taxonomie,
- bekannte Familien-ID in jeder Gerätedatei,
- weiterhin alle bisherigen Symbol-, Footprint- und Datenregeln.
