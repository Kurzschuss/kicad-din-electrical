#!/usr/bin/env python3
"""Reproduzierbare Exportkette für das ProjectOS-eigene MCB-1P-3D-Modell.

Die editierbare Single Source of Truth bleibt die OpenSCAD-Datei. Für den Export
werden ausschließlich lokal installierte Open-Source-Werkzeuge aufgerufen:

1. OpenSCAD rendert die Quelle nach STL.
2. FreeCADCmd wandelt das STL-Netz in einen Volumenkörper um.
3. FreeCAD exportiert STEP und VRML/WRL für KiCad.

Das Skript lädt keine externen CAD-Daten und verwendet keine Herstellergeometrie.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

REPO_ROOT = Path(__file__).resolve().parents[1]
MODEL_DIR = REPO_ROOT / "models" / "Z_MCB_1P"
SOURCE = MODEL_DIR / "Z_MCB_1P.scad"
OUTPUT_DIR = MODEL_DIR / "generated"
STEP_OUTPUT = OUTPUT_DIR / "Z_MCB_1P.step"
WRL_OUTPUT = OUTPUT_DIR / "Z_MCB_1P.wrl"


@dataclass(frozen=True)
class Toolchain:
    openscad: str
    freecadcmd: str


def find_tool(names: tuple[str, ...]) -> str | None:
    for name in names:
        found = shutil.which(name)
        if found:
            return found
    return None


def detect_toolchain() -> Toolchain:
    openscad = find_tool(("openscad", "OpenSCAD"))
    freecadcmd = find_tool(("FreeCADCmd", "freecadcmd", "FreeCADCmd.exe"))
    missing: list[str] = []
    if openscad is None:
        missing.append("OpenSCAD")
    if freecadcmd is None:
        missing.append("FreeCADCmd")
    if missing:
        raise RuntimeError("Fehlende 3D-Exportwerkzeuge: " + ", ".join(missing))
    return Toolchain(openscad=openscad, freecadcmd=freecadcmd)


def freecad_conversion_script(stl_path: Path, step_path: Path, wrl_path: Path) -> str:
    """Erzeugt das FreeCAD-Python-Skript für STEP- und WRL-Ausgabe."""
    return f'''import FreeCAD as App\nimport Mesh\nimport Part\n\nstl = r"{stl_path}"\nstep = r"{step_path}"\nwrl = r"{wrl_path}"\n\ndoc = App.newDocument("Z_MCB_1P")\nmesh_obj = doc.addObject("Mesh::Feature", "SourceMesh")\nmesh_obj.Mesh = Mesh.Mesh(stl)\n\nshape = Part.Shape()\nshape.makeShapeFromMesh(mesh_obj.Mesh.Topology, 0.05)\nsolid = Part.makeSolid(shape) if shape.Shells else shape\npart_obj = doc.addObject("Part::Feature", "Z_MCB_1P")\npart_obj.Shape = solid\n\ndoc.recompute()\nPart.export([part_obj], step)\nGuiUp = False\ntry:\n    import FreeCADGui  # noqa: F401\n    GuiUp = True\nexcept Exception:\n    pass\n\n# VRML kann über das Mesh-Modul headless exportiert werden.\nMesh.export([part_obj], wrl)\n\ndoc.close()\n'''


def export_model(toolchain: Toolchain, *, output_dir: Path = OUTPUT_DIR) -> tuple[Path, Path]:
    if not SOURCE.is_file():
        raise FileNotFoundError(f"OpenSCAD-Quelle fehlt: {SOURCE}")

    output_dir.mkdir(parents=True, exist_ok=True)
    step_output = output_dir / STEP_OUTPUT.name
    wrl_output = output_dir / WRL_OUTPUT.name

    with tempfile.TemporaryDirectory(prefix="projectos-z-mcb-") as temp_dir:
        temp = Path(temp_dir)
        stl = temp / "Z_MCB_1P.stl"
        converter = temp / "convert.py"

        subprocess.run(
            [toolchain.openscad, "-o", str(stl), str(SOURCE)],
            check=True,
        )
        converter.write_text(
            freecad_conversion_script(stl, step_output, wrl_output),
            encoding="utf-8",
        )
        subprocess.run([toolchain.freecadcmd, str(converter)], check=True)

    missing_outputs = [path for path in (step_output, wrl_output) if not path.is_file()]
    if missing_outputs:
        raise RuntimeError(
            "Export wurde ohne erwartete Ausgabedateien beendet: "
            + ", ".join(str(path) for path in missing_outputs)
        )
    return step_output, wrl_output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check-tools",
        action="store_true",
        help="nur prüfen, ob OpenSCAD und FreeCADCmd verfügbar sind",
    )
    args = parser.parse_args()

    try:
        toolchain = detect_toolchain()
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if args.check_tools:
        print(f"OpenSCAD: {toolchain.openscad}")
        print(f"FreeCADCmd: {toolchain.freecadcmd}")
        return 0

    try:
        step, wrl = export_model(toolchain)
    except (FileNotFoundError, RuntimeError, subprocess.CalledProcessError) as exc:
        print(f"3D-Export fehlgeschlagen: {exc}", file=sys.stderr)
        return 1

    print(f"STEP erzeugt: {step.relative_to(REPO_ROOT)}")
    print(f"WRL erzeugt: {wrl.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
