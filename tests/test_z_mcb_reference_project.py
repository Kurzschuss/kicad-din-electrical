import json
from pathlib import Path


PROJECT = Path("projects/Z_MCB_reference")


def test_reference_project_contains_required_files():
    required = {
        "README.md",
        "Z_MCB_reference.kicad_pro",
        "Z_MCB_reference.kicad_sch",
        "sym-lib-table",
        "Z_PROJECT_MANIFEST.json",
    }
    assert required <= {path.name for path in PROJECT.iterdir()}


def test_symbol_library_is_bound_reproducibly():
    table = (PROJECT / "sym-lib-table").read_text(encoding="utf-8")
    assert '(name "Z_MCB")' in table
    assert "${KIPRJMOD}/../../symbols/Z_MCB.kicad_sym" in table


def test_manifest_uses_z_prefix_and_keeps_practice_status_honest():
    manifest = json.loads((PROJECT / "Z_PROJECT_MANIFEST.json").read_text(encoding="utf-8"))
    assert manifest["id"].startswith("Z_")
    assert manifest["device_family"] == "Z_MCB"
    assert manifest["symbol_id"] == "Z_MCB:MCB"
    assert manifest["quality_level"] == "Entwurf"
    assert manifest["validation"] == {
        "library_binding": True,
        "symbol_placed": False,
        "erc_checked": False,
        "opened_in_kicad": False,
    }


def test_project_documentation_states_practice_gate():
    readme = (PROJECT / "README.md").read_text(encoding="utf-8")
    assert "Praxisgetestet" in readme
    assert "ERC" in readme
    assert "KiCad ist der Standard" in readme
