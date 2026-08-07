#!/usr/bin/env python3
"""Reproduzierbare Exportkette für das ProjectOS-eigene MCB-1P-3D-Modell.

Die editierbare Single Source of Truth bleibt die OpenSCAD-Datei. Für den Export
werden ausschließlich lokal installierte Open-Source-Werkzeuge aufgerufen:

1. OpenSCAD rendert die Quelle nach STL.
2. FreeCADCmd wandelt das STL-Netz in einen Volumenkörper um.
3. FreeCAD exportiert STEP und VRML/WRL für KiCad.
4. Optional wird die geometrische Maßhaltigkeit der Exportartefakte geprüft.

Das Skript lädt keine externen CAD-Daten und verwendet keine Herstellergeometrie.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import os
from pathlib import Path
import re
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
EXPECTED_MODULE_WIDTH_MM = 18.0
GEOMETRY_TOLERANCE_MM = 0.05


@dataclass(frozen=True)
class Toolchain:
    openscad: str
    freecadcmd: str


@dataclass(frozen=True)
class Bounds:
    x: float
    y: float
    z: float

    def format(self) -> str:
        return f"X={self.x:.4f} mm, Y={self.y:.4f} mm, Z={self.z:.4f} mm"


def find_tool(names: tuple[str, ...]) -> str | None:
    for name in names:
        found = shutil.which(name)
        if found:
            return found
    return None


def windows_program_roots() -> tuple[Path, ...]:
    """Liefert vorhandene Windows-Installationswurzeln ohne PATH-Abhängigkeit."""
    roots: list[Path] = []
    for variable in ("ProgramFiles", "ProgramFiles(x86)"):
        value = os.environ.get(variable)
        if value:
            path = Path(value)
            if path not in roots:
                roots.append(path)
    return tuple(roots)


def find_windows_openscad() -> str | None:
    for root in windows_program_roots():
        candidate = root / "OpenSCAD" / "openscad.exe"
        if candidate.is_file():
            return str(candidate)
    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        candidate = Path(local_app_data) / "Programs" / "OpenSCAD" / "openscad.exe"
        if candidate.is_file():
            return str(candidate)
    return None


def find_windows_freecadcmd() -> str | None:
    candidates: list[Path] = []
    for root in windows_program_roots():
        candidates.extend(root.glob("FreeCAD*/bin/FreeCADCmd.exe"))
        candidates.extend(root.glob("FreeCAD*/bin/freecadcmd.exe"))
    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        local_root = Path(local_app_data) / "Programs"
        candidates.extend(local_root.glob("FreeCAD*/bin/FreeCADCmd.exe"))
        candidates.extend(local_root.glob("FreeCAD*/bin/freecadcmd.exe"))
    existing = sorted(
        (path for path in candidates if path.is_file()),
        key=lambda path: path.as_posix().casefold(),
        reverse=True,
    )
    return str(existing[0]) if existing else None


def detect_toolchain() -> Toolchain:
    openscad = find_tool(("openscad", "OpenSCAD", "openscad.exe"))
    freecadcmd = find_tool(("FreeCADCmd", "freecadcmd", "FreeCADCmd.exe"))

    if sys.platform == "win32":
        openscad = openscad or find_windows_openscad()
        freecadcmd = freecadcmd or find_windows_freecadcmd()

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
    return f'''import FreeCAD as App\nimport Mesh\nimport Part\n\nstl = r"{stl_path}"\nstep = r"{step_path}"\nwrl = r"{wrl_path}"\n\ndoc = App.newDocument("Z_MCB_1P")\nmesh_obj = doc.addObject("Mesh::Feature", "SourceMesh")\nmesh_obj.Mesh = Mesh.Mesh(stl)\n\nshape = Part.Shape()\nshape.makeShapeFromMesh(mesh_obj.Mesh.Topology, 0.05)\nsolid = Part.makeSolid(shape) if shape.Shells else shape\npart_obj = doc.addObject("Part::Feature", "Z_MCB_1P")\npart_obj.Shape = solid\n\ndoc.recompute()\nPart.export([part_obj], step)\n\n# VRML kann über das Mesh-Modul headless exportiert werden.\nMesh.export([part_obj], wrl)\n\nApp.closeDocument(doc.Name)\n'''


def freecad_step_measurement_script(step_path: Path) -> str:
    return f'''import Part\nshape = Part.Shape()\nshape.read(r"{step_path}")\nb = shape.BoundBox\nprint("PROJECTOS_BOUNDS={{:.9f}},{{:.9f}},{{:.9f}}".format(b.XLength, b.YLength, b.ZLength))\n'''


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


def measure_step(toolchain: Toolchain, step_path: Path) -> Bounds:
    with tempfile.TemporaryDirectory(prefix="projectos-z-mcb-measure-") as temp_dir:
        script = Path(temp_dir) / "measure_step.py"
        script.write_text(freecad_step_measurement_script(step_path), encoding="utf-8")
        result = subprocess.run(
            [toolchain.freecadcmd, str(script)],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

    for line in result.stdout.splitlines():
        if line.startswith("PROJECTOS_BOUNDS="):
            values = line.partition("=")[2].split(",")
            if len(values) == 3:
                return Bounds(*(float(value) for value in values))
    raise RuntimeError("FreeCAD lieferte keine auswertbaren STEP-Abmessungen.")


def measure_wrl(wrl_path: Path) -> Bounds:
    """Liest die Koordinatenausdehnung aus einer textuellen VRML/WRL-Datei."""
    text = wrl_path.read_text(encoding="utf-8", errors="replace")
    number = r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?"
    points: list[tuple[float, float, float]] = []
    for match in re.finditer(r"point\s*\[(.*?)\]", text, flags=re.IGNORECASE | re.DOTALL):
        values = [float(value) for value in re.findall(number, match.group(1))]
        for index in range(0, len(values) - 2, 3):
            points.append((values[index], values[index + 1], values[index + 2]))

    if not points:
        raise RuntimeError("WRL enthält keine auswertbaren Koordinatenpunkte.")

    xs, ys, zs = zip(*points)
    return Bounds(max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs))


def validate_module_width(bounds: Bounds, *, label: str) -> None:
    difference = abs(bounds.x - EXPECTED_MODULE_WIDTH_MM)
    if difference > GEOMETRY_TOLERANCE_MM:
        raise RuntimeError(
            f"{label}-Modulbreite ist nicht maßhaltig: {bounds.x:.4f} mm statt "
            f"{EXPECTED_MODULE_WIDTH_MM:.4f} mm (Toleranz {GEOMETRY_TOLERANCE_MM:.2f} mm)."
        )


def check_geometry(toolchain: Toolchain) -> tuple[Bounds, Bounds]:
    """Exportiert temporär und prüft STEP/WRL ohne versionierte Artefakte zu verändern."""
    with tempfile.TemporaryDirectory(prefix="projectos-z-mcb-geometry-") as temp_dir:
        step, wrl = export_model(toolchain, output_dir=Path(temp_dir))
        step_bounds = measure_step(toolchain, step)
        wrl_bounds = measure_wrl(wrl)

    validate_module_width(step_bounds, label="STEP")
    validate_module_width(wrl_bounds, label="WRL")
    return step_bounds, wrl_bounds


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check-tools",
        action="store_true",
        help="nur prüfen, ob OpenSCAD und FreeCADCmd verfügbar sind",
    )
    parser.add_argument(
        "--check-geometry",
        action="store_true",
        help="temporär exportieren und STEP-/WRL-Maßhaltigkeit prüfen",
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

    if args.check_geometry:
        try:
            step_bounds, wrl_bounds = check_geometry(toolchain)
        except (FileNotFoundError, RuntimeError, subprocess.CalledProcessError) as exc:
            print(f"3D-Maßhaltigkeitsprüfung fehlgeschlagen: {exc}", file=sys.stderr)
            return 1
        print(f"Soll-Modulbreite: {EXPECTED_MODULE_WIDTH_MM:.4f} mm")
        print(f"STEP-Abmessungen: {step_bounds.format()}")
        print(f"WRL-Abmessungen:  {wrl_bounds.format()}")
        print("3D-Maßhaltigkeitsprüfung erfolgreich.")
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
