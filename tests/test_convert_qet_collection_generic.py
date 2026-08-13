from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "tools" / "convert_qet_to_kicad.py"
SPEC = importlib.util.spec_from_file_location("convert_qet_to_kicad_collection_generic", MODULE_PATH)
assert SPEC and SPEC.loader
mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = mod
SPEC.loader.exec_module(mod)


LOGIC_GATE = """\
<definition version="0.100.0" type="element">
  <names>
    <name lang="de">UND-Gatter</name>
    <name lang="en">AND gate</name>
  </names>
  <description>
    <rect x="-10" y="-10" width="20" height="20"
          style="line-style:normal;line-weight:normal;filling:none;color:black"/>
    <terminal name="A" x="-11" y="-5" orientation="w"/>
    <terminal name="B" x="-11" y="5" orientation="w"/>
    <terminal name="Q" x="11" y="0" orientation="e"/>
  </description>
</definition>
"""


def test_collection_root_is_preserved_without_qet_labels(tmp_path: Path):
    qet = tmp_path / "20_logic"
    scope = qet / "2010_logic_gates" / "201020_iec_60617"
    scope.mkdir(parents=True)
    (scope / "and.elmt").write_text(LOGIC_GATE, encoding="utf-8")

    output = tmp_path / "logic.kicad_sym"
    report = tmp_path / "report.json"
    stats = mod.convert_library(qet, None, ["2010_logic_gates"], output, report)
    data = output.read_text(encoding="utf-8")
    payload = json.loads(report.read_text(encoding="utf-8"))

    assert stats.source_files == stats.converted == 1
    assert stats.missing_german_names == 0
    assert stats.fallback_references == 1
    assert '(property "Value" "UND-Gatter"' in data
    assert '(property "Reference" "QET"' in data
    assert '20_logic / 2010_logic_gates / 201020_iec_60617' in data
    assert '(property "QET_Source_Path" "20_logic/2010_logic_gates/201020_iec_60617/and.elmt"' in data
    assert "reference_prefix_missing:qet_placeholder" in data
    assert "10_electric" not in data
    assert payload["labels_file"] is None


def test_prefix_inheritance_accepts_arbitrary_collection_root():
    prefixes = {
        ("2010_logic_gates",): "G",
        ("2010_logic_gates", "201020_iec_60617"): "L",
    }

    assert mod.prefix_for_category(
        ["20_logic", "2010_logic_gates", "201020_iec_60617", "nested"], prefixes
    ) == "L"


def test_main_discovers_collection_scopes_when_none_are_given(tmp_path: Path):
    qet = tmp_path / "20_logic"
    first = qet / "2010_logic_gates"
    second = qet / "2020_flow_chart"
    first.mkdir(parents=True)
    second.mkdir(parents=True)
    (first / "gate.elmt").write_text(LOGIC_GATE, encoding="utf-8")
    (second / "flow.elmt").write_text(LOGIC_GATE.replace("UND-Gatter", "Ablaufblock"), encoding="utf-8")

    output = tmp_path / "logic.kicad_sym"
    report = tmp_path / "report.json"
    result = mod.main([
        "--qet-root", str(qet),
        "--output", str(output),
        "--report", str(report),
        "--fail-on-errors",
    ])
    payload = json.loads(report.read_text(encoding="utf-8"))

    assert result == 0
    assert payload["source_files"] == payload["converted"] == 2
    assert payload["scopes"] == ["2010_logic_gates", "2020_flow_chart"]
    assert payload["labels_file"] is None
