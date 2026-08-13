#!/usr/bin/env python3
from __future__ import annotations

import re

from qet_98_assembly_common import filename_stem, source_name, subgroup


def german_name(item: dict) -> str:
    category = subgroup(item, "schneider_electric")
    stem = filename_stem(item)
    source = source_name(item)

    if category == "disjoncteurs":
        lower_stem = stem.casefold()
        if "domb" in lower_stem:
            return "Schneider Electric " + source.replace(" ma", " mA") + " – FI-Schutzschalter"
        if "vigi" in lower_stem:
            return "Schneider Electric Vigi DT40 – FI-Zusatzmodul"
        if "30ma" in lower_stem and "schneider_man" in lower_stem:
            return "Schneider Electric – Geräteansicht 30 mA"
        description = source.replace("Disjoncteur", "").strip()
        return f"Schneider Electric {description} – Leitungsschutzschalter"

    if category == "idt40":
        amps = re.search(r"(\d+)\s*A", source, re.I)
        return (
            f"Schneider Electric iDT40 – Leitungsschutzschalter {amps.group(1)} A"
            if amps
            else "Schneider Electric iDT40 – Leitungsschutzschalter"
        )

    if category == "gv2":
        return f"Schneider Electric {source.strip()} – Motorschutzschalter" + (
            " (Variante 2)" if stem.endswith("_2") else ""
        )

    if category == "porte_etiquettes":
        labels = {
            "zby2126": "„UNTER SPANNUNG“",
            "zby2130": "„NOT-HALT“",
            "zby2134": "„STÖRUNG“ – schwarz",
            "zby2135": "„STÖRUNG“ – rot",
            "zby2185": "„AUTO–0–HAND“",
            "zby2186": "„I–0–II“",
        }
        key = stem.casefold()
        return f"Schneider Electric {key.upper()} – Beschriftungsschild {labels[key]}"

    if category == "relays_contactors_contacts":
        model = source.strip()
        if stem == "ka":
            return "Schneider Electric CAD32 – Hilfsschütz"
        if stem.startswith("km_"):
            return f"Schneider Electric {model} – Leistungsschütz"
        if stem.startswith("ladn22"):
            return f"Schneider Electric {model} – Hilfskontaktblock"
        if stem.startswith("ladr4"):
            return "Schneider Electric LADR4 – rückfallverzögerter Hilfskontaktblock"
        if stem.startswith("lads2"):
            return "Schneider Electric LADS2 – ansprechverzögerter Hilfskontaktblock"
        if stem in ("lc1d", "lc1k"):
            return f"Schneider Electric {model} – Leistungsschütz"
        if stem in ("lc2d", "lc2k"):
            return f"Schneider Electric {model} – Wendeschütz"
        if stem == "lrd":
            return "Schneider Electric LRD – Motorschutz-/Überlastrelais"
        if stem.startswith("ict_"):
            return f"Schneider Electric {source.replace('Contacteur ITC', 'iCT')} – Installationsschütz"

    if category.startswith("voyants/"):
        colors = {"blanc": "weiß", "vert": "grün", "rouge": "rot", "orange": "orange", "bleu": "blau"}
        color = next((value for key, value in colors.items() if key in stem.casefold()), "")
        model_match = re.search(r"(XB4BV[BM]\d)", source, re.I)
        model = model_match.group(1).upper() if model_match else ""
        voltage = "230 V" if "230v" in category.casefold() else "24 V"
        return f"Schneider Electric {model} – Meldeleuchte {voltage}, {color}".strip(", ")

    root_names = {
        "alim-24vdc": "Schneider Electric – Netzteil 24 VDC",
        "demarreur-sch-ats01n222qn": "Schneider Electric Altistart ATS01N222QN – Sanftstarter",
        "is-neutre": "Schneider Electric – Neutralleiter-Trennschalter",
        "is-tri": "Schneider Electric – dreipoliger Sicherungslasttrennschalter",
        "lrd": "Schneider Electric LRD – Motorschutz-/Überlastrelais",
        "m221ce40t": "Schneider Electric Modicon M221CE40T – SPS",
        "porte-fusible-5x20": "Schneider Electric – Sicherungshalter 5×20 mm",
        "sch-cct15225-interrupteur-crepusculaire": "Schneider Electric CCT15225 – Dämmerungsschalter",
        "sch_23158": "Schneider Electric SCH_23158",
        "schneider_parafoudre": "Schneider Electric – Überspannungsschutz",
        "sectiopf_tri": "Schneider Electric – dreipoliger Sicherungslasttrennschalter",
        "sectiopf_tri_9596": "Schneider Electric – dreipoliger Sicherungslasttrennschalter 95/96",
    }
    if not category and stem.casefold() in root_names:
        return root_names[stem.casefold()]

    raise ValueError(("unhandled Schneider Electric assembly graphic", category, stem, source))
