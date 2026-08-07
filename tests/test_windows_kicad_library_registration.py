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


def test_projectos_3d_model_path_points_to_kicad_runtime_not_repository() -> None:
    detect = (REPO_ROOT / "tools/windows/detect_kicad.bat").read_text(encoding="utf-8")
    paths = (REPO_ROOT / "tools/windows/register_kicad_z_paths.ps1").read_text(
        encoding="utf-8"
    )

    assert "PROJECTOS_MODEL_SOURCE_DIR=%PROJECTOS_REPOSITORY_ROOT%\\models" in detect
    assert 'set "Z_PROJECTOS_3DMODEL_DIR=%KICAD_Z_3DMODEL_DIR%"' in detect
    assert "Z_PROJECTOS_3DMODEL_DIR" in paths
    assert "$projectOs3dRuntime" in paths
    assert "Z_PROJECTOS_3DMODEL_DIR   = $projectOs3dRuntime" in paths


def test_projectos_3d_path_migrates_legacy_repository_value() -> None:
    paths = (REPO_ROOT / "tools/windows/register_kicad_z_paths.ps1").read_text(
        encoding="utf-8"
    )

    assert "$entry.Key -eq 'Z_PROJECTOS_3DMODEL_DIR'" in paths
    assert "$property.Value = $entry.Value" in paths
    assert "Andere bestehende, abweichende Benutzerwerte niemals automatisch überschreiben" in paths


def test_projectos_models_are_synchronized_from_repository_to_kicad_runtime() -> None:
    libraries = (REPO_ROOT / "tools/windows/register_kicad_z_libraries.ps1").read_text(
        encoding="utf-8"
    )

    assert "$modelSource = Join-Path $RepositoryRoot 'models'" in libraries
    assert "$modelTarget = Join-Path $UserRoot '3dmodels\\Z_3DModell.3dshapes'" in libraries
    assert "Copy-Item -LiteralPath $model.FullName -Destination $target -Force" in libraries
    assert "Substring($modelSource.Length)" in libraries


def test_z_3d_model_library_is_created_registered_and_synchronized() -> None:
    detect = (REPO_ROOT / "tools/windows/detect_kicad.bat").read_text(encoding="utf-8")
    paths = (REPO_ROOT / "tools/windows/register_kicad_z_paths.ps1").read_text(
        encoding="utf-8"
    )
    libraries = (REPO_ROOT / "tools/windows/register_kicad_z_libraries.ps1").read_text(
        encoding="utf-8"
    )

    assert "Z_3DModell.3dshapes" in detect
    assert "KICAD_Z_3DMODEL_DIR" in detect
    assert "Z_3DModell.3dshapes" in paths
    assert "3dmodels\\Z_3DModell.3dshapes" in libraries
    assert "'.step', '.stp', '.wrl'" in libraries
    assert "KICAD_Z_3DMODEL_FILES" in libraries


def test_required_z_entries_are_reported() -> None:
    detect = (REPO_ROOT / "tools/windows/detect_kicad.bat").read_text(encoding="utf-8")
    libraries = (REPO_ROOT / "tools/windows/register_kicad_z_libraries.ps1").read_text(
        encoding="utf-8"
    )

    assert "KICAD_Z_REQUIRED_ENTRIES" in detect
    assert "KICAD_Z_REQUIRED_ENTRIES" in libraries
