# Z_-Gerätepakete: Fortschrittsübersicht

Diese Datei wird aus `data/Z_PACKAGE_PROGRESS.json` erzeugt. **KiCad ist der Standard; projektspezifische Erweiterungen tragen konsequent `Z_`.**

Eine Familie gilt erst als vollständiges Paket, wenn Symbol, Gerätedaten, Dokumentation, Beispiel und Tests zusammen vorhanden sind.

| Gerätefamilie | Symbol | Gerätedaten | Dokumentation | Beispiel | Tests | Qualitätsstatus | Reifegrad |
|---|:---:|:---:|:---:|:---:|:---:|---|---|
| MCB (`Z_MCB`) | ✅ | ✅ | ✅ | ⬜ | ✅ | `z_conform` | Geprüft |
| RCD (`Z_RCD`) | ✅ | ✅ | ✅ | ⬜ | ✅ | `z_conform` | Geprüft |
| RCBO (`Z_RCBO`) | ✅ | ✅ | ✅ | ⬜ | ✅ | `z_conform` | Geprüft |
| Hauptschalter (`Z_MAIN_SWITCH`) | ✅ | ✅ | ✅ | ⬜ | ✅ | `z_conform` | Geprüft |

## Reifegrade

- **Entwurf:** Paketbestandteile sind begonnen, aber noch nicht vollständig geprüft.
- **Geprüft:** Symbol, Gerätedaten, Dokumentation und Tests sind vorhanden; die aktivierten KiCad- und `Z_`-Regeln sind erfüllt oder eine dokumentierte zeitweilige Ausnahme ist freigegeben. Ein Praxisbeispiel kann noch fehlen.
- **Praxisgetestet:** Das geprüfte Paket wurde zusätzlich in einem dokumentierten Beispielprojekt praktisch geprüft.

## Aktualisierung

Geräte-PRs ändern ausschließlich die Datenquelle und erzeugen anschließend diese Datei neu. Manuelle Statuskosmetik ohne prüfbare Paketdaten ist nicht zulässig.
