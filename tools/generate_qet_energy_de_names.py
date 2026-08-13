#!/usr/bin/env python3
"""Generate reviewed German visible-name overrides for QET 60_energy.

The source audit supplies multilingual names.  This resolver applies a pinned,
reviewed terminology table plus deterministic domain rules; it never calls an
online translation service and never invents names from the filename alone.
"""
from __future__ import annotations

import argparse
import base64
import gzip
import json
import re
from pathlib import Path
from typing import Sequence

SOURCE_COMMIT = "42692ea76d2fcc3c6cf1ca335951584cd0978922"
SCOPES = {
    "11_water": 772,
    "21_refrigeration": 307,
    "31_solar_thermal": 128,
    "41_manufacturers_articles": 19,
}
LANG_PRIORITY = ("en", "fr", "es", "ca")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_rules(rule_dir: Path) -> dict:
    path_payload = load_json(rule_dir / "path_overrides.json")
    blob_payload = load_json(rule_dir / "generic_rules.json")
    for name, payload in (("path_overrides.json", path_payload), ("generic_rules.json", blob_payload)):
        if payload.get("schema_version") != 1:
            raise ValueError(f"Unsupported schema in {rule_dir / name}")
        if payload.get("source_commit") != SOURCE_COMMIT:
            raise ValueError(f"Wrong QET source commit in {rule_dir / name}")
    if blob_payload.get("encoding") != "gzip+base64":
        raise ValueError("Unsupported Energy terminology encoding")
    generic = json.loads(gzip.decompress(base64.b64decode(blob_payload["data"])).decode("utf-8"))
    if generic.get("source_commit") != SOURCE_COMMIT:
        raise ValueError("Wrong QET source commit inside Energy terminology data")
    return {
        "path": path_payload["path_overrides"],
        "en_exact": generic["en_exact"],
        "en_phrases": generic["en_phrases"],
        "es_exact": generic["es_exact"],
        "es_prefixes": generic["es_prefixes"],
        "fr_exact": generic["fr_exact"],
        "fr_prefixes": generic["fr_prefixes"],
    }


def clean(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip()).replace("º", "°")


def german_post(s: str) -> str:
    s = clean(s)
    s = re.sub(r"\bECS\b", "Trinkwarmwasser", s)
    s = re.sub(r"\bACS\b", "Trinkwarmwasser", s)
    s = re.sub(r"\bDHW\b", "Trinkwarmwasser", s)
    s = re.sub(r"\bn°\s*", "Nr. ", s, flags=re.I)
    for pattern, replacement in (
        (r"(?<![A-Za-z])HH(?![A-Za-z])", "IG-IG"),
        (r"(?<![A-Za-z])MM(?![A-Za-z])", "AG-AG"),
        (r"(?<![A-Za-z])MH(?![A-Za-z])", "AG-IG"),
        (r"(?<![A-Za-z])HM(?![A-Za-z])", "IG-AG"),
    ):
        s = re.sub(pattern, replacement, s)
    s = re.sub(r'(?<=[0-9/"\'])H\b', " IG", s)
    s = re.sub(r'(?<=[0-9/"\'])M\b', " AG", s)
    s = re.sub(r"\b(Muffe|Winkelmuffe|Absperrventil|T-Stück|Verschraubung)(?=\d)", r"\1 ", s)
    s = re.sub(r"(?<=\d)kg\b", " kg", s, flags=re.I)
    s = re.sub(r"(?<=\d)L\b", " l", s)
    s = re.sub(r"\bNF\b", "stromlos geschlossen", s)
    s = re.sub(r"\bNO\b", "stromlos offen", s)
    s = re.sub(r"\s+", " ", s).strip()
    s = s.replace("Sicherheits Gruppe", "Sicherheitsgruppe")
    s = s.replace("Reversibel Umwälzpumpe", "Reversible Umwälzpumpe")
    return s


def translate_en(text: str, rules: dict) -> str | None:
    t = clean(text)
    if t in rules["en_exact"]:
        return rules["en_exact"][t]
    for source, target in sorted(rules["en_phrases"], key=lambda x: len(x[0]), reverse=True):
        if t.casefold() == source.casefold():
            return target
    if re.fullmatch(r"[A-Za-z0-9./+\- ]{3,}", t) and any(
        marker in t for marker in ("VPM", "allSTOR", "VPS", "auroFLOW", "tafusion", "tamodulator", "Thermovar")
    ):
        return t
    wordmap = {
        "horizontal":"horizontal","vertical":"vertikal","right":"rechts","left":"links","open":"offen",
        "electric":"elektrisch","solar":"Solar","water":"Wasser","cold":"Kaltwasser","warm":"Warmwasser",
        "heating":"Heizung","heater":"Heizgerät","boiler":"Kessel","tank":"Behälter","bottle":"Flasche",
        "valve":"Ventil","pump":"Pumpe","filter":"Filter","sensor":"Sensor","switch":"Schalter",
        "controller":"Regler","thermical":"thermisch","thermostatic":"thermostatisch",
        "pressure":"Druck","differential":"Differenz","safety":"Sicherheits","security":"Sicherheits",
        "group":"Gruppe","faucet":"Armatur","elbow":"Bogen","tee":"T-Stück","set":"Satz",
        "plate":"Platte","plates":"Platten","exchanger":"Wärmetauscher","fan":"Ventilator",
        "compressor":"Verdichter","air":"Luft","floor":"Boden","wall":"Wand","radiator":"Heizkörper",
        "supply":"Versorgung","return":"Rücklauf","meter":"Zähler","probe":"Fühler","level":"Füllstand",
        "diesel":"Diesel","expansion":"Ausdehnung","vase":"Gefäß","deposit":"Behälter",
        "ball":"Kugel","flanges":"Flansche","motorized":"motorisiert","combined":"kombiniert",
        "arrow":"Pfeil","irrigation":"Bewässerung","garden":"Garten","house":"Haus","domestic":"Haus",
        "pool":"Schwimmbad","thermometer":"Thermometer","resistance":"Heizstab","retention":"Rückschlag",
        "storage":"Speicher","flexible":"flexibel","piping":"Rohrleitung","general":"allgemein",
        "submerged":"Tauch","axial":"Axial","centrifugal":"Radial","rotary":"Rotations",
        "piston":"Kolben","screw":"Schrauben","vane":"Drehschieber","turbo":"Turbo",
        "capillary":"Kapillar","tubing":"Rohr","cartridge":"Patronen","screens":"Sieb",
        "calorie":"Wärmemenge","counter":"Zähler","consume":"Entnahme","filled":"gefüllt","emptied":"entleert",
        "clock":"Uhr","scheduler":"Zeitschalt","trap":"Siphon","toilet":"WC",
        "large":"groß","litle":"klein","little":"klein","average":"mittel","square":"rechteckig",
        "underground":"unterirdisch","terrace":"Dach","planar":"Flach","inclined":"geneigt",
        "capturator":"Kollektor","thermosyphon":"Thermosiphon","profile":"Profil",
        "reversible":"reversibel","circulator":"Umwälzpumpe","circulating":"Umwälz",
        "mixer":"Mischer","mix":"Kombi","room":"Raum","damp":"Feuchte","environment":"Umgebung",
        "exterior":"Außen","insertion":"Einsteck","bulb":"Kapillar","instant":"Durchlauf",
        "connection":"Anschluss","connexion":"Anschluss","output":"Abgang","collector":"Verteiler",
    }
    parts = re.split(r"(\W+)", t)
    out, changed = [], False
    for part in parts:
        key = part.casefold()
        if key in wordmap:
            out.append(wordmap[key])
            changed = True
        else:
            out.append(part)
    result = re.sub(r"\s+", " ", "".join(out)).strip()
    if not changed:
        return None
    return result[0].upper() + result[1:] if result else result


def translate_es(text: str, rules: dict) -> str | None:
    t = clean(text)
    if t in rules["es_exact"]:
        return rules["es_exact"][t]
    result = t
    for source, target in sorted(rules["es_prefixes"], key=lambda x: len(x[0]), reverse=True):
        if result.casefold().startswith(source.casefold()):
            result = target + result[len(source):]
            break
    for source, target in (
        (" exterior"," außen"),(" Exterior"," außen"),(" doble"," doppelt"),
        (" horizontal"," horizontal"),(" Horiz."," horizontal"),(" vertical"," vertikal"),
        (" izquierda"," links"),(" derecha"," rechts"),("-izq"," links"),
        (" agua"," Wasser"),(" gas"," Gas"),(" seguridad"," Sicherheit"),
        (" presión"," Druck"),(" pres."," Druck"),(" pres"," Druck"),
        (" rosca"," Gewinde"),(" bridas"," Flansche"),(" brida"," Flansch"),
        (" H-H"," IG-IG"),(" M-M"," AG-AG"),(" H"," IG"),(" M"," AG"),
        (" aceite"," Öl"),(" líquido"," Flüssigkeit"),
        (" general"," allgemein"),(" manual"," handbetätigt"),
    ):
        result = re.sub(re.escape(source), target, result, flags=re.I)
    return None if result == t else result


def translate_fr(text: str, rules: dict) -> str | None:
    t = clean(text)
    if t in rules["fr_exact"]:
        return rules["fr_exact"][t]
    result = t
    for source, target in sorted(rules["fr_prefixes"], key=lambda x: len(x[0]), reverse=True):
        if result.casefold().startswith(source.casefold()):
            result = target + result[len(source):]
            break
    for source, target in (
        (" eau"," Wasser"),(" Gaz"," Gas"),(" gaz"," Gas"),(" GPL"," Flüssiggas"),
        (" Cu "," Kupfer "),(" Cu"," Kupfer"),(" cuivre"," Kupfer"),
        (" laiton"," Messing"),(" fer"," Stahl"),(" PVC pression"," PVC-Druck"),
        (" pression"," Druck"),(" isolé"," gedämmt"),(" isolée"," gedämmt"),
        (" femelle"," Innengewinde"),(" mâle"," Außengewinde"),
        (" droite"," rechts"),(" gauche"," links"),(" haut"," oben"),
        (" horizontal"," horizontal"),(" vertical"," vertikal"),
        (" extérieur"," außen"),(" extérieure"," außen"),
        (" à brides"," mit Flanschen"),(" à purge"," mit Entleerung"),
        (" filetée"," Außengewinde"),(" taraudée"," Innengewinde"),
        (" à sertir"," Press"),(" glissement"," Schiebe"),
        (" libre"," frei"),(" double"," doppelt"),
    ):
        result = re.sub(re.escape(source), target, result, flags=re.I)
    result = (
        result.replace(" F-F", " IG-IG").replace(" FF", " IG-IG")
        .replace(" MF", " AG-IG").replace(" DF", " IG-IG").replace(" DM", " IG-AG")
    )
    return None if result == t else result


def translate_ca(text: str) -> str | None:
    return "Ölstandregler" if clean(text) == "Reg. nivel aceite" else None


def resolve_item(item: dict, rules: dict) -> str:
    path = item["path"]
    if path in rules["path"]:
        return german_post(rules["path"][path])
    names = item.get("names") or {}
    for lang in LANG_PRIORITY:
        text = names.get(lang)
        if not text:
            continue
        if lang == "en":
            value = translate_en(text, rules)
        elif lang == "fr":
            value = translate_fr(text, rules)
        elif lang == "es":
            value = translate_es(text, rules)
        else:
            value = translate_ca(text)
        if value:
            return german_post(value)
    raise ValueError(f"No reviewed German resolver result for {path}: {names!r}")


def generate(audit_file: Path, rule_dir: Path, output_dir: Path, report_file: Path | None = None) -> dict:
    audit = load_json(audit_file)
    rules = load_rules(rule_dir)
    if audit.get("missing_german_names") != 1226:
        raise ValueError(f"Expected 1226 missing German names, got {audit.get('missing_german_names')}")
    items = audit.get("items") or []
    missing_paths = [item["path"] for item in items]
    if len(items) != 1226 or len(set(missing_paths)) != 1226:
        raise ValueError("Energy audit items are not the expected unique 1226 paths")

    resolved = {item["path"]: resolve_item(item, rules) for item in items}
    if set(resolved) != set(missing_paths):
        raise AssertionError("Resolved path set differs from audit path set")
    if any(not value.strip() for value in resolved.values()):
        raise AssertionError("Empty German visible name generated")
    if any(value.startswith("Energie-Symbol ") for value in resolved.values()):
        raise AssertionError("Generic Energy fallback leaked into reviewed names")

    output_dir.mkdir(parents=True, exist_ok=True)
    counts = {}
    for scope, expected_count in SCOPES.items():
        prefix = f"60_energy/{scope}/"
        overrides = {path: resolved[path] for path in sorted(resolved) if path.startswith(prefix)}
        if len(overrides) != expected_count:
            raise ValueError(f"{scope}: expected {expected_count} overrides, got {len(overrides)}")
        payload = {
            "schema_version": 1,
            "source_commit": SOURCE_COMMIT,
            "scope": f"60_energy/{scope}",
            "overrides": overrides,
        }
        (output_dir / f"{scope}.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        counts[scope] = len(overrides)

    report = {
        "qet_source_commit": SOURCE_COMMIT,
        "audited_missing_german_names": 1226,
        "configured_german_names": len(resolved),
        "remaining_translation_count": 0,
        "scopes": counts,
    }
    if report_file:
        report_file.parent.mkdir(parents=True, exist_ok=True)
        report_file.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--rule-dir", type=Path, default=Path("config/qet_de_names/60_energy/rules"))
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args(argv)
    report = generate(args.audit, args.rule_dir, args.output_dir, args.report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
