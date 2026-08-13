#!/usr/bin/env python3
from __future__ import annotations

import re

from qet_98_assembly_common import article_code, filename_stem, source_name, subgroup, suffix_after_dash


def _translate_connections(text: str) -> str:
    replacements = [
        ("Haut-Auto/Bas-Vis", "oben Steckklemme / unten Schraubklemme"),
        ("Haut-Vis/Bas-Vis", "oben Schraubklemme / unten Schraubklemme"),
        ("Haut-Vis/Haut-Vis", "oben Schraubklemme / oben Schraubklemme"),
        ("Haut-Vis/Haut-Auto", "oben Schraubklemme / oben Steckklemme"),
        ("Auto/Auto", "Steckklemme/Steckklemme"),
        ("Auto/Vis", "Steckklemme/Schraubklemme"),
        ("Vis/Vis", "Schraubklemme/Schraubklemme"),
        ("Vis/Auto", "Schraubklemme/Steckklemme"),
    ]
    for source, target in replacements:
        text = text.replace(source, target)
    return text


def german_name(item: dict) -> str:
    category = subgroup(item, "legrand")
    source = source_name(item)
    stem = filename_stem(item)
    code = article_code(item)
    prefix = f"Legrand {code} – " if code else "Legrand – "
    rest = suffix_after_dash(source).strip()

    if category == "01-coupe_circuit":
        pole = "1-poliger" if "unipolaire" in source else "2-poliger"
        return prefix + f"{pole} Sicherungslasttrennschalter"

    if category == "02-disjoncteur":
        rest = re.sub(r"^Disjoncteur\s*", "", rest)
        return prefix + "Leitungsschutzschalter " + _translate_connections(rest)

    if category == "03-disjoncteur_diff":
        rest = re.sub(r"^Disjoncteur différentiel\s*", "", rest)
        return prefix + "FI/LS-Schalter " + _translate_connections(rest)

    if category == "04-inter_diff":
        rest = re.sub(r"^Interrupteur différentiel\s*", "", rest)
        rest = _translate_connections(rest).replace("3 modules", "3 Module")
        return prefix + "FI-Schutzschalter " + rest

    if category == "05-inter_sec":
        rest = re.sub(r"^Interrupteur-sectionneur\s*", "", rest)
        rest = (
            rest.replace("à voyant", "mit Meldeleuchte")
            .replace("à déclenchement", "mit Auslösung")
            .replace("(ancien modèle)", "(altes Modell)")
        )
        return prefix + "Lasttrennschalter " + rest

    if category == "10-parafoudre":
        if "cassette" in rest.casefold():
            return prefix + "Überspannungsschutz-Ersatzkassette"
        rest = (
            rest.replace("Parafoudre", "Überspannungsschutz")
            .replace("Type", "Typ")
            .replace("Abonné + Cassette", "Teilnehmeranlage + Kassette")
        )
        return prefix + rest

    if category == "20-prise/2pt":
        return prefix + "modulare Schutzkontakt-Steckdose 10 A"
    if category == "20-prise/rj45":
        return prefix + "modulare RJ45-Steckdose"

    if category == "25-multimedia":
        replacements = [
            ("Prise RJ45 6A STP modulaire", "modulare RJ45-Steckdose Cat. 6A STP"),
            ("DTI modulaire RJ45", "modulares DTI-RJ45-Modul"),
            ("Filtre maître pour accès téléphone et internet 3 sorties + modem", "Hauptfilter Telefon/Internet, 3 Ausgänge + Modem"),
            ("Filtre maître pour accès téléphone et internet", "Hauptfilter Telefon/Internet"),
            ("Alimentation modulaire 9V= 1,6A", "modulares Netzteil 9 VDC / 1,6 A"),
            ("Centrale automatique Gigabit TNT Satellite", "automatische Gigabit-TV/Sat-Zentrale"),
            ("Centrale automatique Gigabit TNT Câble", "automatische Gigabit-TV/Kabel-Zentrale"),
            ("Cordon box déportée", "Verbindungskabel für abgesetzte Box"),
            ("Parafoudre téléphonique et communication", "Überspannungsschutz für Telefon-/Kommunikationsleitungen"),
        ]
        for needle, replacement in replacements:
            if needle in rest:
                return prefix + replacement
        raise ValueError(("unhandled Legrand multimedia name", item["path"], source))

    if category == "30-energy":
        if "Eco compteur" in source:
            return prefix + "Energieverbrauchszähler"
        if "courant ouvert" in source:
            return prefix + "offener Stromwandler 90 A"
        if "courant fermé" in source:
            return prefix + "geschlossener Stromwandler 60 A"

    if category == "40-portier/sonnerie":
        rest = (
            rest.replace("Transformateur sonnerie", "Klingeltransformator")
            .replace("Bell transformer", "Klingeltransformator")
            .replace("modules", "Module")
        )
        return prefix + rest

    if category.startswith("50-telerupteur"):
        rest = re.sub(r"^Télérupteur\s*", "", rest)
        rest = rest.replace("silencieux", "geräuscharm").replace("temporisé", "zeitverzögert")
        return prefix + "Stromstoßschalter " + rest

    if category.startswith("51-contacteur"):
        rest = re.sub(r"^Contacteur\s*", "", rest).replace("silencieux", "geräuscharm")
        return prefix + "Installationsschütz " + rest

    if category.startswith("60-tableau/atlantic"):
        match = re.search(r"-(\d+x\d+x\d+)-metal", stem)
        if not match:
            match = re.search(r"(\d+x\d+x\d+)", source)
        if not match:
            raise ValueError(("Legrand Atlantic dimensions missing", item["path"]))
        return prefix + f"Atlantic Schaltschrank {match.group(1)} mm, Metall, IP66 IK10 RAL7035"

    if category == "60-tableau/bornier":
        if "neutre" in stem:
            kind = "Neutralleiterklemme"
        elif "terre" in stem:
            kind = "Schutzleiterklemme"
        else:
            kind = "Phasenklemme"
        detail = rest.split("Bornier", 1)[-1].strip()
        detail = re.sub(r"^(neutre|phase|terre)\s*", "", detail, flags=re.I)
        return prefix + kind + (f" {detail}" if detail else "")

    if category == "60-tableau/coffret":
        if "cache-bornes" in source:
            match = re.search(r"(\d+)\s+module", source)
            return prefix + (f"Klemmenabdeckung-Gehäuse, {match.group(1)} Module" if match else "Klemmenabdeckung-Gehäuse")
        match = re.search(r"(\d+)\s+modules", source)
        if "capacité mini" in source:
            return prefix + "Gehäuse, Kapazität 8–9 Module"
        return prefix + (f"Gehäuse, {match.group(1)} Module" if match else "Gehäuse")

    if category.startswith("60-tableau/drivia_"):
        row = re.search(r"(\d+)\s+rang", source)
        if "Bornier" in source:
            values = re.search(r"(\d+\s*\+\s*\d+)", source)
            return prefix + "Drivia Schutzleiter-Klemmleiste" + (f" {values.group(1)}" if values else "")
        series = "Drivia 18" if "drivia_18" in category else "Drivia 13"
        return prefix + series + (f" – {row.group(1)} Reihen" if row else "")

    if category == "60-tableau/equipment/01-full-plate":
        dims = re.search(r"(\d+x\d+)", stem)
        series = "Marina" if "marina" in stem.casefold() or "Marina" in source else "Atlantic/Marina"
        return prefix + f"Montageplatte voll {dims.group(1) if dims else ''} mm – {series}"

    if category == "60-tableau/equipment/03-accessoires":
        if "goulotte" in stem:
            match = re.search(r"Lina25\s+([0-9x]+)mm", source)
            return prefix + (f"Lina25 Verdrahtungskanal {match.group(1)} mm, Länge 2 m" if match else "Lina25 Verdrahtungskanal")
        if "036401" in stem:
            return "Legrand 036401 – Wandbefestigungslaschen"
        if "036440" in stem:
            return "Legrand 036440 – Käfigmuttern-Clip M4"

    if category.startswith("60-tableau/marina"):
        match = re.search(r"-(\d+x\d+x\d+)-polyester", stem)
        return prefix + f"Marina Schaltschrank {match.group(1) if match else ''} mm, Polyester, IP66 IK10 RAL7035"

    if category == "61-busbar/horizontal/live":
        modules = re.search(r"_(\d+)m-live$", stem)
        return prefix + f"HX³ Phasenschiene P+N – {int(modules.group(1))} Module"
    if category == "61-busbar/horizontal/neutral":
        modules = re.search(r"_(\d+)m-neutral$", stem)
        return prefix + f"HX³ Neutralleiterschiene P+N – {int(modules.group(1))} Module"
    if category == "61-busbar/vertical":
        rows = re.search(r"(\d+)\s+rang", source)
        return prefix + (f"VX³ vertikale Sammelschiene P+N – {rows.group(1)} Reihen" if rows else "VX³ vertikale Sammelschiene P+N")

    if category.startswith("65-viking3"):
        text = re.sub(r"^Viking3\s*-\s*", "", rest, flags=re.I)
        replacements = [
            ("1 jonction 2 entrées 2 sorties", "1 Verbindung, 2 Eingänge / 2 Ausgänge"),
            ("1 jonction 1 entrée 1 sortie", "1 Verbindung, 1 Eingang / 1 Ausgang"),
            ("3 jonctions 3 étages", "3 Verbindungen / 3 Etagen"),
            ("2 jonctions 2 étages", "2 Verbindungen / 2 Etagen"),
            ("1 jonction ouverte", "1 offene Trennklemme"),
            ("1 jonction", "1 Verbindung"),
            ("2 entrées 2 sorties", "2 Eingänge / 2 Ausgänge"),
            ("Fusible", "Sicherung"), ("fusible", "Sicherung"),
            ("Circuit neutre", "Neutralleiterkreis"),
            ("Circuit standard", "Standardkreis"),
            ("Circuit non coupé", "nicht getrennter Kreis"),
            ("Mini-préhenseur", "Mini-Steckbrücke"),
            ("Mini préhenseur", "Mini-Steckbrücke"),
            ("Préhenseur", "Steckbrücke"), ("préhenseur", "Steckbrücke"),
            ("Bouchon", "Kappe"), ("Témoin", "Anzeige"),
            ("à équiper", "zum Bestücken"),
            ("de meusre sectionnable", "Messkreis trennbar"),
            ("sectionnable", "trennbar"),
            ("Butée de blocage pour bloc de jonction Viking3 avec pas", "Endhalter für Viking3-Reihenklemme, Teilung"),
            ("Butée de blocage pour bloc de jonction Viking3", "Endhalter für Viking3-Reihenklemme"),
            ("Porte-étiquette transparent à inclinaison variable", "transparenter, neigbarer Beschriftungsträger"),
            ("Cloison terminale bloc jonction Viking3 à vis", "Endtrennplatte für Viking3-Schraubklemme"),
            ("Cloison terminale pour blocs de jonction à vis Viking3 avec", "Endtrennplatte für Viking3-Schraubklemme mit"),
            ("Cloison terminale", "Endtrennplatte"),
            ("pas", "Teilung"),
            ("Bleu", "blau"), ("Orange", "orange"), ("Rouge", "rot"),
            ("Gris foncé", "dunkelgrau"), ("Gris", "grau"),
            ("Vert/jaune", "grün/gelb"), ("Nu", "blank"), ("Vert", "grün"),
            ("entrée", "Eingang"), ("sortie", "Ausgang"),
            ("étages", "Etagen"), ("jonctions", "Verbindungen"),
        ]
        for needle, replacement in replacements:
            text = text.replace(needle, replacement)
        text = re.sub(r"(\d(?:,\d+)?)mm²", r"\1 mm²", text)
        text = re.sub(r"(\d+)mm\b", r"\1 mm", text)
        text = re.sub(r"\s+", " ", text).strip(" -")
        text = text.replace("Steckbrücke neutre blau", "Neutralleiter-Steckbrücke, blau")
        text = text.replace("Teilung 12 et 15", "Teilung 12 und 15 mm")
        if re.search(r"(?:-|_)vert(?:-|_|$)", stem.casefold()):
            text = re.sub(r"\bgrau\b", "grün", text)
        return prefix + "Viking3 – " + text

    if category == "80-netatmo":
        if "ecocompteur" in stem:
            return prefix + "Netatmo Energieverbrauchszähler"
        if "telerupteur" in stem:
            return prefix + "Netatmo Stromstoßschalter 1P 16AX 230 V, geräuscharm"
        if "contacteur" in stem:
            return prefix + "Netatmo Installationsschütz 1P 20AX 230 V, geräuscharm"
        if "module-controle" in stem:
            return prefix + "Netatmo Steuermodul"
        if "412008" in stem:
            return prefix + "geschlossener Stromwandler 60 A"

    if not category and "sectionneur" in stem.casefold():
        return "Legrand – Lasttrennschalter, 2-polig, 63 A"

    raise ValueError(("unhandled Legrand assembly graphic", category, stem, source))
