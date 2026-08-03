# Z_-Gerätepakete: Fortschrittsübersicht

Diese Datei wird aus `data/Z_PACKAGE_PROGRESS.json` erzeugt. **KiCad ist der Standard; projektspezifische Erweiterungen tragen konsequent `Z_`.**

Eine Familie gilt erst als vollständiges Paket, wenn Symbol, Gerätedaten, Dokumentation, Beispiel und Tests zusammen vorhanden sind.

| Gerätefamilie | Symbol | Gerätedaten | Dokumentation | Beispiel | Tests | Qualitätsstatus | Reifegrad |
|---|:---:|:---:|:---:|:---:|:---:|---|---|
| MCB (`Z_MCB`) | ✅ | ✅ | ✅ | ⬜ | ✅ | `z_conform` | Geprüft |
| RCD (`Z_RCD`) | ✅ | ✅ | ⬜ | ⬜ | ⬜ | `needs_rework` | Entwurf |
| RCBO (`Z_RCBO`) | ✅ | ✅ | ⬜ | ⬜ | ⬜ | `needs_rework` | Entwurf |
| Hauptschalter (`Z_MAIN_SWITCH`) | ✅ | ✅ | ⬜ | ⬜ | ⬜ | `needs_rework` | Entwurf |

## Reifegrade

- **Entwurf:** Paketbestandteile sind begonnen, aber noch nicht vollständig geprüft.
- **Geprüft:** Die vorhandenen Bestandteile erfüllen die aktivierten KiCad- und `Z_`-Regeln; ein Praxisbeispiel kann noch fehlen.
- **Praxisgetestet:** Das vollständige Paket wurde zusätzlich in einem dokumentierten Beispielprojekt praktisch geprüft.

## Aktualisierung

Geräte-PRs ändern ausschließlich die Datenquelle und erzeugen anschließend diese Datei neu. Manuelle Statuskosmetik ohne prüfbare Paketdaten ist nicht zulässig.
