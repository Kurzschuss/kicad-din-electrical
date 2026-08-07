#!/usr/bin/env python3
"""Exportiert und prüft das ProjectOS-eigene MCB-3P-3D-Modell."""

from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys
import tempfile

from tools.export_z_mcb_3d import (
    GEOMETRY_TOLERANCE_MM,
    REPO_ROOT,
    Toolchain,
    detect_toolchain,
    freecad_conversion_script,
    measure_step,
    measure_wrl,
)

MODEL_DIR = REPO_ROOT / "models" / "Z_MCB_3P"
SOURCE = MODEL_DIR / "Z_MCB_3P.scad"
OUTPUT_DIR = MODEL_DIR / "generated"
STEP_OUTPUT = OUTPUT_DIR / "Z_MCB_3P.step"
WRL_OUTPUT = OUTPUT_DIR / "Z_MCB_3P.wrl"
EXPECTED_WIDTH_MM = 54.0
EXPECTED_LENGTH_MM = 84.0


def export_model(toolchain: Toolchain, *, output_dir: Path = OUTPUT_DIR) -> tuple[Path, Path]:
    if not SOURCE.is_file():
        raise FileNotFoundError(f"OpenSCAD-Quelle fehlt: {SOURCE}")

    output_dir.mkdir(parents=True, exist_ok=True)
    step_output = output_dir / STEP_OUTPUT.name
    wrl_output = output_dir / WRL_OUTPUT.name

    with tempfile.TemporaryDirectory(prefix="projectos-z-mcb-3p-") as temp_dir:
        temp = Path(temp_dir)
        stl = temp / "Z_MCB_3P.stl"
        converter = temp / "convert.py"
        subprocess.run([toolchain.openscad, "-o", str(stl), str(SOURCE)], check=True)
        converter.write_text(
            freecad_conversion_script(stl, step_output, wrl_output), encoding="utf-8"
        )
        subprocess.run([toolchain.freecadcmd, str(converter)], check=True)

    for path in (step_output, wrl_output):
        if not path.is_file():
            raise RuntimeError(f"Erwartete Ausgabedatei fehlt: {path}")
    return step_output, wrl_output


def validate_bounds(label: str, x: float, y: float) -> None:
    if abs(x - EXPECTED_WIDTH_MM) > GEOMETRY_TOLERANCE_MM:
        raise RuntimeError(
            f"{label}-Breite {x:.4f} mm statt {EXPECTED_WIDTH_MM:.4f} mm"
        )
    if abs(y - EXPECTED_LENGTH_MM) > GEOMETRY_TOLERANCE_MM:
        raise RuntimeError(
            f"{label}-Länge {y:.4f} mm statt {EXPECTED_LENGTH_MM:.4f} mm"
        )


def check_geometry(toolchain: Toolchain) -> None:
    with tempfile.TemporaryDirectory(prefix="projectos-z-mcb-3p-geometry-") as temp_dir:
        step, wrl = export_model(toolchain, output_dir=Path(temp_dir))
        step_bounds = measure_step(toolchain, step)
        wrl_bounds = measure_wrl(wrl)

    validate_bounds("STEP", step_bounds.x, step_bounds.y)
    validate_bounds("WRL", wrl_bounds.x, wrl_bounds.y)
    print(f"Soll-Draufsicht: X={EXPECTED_WIDTH_MM:.4f} mm, Y={EXPECTED_LENGTH_MM:.4f} mm")
    print(f"STEP-Abmessungen: {step_bounds.format()}")
    print(f"WRL-Abmessungen:  {wrl_bounds.format()}")
    print("MCB-3P-3D-Maßhaltigkeitsprüfung erfolgreich.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-tools", action="store_true")
    parser.add_argument("--check-geometry", action="store_true")
    args = parser.parse_args()

    try:
        toolchain = detect_toolchain()
        if args.check_tools:
            print(f"OpenSCAD: {toolchain.openscad}")
            print(f"FreeCADCmd: {toolchain.freecadcmd}")
            return 0
        if args.check_geometry:
            check_geometry(toolchain)
            return 0
        step, wrl = export_model(toolchain)
    except (FileNotFoundError, RuntimeError, subprocess.CalledProcessError) as exc:
        print(f"MCB-3P-3D-Export fehlgeschlagen: {exc}", file=sys.stderr)
        return 1

    print(f"STEP erzeugt: {step.relative_to(REPO_ROOT)}")
    print(f"WRL erzeugt: {wrl.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
