"""Track intentionally empty KiCad symbol-library placeholders."""
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
SYMBOL_ROOT = ROOT / "symbols"
TOP_LEVEL_SYMBOL_RE = re.compile(r'^  \(symbol "([^"]+)"', re.MULTILINE)

# These files are intentional placeholders. Additions or removals must be explicit.
EXPECTED_EMPTY_SYMBOL_LIBRARIES = {
    "symbols/Z_DIN_Control.kicad_sym",
    "symbols/Z_DIN_Electrical.kicad_sym",
    "symbols/Z_DIN_Power.kicad_sym",
    "symbols/Z_DIN_Safety.kicad_sym",
    "symbols/Z_DIN_Terminals.kicad_sym",
    "symbols/Z_DISTRIBUTION.kicad_sym",
    "symbols/Z_MCB_single_pole.kicad_sym",
    "symbols/Z_MOTOR_PROTECT.kicad_sym",
    "symbols/Z_RCBO.kicad_sym",
}


def test_empty_symbol_libraries_match_explicit_allowlist():
    empty_libraries = {
        path.relative_to(ROOT).as_posix()
        for path in SYMBOL_ROOT.rglob("*.kicad_sym")
        if not TOP_LEVEL_SYMBOL_RE.search(path.read_text(encoding="utf-8"))
    }

    assert empty_libraries == EXPECTED_EMPTY_SYMBOL_LIBRARIES
