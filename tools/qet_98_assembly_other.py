#!/usr/bin/env python3
from __future__ import annotations

from qet_98_assembly_common import filename_stem, source_name, subgroup


def _bticino(item: dict) -> str:
    category = subgroup(item, "bticino")
    stem = filename_stem(item)
    source = source_name(item)

    if category == "myhome/actionneur":
        if "f4111n-" in stem:
            return "BTicino MyHOME F411/1N – 1-fach-Relaisaktor"
        if "f4111nc" in stem:
            return "BTicino MyHOME F411/1NC – 1-fach-Relaisaktor"
        if "f411u1" in stem:
            return "BTicino MyHOME F411U1 – 1-fach-Schaltaktor"

    if category == "myhome/alimentation":
        if "e46adcn" in stem:
            return "BTicino MyHOME E46ADCN – Bus-Netzteil 230 VAC / 27 VDC, 1,2 A, 8 Module"
        if "e47adcn" in stem:
            return "BTicino MyHOME E47ADCN – Bus-Netzteil"
        if "e49-" in stem:
            return "BTicino MyHOME_Up E49 – Bus-Netzteil 230 VAC / 27 VDC, 0,6 A, 2 Module"

    if category == "myhome/configuration":
        english = (item.get("names") or {}).get("en") or source
        left, _, right = english.partition(" - ")
        if right:
            right = right.replace("Configurator", "").replace("Configurateur", "").strip()
            return f"BTicino MyHOME {left.strip()} – Konfigurator {right}".strip()
        return "BTicino MyHOME – Konfigurator"

    fixed = {
        "myhome/memoire": "BTicino MyHOME F425 – Speichermodul",
        "myhome/passerelle": "BTicino MyHOME F422 – SCS/SCS-Gateway",
        "myhome/serveur": "BTicino MyHOME F454 – A/V-Webserver",
        "myhome/variateur": "BTicino MyHOME F418U2 – Dimmaktor",
    }
    if category in fixed:
        return fixed[category]
    raise ValueError(("unhandled BTicino assembly graphic", item["path"]))


def _icp_das(item: dict) -> str:
    source = (item.get("names") or {}).get("en") or source_name(item)
    code, _, description = source.partition(" - ")
    replacements = [
        ("4CH Isolated RS-485 Hub", "isolierter 4-Kanal-RS-485-Hub"),
        ("Isolated RS-232 to RS-422/485 Converter", "isolierter RS-232/RS-422/485-Wandler"),
        ("Isolated RS-232 to RS-485 Converter", "isolierter RS-232/RS-485-Wandler"),
        ("Isolated RS-232 to 4CH RS-485", "isolierter RS-232-auf-4×RS-485-Wandler"),
        ("RS-232 to RS-232 Converter", "RS-232/RS-232-Wandler"),
        ("USB to RS-232/422/485 Converter", "USB/RS-232/422/485-Wandler"),
        ("USB to 3 Ports RS-485 Hub Converter", "USB-auf-3-Port-RS-485-Hub"),
        ("USB to 3 Channels 485 Converter", "USB-auf-3-Kanal-RS-485-Wandler"),
        ("RS-485/422 Repeater", "RS-485/422-Repeater"),
        ("RS-422/485 Repeater", "RS-422/485-Repeater"),
        ("RS-485 Repeater", "RS-485-Repeater"),
        ("RS-485 Hub", "RS-485-Hub"),
    ]
    for needle, replacement in replacements:
        description = description.replace(needle, replacement)
    if not description and code.strip() == "ET-7042":
        description = "Ethernet-E/A-Modul"
    return f"ICP DAS {code.strip()}" + (f" – {description.strip()}" if description.strip() else "")


def _small_vendor(item: dict, vendor: str) -> str:
    stem = filename_stem(item)

    if vendor == "99_divers":
        names = {
            "borne-neutre": "Neutralleiterklemme",
            "borne-phase": "Phasenklemme",
            "borne_2.5": "Reihenklemme 2,5 mm²",
            "borne_de_terre": "Schutzleiterklemme",
            "borne_grise1": "Reihenklemme – grau",
            "borne_vj": "Schutzleiterklemme – grün/gelb",
            "bornegrise6": "Reihenklemme 6 mm² – grau",
            "c2a": "Legrand Leitungsschutzschalter 2 A",
            "cloison_terminale": "Endtrennplatte",
            "digital_ammeter": "Digitalamperemeter",
            "gps1b-aux": "GPS1B – Motorschutzschalter, Hilfsteil",
            "gps1b": "GPS1B – Motorschutzschalter",
            "inter_dif": "Legrand FI-Schutzschalter 40 A / 30 mA",
            "prise_modulaire": "Legrand modulare Steckdose",
            "terre_petite": "kleine Schutzleiterklemme",
            "transfo": "Legrand Transformator",
            "vis": "Kreuzschlitzschraube",
            "voltmeter": "Digitalvoltmeter",
        }
        return names[stem]

    if vendor == "omron":
        if stem.startswith("embase-p2rf-"):
            return "Omron " + stem.replace("embase-", "").replace("-", " ").upper() + " – Relaissockel"
        if stem == "embase_pf":
            return "Omron PF – Relaissockel"
        if stem == "embase_pyf_2":
            return "Omron PYF 2 – Relaissockel"
        if stem in ("g2rs", "mks", "my"):
            return f"Omron {stem.upper()} – Relais"
        if stem == "Omron_Log._output_input":
            return "Omron – Logik-Ein-/Ausgang"

    if vendor == "sofrel":
        return {
            "16di": "Sofrel 16DI – 16 Digitaleingänge",
            "parafoudre_sofrel": "Sofrel – Überspannungsschutz",
            "S510": "Sofrel S510 – Frontansicht Telemetriestation",
            "S550": "Sofrel S550 – Frontansicht Telemetriestation",
            "sg1000": "Sofrel SG1000 – Frontansicht Gateway",
            "sofrel_6ai-t": "Sofrel 6AI-T° – 6 analoge Temperatureingänge",
            "sofrel_6do": "Sofrel 6DO – 6 Digitalausgänge",
        }[stem]

    if vendor == "abb":
        return {
            "ABB_JRA2_230_5_1": "ABB JRA/S8.230.5.1 – Jalousieaktor",
            "ABB_JRA8_230_5_1": "ABB JRA/S2.230.5.1 – Jalousieaktor",
            "ABB_SA_S_12": "ABB – 12-fach-Schaltaktor",
            "ABB_SA_S_4": "ABB SA/S 4 – 4-fach-Schaltaktor",
        }[stem]

    if vendor == "delta_dore":
        return {
            "ddo_gp50": "Delta Dore GP50",
            "ddo_t1d_digit": "Delta Dore T1D Digit – Digitalthermostat",
            "ddo_tywatt": "Delta Dore Tywatt – Energiezähler",
        }[stem]

    if vendor == "finder":
        return {
            "finder60": "Finder Serie 60 – Industrierelais",
            "finder80_51": "Finder 80.51 – Zeitrelais",
            "rele_2p": "Finder – 2-poliges Steckrelais",
        }[stem]

    if vendor == "jumo":
        return {
            "ctron08big": "JUMO cTRON 08 – große Darstellung",
            "ctron08small": "JUMO cTRON 08 – kleine Darstellung",
            "etron": "JUMO eTRON T – Regler",
        }[stem]

    if vendor == "siemens":
        if "262" in stem:
            return "Siemens 5WG1 262-1EB22 – Binäreingangsgerät, potenzialfreie Kontakte"
        if "523" in stem:
            return "Siemens 5WG1 523-1AB11 – Jalousieaktor 230 V / 6 A"
        if "567" in stem:
            return "Siemens 5WG1 567-1AB22 – Schaltaktor 230 V / 10 A"

    if vendor == "tronic":
        return {
            "tlumivka2mh": "Tronic 9803861 – Drossel 2 mH",
            "trafo81": "Tronic 0703237 – Transformator",
            "trafo_0404611": "Tronic 0404611 – Transformator",
        }[stem]

    singleton = {
        "cognex": "Cognex D900 – Frontansicht",
        "hiquel": "HiQUEL TM16+ – Multifunktions-Zeitrelais",
        "schaffner": "Schaffner – Netzfilter",
        "sick": "SICK UE45-3S1 – Sicherheitsmodul",
        "somesca": "SOMESCA – Geräteansicht",
        "tpl-vision": "TPL Vision M-EBAR 125 – Frontansicht",
    }
    if vendor in singleton:
        return singleton[vendor]

    raise ValueError(("unhandled assembly graphic vendor/path", vendor, item["path"]))


def german_name(item: dict, vendor: str) -> str:
    if vendor == "bticino":
        return _bticino(item)
    if vendor == "icp-das":
        return _icp_das(item)
    return _small_vendor(item, vendor)
