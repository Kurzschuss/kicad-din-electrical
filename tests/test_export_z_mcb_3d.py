from pathlib import Path

from tools.export_z_mcb_3d import (
    MODEL_DIR,
    SOURCE,
    STEP_OUTPUT,
    WRL_OUTPUT,
    Toolchain,
    find_windows_freecadcmd,
    find_windows_openscad,
    freecad_conversion_script,
)


def test_mcb_3d_export_uses_project_source_only() -> None:
    assert SOURCE == MODEL_DIR / "Z_MCB_1P.scad"
    assert SOURCE.is_file()
    assert STEP_OUTPUT.name == "Z_MCB_1P.step"
    assert WRL_OUTPUT.name == "Z_MCB_1P.wrl"


def test_freecad_conversion_exports_step_and_wrl(tmp_path: Path) -> None:
    stl = tmp_path / "source.stl"
    step = tmp_path / "model.step"
    wrl = tmp_path / "model.wrl"

    script = freecad_conversion_script(stl, step, wrl)

    assert str(stl) in script
    assert str(step) in script
    assert str(wrl) in script
    assert "Part.export" in script
    assert "Mesh.export" in script
    assert "TraceParts" not in script
    assert "Siemens" not in script


def test_toolchain_keeps_tools_explicit() -> None:
    toolchain = Toolchain(openscad="openscad", freecadcmd="FreeCADCmd")

    assert toolchain.openscad == "openscad"
    assert toolchain.freecadcmd == "FreeCADCmd"


def test_windows_openscad_detection_uses_program_files(monkeypatch, tmp_path: Path) -> None:
    program_files = tmp_path / "Program Files"
    exe = program_files / "OpenSCAD" / "openscad.exe"
    exe.parent.mkdir(parents=True)
    exe.write_text("", encoding="utf-8")

    monkeypatch.setenv("ProgramFiles", str(program_files))
    monkeypatch.delenv("ProgramFiles(x86)", raising=False)
    monkeypatch.delenv("LOCALAPPDATA", raising=False)

    assert find_windows_openscad() == str(exe)


def test_windows_freecad_detection_accepts_versioned_folder(monkeypatch, tmp_path: Path) -> None:
    program_files = tmp_path / "Program Files"
    exe = program_files / "FreeCAD 1.0" / "bin" / "FreeCADCmd.exe"
    exe.parent.mkdir(parents=True)
    exe.write_text("", encoding="utf-8")

    monkeypatch.setenv("ProgramFiles", str(program_files))
    monkeypatch.delenv("ProgramFiles(x86)", raising=False)
    monkeypatch.delenv("LOCALAPPDATA", raising=False)

    assert find_windows_freecadcmd() == str(exe)
