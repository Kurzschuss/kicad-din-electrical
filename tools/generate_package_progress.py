"""Generate the central Z_ device-package progress overview."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

SOURCE = Path("data/Z_PACKAGE_PROGRESS.json")
OUTPUT = Path("docs/04_Reference/Z_PACKAGE_PROGRESS.md")
VALID_QUALITY_STATUSES = {
    "kicad_conform",
    "z_conform",
    "needs_rework",
    "temporarily_accepted",
}
VALID_LEVELS = {"Entwurf", "Geprüft", "Praxisgetestet"}


def _mark(value: bool) -> str:
    return "✅" if value else "⬜"


def load_progress(path: Path = SOURCE) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    families = payload.get("families")
    if not isinstance(families, list) or not families:
        raise ValueError("Z_PACKAGE_PROGRESS requires a non-empty families list")

    seen: set[str] = set()
    for family in families:
        family_id = str(family.get("id", ""))
        if not family_id.startswith("Z_"):
            raise ValueError(f"Package id must start with Z_: {family_id!r}")
        if family_id in seen:
            raise ValueError(f"Duplicate package id: {family_id}")
        seen.add(family_id)
        if family.get("quality_status") not in VALID_QUALITY_STATUSES:
            raise ValueError(f"Invalid quality status for {family_id}")
        if family.get("quality_level") not in VALID_LEVELS:
            raise ValueError(f"Invalid quality level for {family_id}")
        if family.get("quality_level") == "Praxisgetestet" and not all(
            family.get(field) for field in ("symbol", "device_data", "documentation", "example", "tests")
        ):
            raise ValueError(f"Praxisgetestet package is incomplete: {family_id}")
    return payload


def render(payload: dict[str, Any]) -> str:
    lines = [
        "# Z_-Gerätepakete: Fortschrittsübersicht",
        "",
        "Diese Datei wird aus `data/Z_PACKAGE_PROGRESS.json` erzeugt. **KiCad ist der Standard; projektspezifische Erweiterungen tragen konsequent `Z_`.**",
        "",
        "Eine Familie gilt erst als vollständiges Paket, wenn Symbol, Gerätedaten, Dokumentation, Beispiel und Tests zusammen vorhanden sind.",
        "",
        "| Gerätefamilie | Symbol | Gerätedaten | Dokumentation | Beispiel | Tests | Qualitätsstatus | Reifegrad |",
        "|---|:---:|:---:|:---:|:---:|:---:|---|---|",
    ]
    for family in payload["families"]:
        lines.append(
            "| {name} (`{id}`) | {symbol} | {device_data} | {documentation} | {example} | {tests} | `{quality_status}` | {quality_level} |".format(
                name=family["name"],
                id=family["id"],
                symbol=_mark(bool(family["symbol"])),
                device_data=_mark(bool(family["device_data"])),
                documentation=_mark(bool(family["documentation"])),
                example=_mark(bool(family["example"])),
                tests=_mark(bool(family["tests"])),
                quality_status=family["quality_status"],
                quality_level=family["quality_level"],
            )
        )
    lines.extend(
        [
            "",
            "## Reifegrade",
            "",
            "- **Entwurf:** Paketbestandteile sind begonnen, aber noch nicht vollständig geprüft.",
            "- **Geprüft:** Die vorhandenen Bestandteile erfüllen die aktivierten KiCad- und `Z_`-Regeln; ein Praxisbeispiel kann noch fehlen.",
            "- **Praxisgetestet:** Das vollständige Paket wurde zusätzlich in einem dokumentierten Beispielprojekt praktisch geprüft.",
            "",
            "## Aktualisierung",
            "",
            "Geräte-PRs ändern ausschließlich die Datenquelle und erzeugen anschließend diese Datei neu. Manuelle Statuskosmetik ohne prüfbare Paketdaten ist nicht zulässig.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = render(load_progress())
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != rendered:
            raise SystemExit(f"Generated progress overview is stale: {OUTPUT}")
        print("Die Z_-Paketfortschrittsübersicht ist aktuell.")
        return 0
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(rendered, encoding="utf-8")
    print(f"Erzeugt: {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
