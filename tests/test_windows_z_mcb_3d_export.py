from pathlib import Path


SCRIPT = Path("tools/windows/export_z_mcb_3d.bat")


def test_windows_mcb_3d_export_uses_project_python() -> None:
    content = SCRIPT.read_text(encoding="utf-8")

    assert 'set "PYTHON_EXE=.venv\\Scripts\\python.exe"' in content
    assert 'if not exist "%PYTHON_EXE%" set "PYTHON_EXE=python"' in content


def test_windows_mcb_3d_export_checks_tools_before_export() -> None:
    content = SCRIPT.read_text(encoding="utf-8")

    check_call = 'tools\\export_z_mcb_3d.py --check-tools'
    export_call = 'tools\\export_z_mcb_3d.py"'

    assert check_call in content
    assert export_call in content
    assert content.index(check_call) < content.rindex(export_call)


def test_windows_mcb_3d_export_names_expected_outputs() -> None:
    content = SCRIPT.read_text(encoding="utf-8")

    assert 'models\\Z_MCB_1P\\generated\\Z_MCB_1P.step' in content
    assert 'models\\Z_MCB_1P\\generated\\Z_MCB_1P.wrl' in content
    assert 'footprints\\Z_MCB.pretty\\Z_MCB_1P_18mm.kicad_mod' in content
