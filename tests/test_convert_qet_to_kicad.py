from __future__ import annotations

import importlib.util
import json
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "tools" / "convert_qet_to_kicad.py"
SPEC = importlib.util.spec_from_file_location("convert_qet_to_kicad", MODULE_PATH)
assert SPEC and SPEC.loader
mod = importlib.util.module_from_spec(SPEC)
import sys
sys.modules[SPEC.name] = mod
SPEC.loader.exec_module(mod)


MOTOR = """\
<definition version="0.100.0" type="element" link_type="simple" width="40" height="60" hotspot_x="24" hotspot_y="32">
  <uuid uuid="{31693403-3637-0043-a7d5-dea95ddaa603}"/>
  <names>
    <name lang="de">Motor</name>
    <name lang="en">Engine</name>
  </names>
  <informations>Author: The QElectroTech team
License: see http://qelectrotech.org/wiki/doc/elements_license</informations>
  <description>
    <dynamic_text x="18" y="-12.5" text_from="ElementInfo" font="Liberation Sans,9">
      <text></text><info_name>label</info_name>
    </dynamic_text>
    <ellipse x="-10.5" y="-10.5" width="21" height="21" style="line-style:normal;line-weight:normal;filling:none;color:black"/>
    <ellipse x="-13" y="-13" width="26" height="26" style="line-style:normal;line-weight:normal;filling:none;color:black"/>
    <line x1="0" y1="-13" x2="0" y2="-20" end1="none" end2="none" style="line-style:normal;line-weight:normal;filling:none;color:black"/>
    <text text="M" x="-8.25" y="7" rotation="0" font="Liberation Sans,14"/>
    <terminal uuid="{ad5e}" name="" x="0" y="-21" orientation="n" type="Generic"/>
  </description>
</definition>
"""

ZERO_PIN = """\
<definition version="0.100.0" type="element" width="40" height="40">
  <names><name lang="de">Hinweisrahmen</name></names>
  <informations>Author: Example
License: CC-BY</informations>
  <description>
    <rect x="-10" y="-5" width="20" height="10" style="line-style:dashed;line-weight:thin;filling:none;color:black"/>
    <text text="ACHTUNG" x="-8" y="0" rotation="0" font="Liberation Sans,6"/>
  </description>
</definition>
"""

ARC_POLYGON = """\
<definition version="0.100.0" type="element">
  <names><name lang="de">Sprung</name></names>
  <description>
    <arc x="-3" y="-3" width="6" height="6" start="270" angle="180" style="line-style:normal;line-weight:normal;filling:none;color:black"/>
    <polygon x1="-10" y1="0" x2="-5" y2="0" x3="0" y3="5" x4="5" y4="0" x5="10" y5="0" closed="false" style="line-style:normal;line-weight:normal;filling:none;color:black"/>
    <terminal name="1" x="0" y="-7" orientation="n"/>
    <terminal name="2" x="0" y="7" orientation="s"/>
  </description>
</definition>
"""

LABELS = """\
<labels>
  <category name="10_allpole">
    <category name="120_cables_wiring"><prefix>W</prefix></category>
    <category name="310_relays_contactors_contacts">
      <category name="01_coils"><prefix>K</prefix></category>
    </category>
    <category name="391_consumers_actuators">
      <category name="10_engines"><prefix>M</prefix></category>
    </category>
  </category>
</labels>
"""


def make_tree(tmp_path: Path) -> tuple[Path, Path]:
    qet = tmp_path / "10_electric"
    (qet / "10_allpole" / "391_consumers_actuators" / "10_engines").mkdir(parents=True)
    (qet / "10_allpole" / "98_graphics").mkdir(parents=True)
    (qet / "10_allpole" / "114_connections").mkdir(parents=True)

    (qet / "qet_labels.xml").write_text(LABELS, encoding="utf-8")
    (qet / "10_allpole" / "391_consumers_actuators" / "10_engines" / "moteur.elmt").write_text(MOTOR, encoding="utf-8")
    (qet / "10_allpole" / "98_graphics" / "frame.elmt").write_text(ZERO_PIN, encoding="utf-8")
    (qet / "10_allpole" / "114_connections" / "jump.elmt").write_text(ARC_POLYGON, encoding="utf-8")
    return qet, qet / "qet_labels.xml"


def test_prefix_inheritance_from_qet_labels(tmp_path: Path):
    labels = tmp_path / "labels.xml"
    labels.write_text(LABELS, encoding="utf-8")
    prefixes = mod.parse_prefix_tree(labels)

    assert mod.prefix_for_category(
        ["10_electric", "10_allpole", "391_consumers_actuators", "10_engines"], prefixes
    ) == "M"
    assert mod.prefix_for_category(
        ["10_electric", "10_allpole", "310_relays_contactors_contacts", "01_coils", "nested"], prefixes
    ) == "K"


def test_internal_prefix_never_leaks_into_visible_value(tmp_path: Path):
    qet, labels = make_tree(tmp_path)
    output = tmp_path / "out.kicad_sym"
    report = tmp_path / "report.json"
    stats = mod.convert_library(qet, labels, ["10_allpole"], output, report)
    data = output.read_text(encoding="utf-8")

    assert stats.converted == 3
    assert '(symbol "Z_Q_10_allpole__391_consumers_actuators__10_engines__moteur"' in data
    assert '(property "Value" "Motor"' in data
    assert '(property "Value" "Z_Q_Motor"' not in data


def test_motor_uses_m_reference_and_preserves_provenance(tmp_path: Path):
    qet, labels = make_tree(tmp_path)
    output = tmp_path / "out.kicad_sym"
    report = tmp_path / "report.json"
    mod.convert_library(qet, labels, ["10_allpole"], output, report)
    data = output.read_text(encoding="utf-8")

    assert '(property "Reference" "M"' in data
    assert '(property "QET_Author" "The QElectroTech team"' in data
    assert 'qelectrotech.org/wiki/doc/elements_license' in data
    assert '(property "QET_Original_Pin_Count" "1"' in data
    assert '10_electric / 10_allpole / 391_consumers_actuators / 10_engines' in data


def test_empty_terminal_number_is_generated_and_recorded(tmp_path: Path):
    qet, labels = make_tree(tmp_path)
    output = tmp_path / "out.kicad_sym"
    report = tmp_path / "report.json"
    stats = mod.convert_library(qet, labels, ["10_allpole"], output, report)
    data = output.read_text(encoding="utf-8")

    assert stats.generated_pin_numbers == 1
    assert '(number "1"' in data
    assert "generated_pin_number" in data


def test_zero_pin_symbol_is_retained_and_not_in_bom(tmp_path: Path):
    qet, labels = make_tree(tmp_path)
    output = tmp_path / "out.kicad_sym"
    report = tmp_path / "report.json"
    stats = mod.convert_library(qet, labels, ["10_allpole"], output, report)
    data = output.read_text(encoding="utf-8")

    assert stats.zero_pin_symbols == 1
    assert "Z_Q_10_allpole__98_graphics__frame" in data
    assert '(property "Reference" "QET"' in data
    assert "reference_prefix_missing:qet_placeholder" in data


def test_arc_is_deliberately_approximated_and_polygon_is_kept(tmp_path: Path):
    qet, labels = make_tree(tmp_path)
    output = tmp_path / "out.kicad_sym"
    report = tmp_path / "report.json"
    mod.convert_library(qet, labels, ["10_allpole"], output, report)
    data = output.read_text(encoding="utf-8")

    assert "arc_approximated" in data
    assert data.count("(polyline (pts") >= 3


def test_report_is_machine_readable_and_complete(tmp_path: Path):
    qet, labels = make_tree(tmp_path)
    output = tmp_path / "out.kicad_sym"
    report = tmp_path / "report.json"
    stats = mod.convert_library(qet, labels, ["10_allpole"], output, report)
    payload = json.loads(report.read_text(encoding="utf-8"))

    assert payload["source_files"] == 3
    assert payload["converted"] == 3
    assert payload["zero_pin_symbols"] == 1
    assert payload["errors"] == []
    assert payload["scopes"] == ["10_allpole"]
    assert stats.converted == stats.source_files


def test_parentheses_are_balanced_for_fixture_output(tmp_path: Path):
    qet, labels = make_tree(tmp_path)
    output = tmp_path / "out.kicad_sym"
    mod.convert_library(qet, labels, ["10_allpole"], output, tmp_path / "report.json")
    data = output.read_text(encoding="utf-8")

    depth = 0
    in_string = False
    escaped = False
    for ch in data:
        if in_string:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_string = False
            continue
        if ch == '"':
            in_string = True
        elif ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            assert depth >= 0
    assert depth == 0


def test_circle_primitive_and_default_closed_polygon_are_supported(tmp_path: Path):
    xml = """\
<definition version="0.100.0" type="element">
  <names><name lang="de">Kreisprüfung</name></names>
  <description>
    <circle x="-5" y="-5" diameter="10" style="line-style:normal;line-weight:normal;filling:none;color:black"/>
    <polygon x1="0" y1="0" x2="10" y2="0" x3="10" y3="10"
             style="line-style:normal;line-weight:normal;filling:none;color:black"/>
  </description>
</definition>
"""
    qet = tmp_path / "10_electric"
    scope = qet / "10_allpole" / "test"
    scope.mkdir(parents=True)
    (qet / "qet_labels.xml").write_text("<labels><category name='10_allpole'/></labels>", encoding="utf-8")
    (scope / "shape.elmt").write_text(xml, encoding="utf-8")
    out = tmp_path / "out.kicad_sym"
    stats = mod.convert_library(qet, qet / "qet_labels.xml", ["10_allpole"], out, tmp_path / "report.json")
    data = out.read_text(encoding="utf-8")

    assert stats.converted == 1
    assert "(circle (center 0 0) (radius 1.27)" in data
    assert "(xy 0 0)" in data
    assert data.count("(xy 0 0)") >= 2


def test_missing_german_name_is_reported_not_silently_hidden(tmp_path: Path):
    xml = """\
<definition version="0.100.0" type="element">
  <names><name lang="en">English only</name></names>
  <description><line x1="0" y1="0" x2="10" y2="0"/></description>
</definition>
"""
    qet = tmp_path / "10_electric"
    scope = qet / "10_allpole" / "test"
    scope.mkdir(parents=True)
    (qet / "qet_labels.xml").write_text("<labels><category name='10_allpole'/></labels>", encoding="utf-8")
    (scope / "english.elmt").write_text(xml, encoding="utf-8")
    out = tmp_path / "out.kicad_sym"
    stats = mod.convert_library(qet, qet / "qet_labels.xml", ["10_allpole"], out, tmp_path / "report.json")
    data = out.read_text(encoding="utf-8")

    assert stats.missing_german_names == 1
    assert "german_name_fallback:en" in data
    assert stats.missing_german_name_paths == ["10_electric/10_allpole/test/english.elmt"]


def test_collection_license_is_explicit(tmp_path: Path):
    qet, labels = make_tree(tmp_path)
    out = tmp_path / "out.kicad_sym"
    mod.convert_library(qet, labels, ["10_allpole"], out, tmp_path / "report.json")
    data = out.read_text(encoding="utf-8")
    assert '(property "QET_Collection_License" "CC-BY-3.0"' in data


def test_non_native_style_and_rounded_rectangle_are_reported(tmp_path: Path):
    xml = """\
<definition version="0.100.0" type="element">
  <names><name lang="de">Stilprüfung</name></names>
  <description>
    <rect x="0" y="0" width="10" height="10" rx="2"
          style="line-style:custom;line-weight:odd;filling:hatch;color:black"/>
  </description>
</definition>
"""
    qet = tmp_path / "10_electric"
    scope = qet / "10_allpole" / "test"
    scope.mkdir(parents=True)
    (qet / "qet_labels.xml").write_text(
        "<labels><category name='10_allpole'/></labels>", encoding="utf-8"
    )
    (scope / "styled.elmt").write_text(xml, encoding="utf-8")
    out = tmp_path / "out.kicad_sym"
    stats = mod.convert_library(
        qet, qet / "qet_labels.xml", ["10_allpole"], out, tmp_path / "report.json"
    )
    data = out.read_text(encoding="utf-8")
    assert "rounded_rectangle_approximated" in data
    assert "line_style_approximated:custom" in data
    assert "line_weight_approximated:odd" in data
    assert "fill_style_approximated:hatch" in data
    assert stats.symbols_with_adjustments == 1
