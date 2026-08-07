#!/usr/bin/env python3
"""Exportiert ProjectOS RCD/RCCB 2P/4P nach STEP und WRL und prueft die Draufsicht."""
from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import tempfile

from tools.export_z_mcb_3d import Bounds, detect_toolchain, measure_wrl, GEOMETRY_TOLERANCE_MM

REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_LENGTH_MM = 84.0


def freecad_conversion_script(stl: Path, step: Path, wrl: Path) -> str:
    return f'''import FreeCAD as App\nimport Mesh\nimport Part\n\ndoc=App.newDocument("Z_RCD")\nmesh=doc.addObject("Mesh::Feature","SourceMesh")\nmesh.Mesh=Mesh.Mesh(r"{stl}")\nshape=Part.Shape()\nshape.makeShapeFromMesh(mesh.Mesh.Topology,0.05)\nsolid=Part.makeSolid(shape) if shape.Shells else shape\npart=doc.addObject("Part::Feature","Z_RCD")\npart.Shape=solid\ndoc.recompute()\nPart.export([part],r"{step}")\nMesh.export([part],r"{wrl}")\nApp.closeDocument(doc.Name)\n'''


def freecad_measure_script(step: Path) -> str:
    return f'''import Part\ns=Part.Shape()\ns.read(r"{step}")\nb=s.BoundBox\nprint("PROJECTOS_BOUNDS={{:.9f}},{{:.9f}},{{:.9f}}".format(b.XLength,b.YLength,b.ZLength))\n'''


def measure_step(toolchain, step: Path) -> Bounds:
    with tempfile.TemporaryDirectory(prefix="projectos-z-rcd-measure-") as td:
        script=Path(td)/"measure.py"
        script.write_text(freecad_measure_script(step),encoding="utf-8")
        result=subprocess.run([toolchain.freecadcmd,str(script)],check=True,capture_output=True,text=True,encoding="utf-8",errors="replace")
    for line in result.stdout.splitlines():
        if line.startswith("PROJECTOS_BOUNDS="):
            x,y,z=(float(v) for v in line.split("=",1)[1].split(","))
            return Bounds(x,y,z)
    raise RuntimeError("FreeCAD lieferte keine RCD-Abmessungen")


def validate(bounds: Bounds, poles: int, label: str) -> None:
    expected_width=poles*18.0
    for name,actual,expected in (("Breite",bounds.x,expected_width),("Laenge",bounds.y,EXPECTED_LENGTH_MM)):
        if abs(actual-expected) > GEOMETRY_TOLERANCE_MM + 1e-9:
            raise RuntimeError(f"{label}-{name} nicht masshaltig: {actual:.4f} statt {expected:.4f} mm")


def export_variant(poles: int, output_dir: Path | None=None):
    toolchain=detect_toolchain()
    name=f"Z_RCD_{poles}P"
    source=REPO_ROOT/"models"/name/f"{name}.scad"
    out=output_dir or (REPO_ROOT/"models"/name/"generated")
    out.mkdir(parents=True,exist_ok=True)
    step=out/f"{name}.step"
    wrl=out/f"{name}.wrl"
    with tempfile.TemporaryDirectory(prefix=f"projectos-z-rcd-{poles}p-") as td:
        td=Path(td)
        stl=td/f"{name}.stl"
        conv=td/"convert.py"
        subprocess.run([toolchain.openscad,"-o",str(stl),str(source)],check=True)
        conv.write_text(freecad_conversion_script(stl,step,wrl),encoding="utf-8")
        subprocess.run([toolchain.freecadcmd,str(conv)],check=True)
    return toolchain,step,wrl


def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("--poles",type=int,choices=(2,4),required=True)
    p.add_argument("--check-tools",action="store_true")
    p.add_argument("--check-geometry",action="store_true")
    args=p.parse_args()
    try:
        if args.check_tools:
            tc=detect_toolchain()
            print(f"OpenSCAD: {tc.openscad}")
            print(f"FreeCADCmd: {tc.freecadcmd}")
            return 0
        if args.check_geometry:
            with tempfile.TemporaryDirectory(prefix=f"projectos-z-rcd-{args.poles}p-geometry-") as td:
                tc,step,wrl=export_variant(args.poles,Path(td))
                sb=measure_step(tc,step); wb=measure_wrl(wrl)
            validate(sb,args.poles,"STEP"); validate(wb,args.poles,"WRL")
            print(f"Soll-Draufsicht: X={args.poles*18.0:.4f} mm, Y={EXPECTED_LENGTH_MM:.4f} mm")
            print(f"STEP-Abmessungen: {sb.format()}")
            print(f"WRL-Abmessungen:  {wb.format()}")
            print(f"RCD-{args.poles}P-3D-Masshaltigkeitspruefung erfolgreich.")
            return 0
        _,step,wrl=export_variant(args.poles)
        print(f"STEP erzeugt: {step.relative_to(REPO_ROOT)}")
        print(f"WRL erzeugt: {wrl.relative_to(REPO_ROOT)}")
        return 0
    except Exception as exc:
        print(f"RCD-3D-Export fehlgeschlagen: {exc}")
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
