from pathlib import Path


REGISTER_SCRIPT = Path("tools/windows/register_kicad_z_libraries.ps1")
COMMON_MCB = Path("models/Z_MCB_common/Z_MCB_module.scad")


def test_footprint_sync_mirrors_library_without_nested_pretty_directory() -> None:
    content = REGISTER_SCRIPT.read_text(encoding="utf-8")

    assert "function Mirror-Directory" in content
    assert "Remove-Item -LiteralPath $Target -Recurse -Force" in content
    assert "Mirror-Directory -Source $_.FullName -Target $target" in content


def test_mcb_prototype_height_is_bounded_for_kicad_preview() -> None:
    content = COMMON_MCB.read_text(encoding="utf-8")

    assert "mcb_module_width = 18.0;" in content
    assert "mcb_module_length = 84.0;" in content
    assert "mcb_body_height = 62.0;" in content
    assert "mcb_front_step_height = 12.0;" in content
    assert "mcb_toggle_height = 6.0;" in content
