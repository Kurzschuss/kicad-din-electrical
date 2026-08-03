from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_detect_kicad_registers_global_z_libraries() -> None:
    content = (REPO_ROOT / "tools/windows/detect_kicad.bat").read_text(encoding="utf-8")
    assert "register_kicad_z_libraries.ps1" in content
    assert "KICAD_Z_DESIGN_BLOCK_DIR" in content
    assert "designblocks" in content


def test_registration_script_handles_all_three_global_tables() -> None:
    content = (REPO_ROOT / "tools/windows/register_kicad_z_libraries.ps1").read_text(
        encoding="utf-8"
    )
    assert "sym-lib-table" in content
    assert "fp-lib-table" in content
    assert "design-block-lib-table" in content
    assert "sym_lib_table" in content
    assert "fp_lib_table" in content
    assert "design_block_lib_table" in content


def test_registration_uses_only_z_prefixed_libraries() -> None:
    content = (REPO_ROOT / "tools/windows/register_kicad_z_libraries.ps1").read_text(
        encoding="utf-8"
    )
    assert "Z_*.kicad_sym" in content
    assert "Z_*.pretty" in content
    assert "Z_*.kicad_blocks" in content
    assert ".z-backup" in content


def test_design_block_path_is_registered_in_kicad_paths() -> None:
    content = (REPO_ROOT / "tools/windows/register_kicad_z_paths.ps1").read_text(
        encoding="utf-8"
    )
    assert "KICAD_Z_DESIGN_BLOCK_DIR" in content
    assert "designblocks" in content
