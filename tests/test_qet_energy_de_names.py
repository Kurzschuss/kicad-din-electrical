from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "generate_qet_energy_de_names.py"
SPEC = importlib.util.spec_from_file_location("generate_qet_energy_de_names", MODULE_PATH)
assert SPEC and SPEC.loader
mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = mod
SPEC.loader.exec_module(mod)

RULE_DIR = ROOT / "config" / "qet_de_names" / "60_energy" / "rules"


def test_energy_rules_are_pinned_and_complete_by_scope():
    rules = mod.load_rules(RULE_DIR)
    assert mod.SOURCE_COMMIT == "42692ea76d2fcc3c6cf1ca335951584cd0978922"
    assert mod.SCOPES == {
        "11_water": 772,
        "21_refrigeration": 307,
        "31_solar_thermal": 128,
        "41_manufacturers_articles": 19,
    }
    assert sum(mod.SCOPES.values()) == 1226
    assert rules["en_exact"]
    assert rules["es_exact"]
    assert rules["fr_exact"]
    assert rules["path"]


def test_reviewed_energy_path_corrections_are_preserved():
    rules = mod.load_rules(RULE_DIR)
    expected = {
        "60_energy/11_water/01_Termicas-Fluidos2_Rafa/Calefaccion/a-esquemas-agua/valv-2vias.elmt": "2-Wege-Magnetventil Trinkwasser",
        "60_energy/11_water/01_Termicas-Fluidos2_Rafa/Calefaccion/a-esquemas-agua/valvula3vias.elmt": "3-Wege-Magnetventil Trinkwasser",
        "60_energy/11_water/plomberie_chauffage/multicouche/rac_multi_25/multi_25_coude.elmt": "Alpex-Bogen 25",
        "60_energy/11_water/plomberie_chauffage/multicouche/rac_multi_32/multi_32_coude.elmt": "Alpex-Bogen 32",
        "60_energy/31_solar_thermal/eau_sanitaire/disconnecteur_01d.elmt": "Systemtrenner rechts",
        "60_energy/31_solar_thermal/eau_sanitaire/disconnecteur_01g.elmt": "Systemtrenner links",
        "60_energy/31_solar_thermal/ballon_echangeur/cumuls_elec_01.elmt": "Elektrischer Trinkwarmwasserspeicher rechts",
        "60_energy/31_solar_thermal/ballon_echangeur/cumulus_elec_2.elmt": "Elektrischer Trinkwarmwasserspeicher links",
    }
    for path, value in expected.items():
        assert rules["path"][path] == value


def test_energy_rule_targets_never_use_generic_placeholder():
    rules = mod.load_rules(RULE_DIR)
    targets = list(rules["path"].values())
    targets += list(rules["en_exact"].values())
    targets += list(rules["es_exact"].values())
    targets += list(rules["fr_exact"].values())
    targets += [target for _, target in rules["en_phrases"]]
    targets += [target for _, target in rules["es_prefixes"]]
    targets += [target for _, target in rules["fr_prefixes"]]
    assert targets
    assert all(value.strip() for value in targets)
    assert all(not value.startswith("Energie-Symbol ") for value in targets)
