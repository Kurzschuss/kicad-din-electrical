from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))

import qet_xml

SPEC = importlib.util.spec_from_file_location(
    "convert_qet_to_kicad_checked_legacy", TOOLS / "convert_qet_to_kicad_checked.py"
)
assert SPEC and SPEC.loader
checked = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = checked
SPEC.loader.exec_module(checked)


def test_invalid_xml10_numeric_reference_is_replaced_not_guessed():
    source = '<definition><names><name lang="ca">Unitat xPx &#11;erge</name></names></definition>'
    sanitized, codes = qet_xml.sanitize_invalid_numeric_references(source)
    assert codes == [11]
    assert "Unitat xPx �erge" in sanitized
    assert "&#11;" not in sanitized


def test_valid_xml_numeric_reference_is_unchanged():
    source = '<definition><names><name lang="en">Line&#10;Break</name></names></definition>'
    sanitized, codes = qet_xml.sanitize_invalid_numeric_references(source)
    assert sanitized == source
    assert codes == []


def test_unclosed_name_before_sibling_is_closed_without_inventing_text():
    import xml.etree.ElementTree as ET

    source = (
        '<definition><names>'
        '<name lang="ca">Màquina, símbol general:'
        '<name lang="cs">Stroj, všeobecná značka</name>'
        '<name lang="de">Maschine, allgemein</name>'
        '</names></definition>'
    )
    sanitized, inserted = qet_xml.sanitize_unclosed_name_siblings(source)
    root = ET.fromstring(sanitized)
    names = {node.get("lang"): (node.text or "") for node in root.find("names").findall("name")}

    assert inserted == 1
    assert names["ca"] == "Màquina, símbol general:"
    assert names["cs"] == "Stroj, všeobecná značka"
    assert names["de"] == "Maschine, allgemein"


def test_valid_sibling_names_are_not_changed():
    source = (
        '<definition><names>'
        '<name lang="de">Maschine</name>'
        '<name lang="en">Machine</name>'
        '</names></definition>'
    )
    sanitized, inserted = qet_xml.sanitize_unclosed_name_siblings(source)
    assert sanitized == source
    assert inserted == 0


def test_legacy_input_label_maps_to_reference_without_placeholder():
    import xml.etree.ElementTree as ET

    node = ET.fromstring('<input rotate="true" text="?U?" tagg="label" x="77" y="182.5" size="9"/>')
    adjustments: set[str] = set()
    drawing = checked.graphics(node, adjustments, {})
    assert drawing == []
    assert "input_label_mapped_to_reference" in adjustments

    root = ET.fromstring(
        '<definition><description><input text="?U?" tagg="label" x="0" y="0"/></description></definition>'
    )
    assert checked.explicit_label(root, root.find("description")) == ""


def test_legacy_free_input_is_preserved_as_static_text():
    import xml.etree.ElementTree as ET

    node = ET.fromstring(
        '<input rotate="true" text="__-__-__-__-__-__" tagg="none" x="-2" y="158.5" size="6"/>'
    )
    adjustments: set[str] = set()
    drawing = checked.graphics(node, adjustments, {})
    assert len(drawing) == 1
    assert "__-__-__-__-__-__" in drawing[0]
    assert "input_staticized:none" in adjustments


def test_full_conversion_records_sanitized_source(tmp_path: Path):
    qet = tmp_path / "10_electric"
    scope = qet / "20_manufacturers_articles" / "vendor"
    scope.mkdir(parents=True)
    (qet / "qet_labels.xml").write_text(
        '<labels><category name="20_manufacturers_articles"><category name="vendor"/></category></labels>',
        encoding="utf-8",
    )
    (scope / "legacy.elmt").write_text(
        '<definition><names><name lang="en">Legacy &#11; name</name></names><description>'
        '<input text="?U?" tagg="label" x="0" y="0" size="9"/>'
        '<input text="editable" tagg="none" x="1" y="2" size="6"/>'
        '<terminal x="0" y="0" orientation="n"/>'
        '</description></definition>',
        encoding="utf-8",
    )

    checked.install()
    output = tmp_path / "out.kicad_sym"
    report = tmp_path / "report.json"
    stats = checked.core.convert_library(
        qet, qet / "qet_labels.xml", ["20_manufacturers_articles"], output, report
    )
    data = output.read_text(encoding="utf-8")

    assert stats.converted == 1
    assert stats.errors == []
    assert "invalid_xml_char_reference_sanitized" in data
    assert "input_label_mapped_to_reference" in data
    assert "input_staticized:none" in data
    assert '(property "Reference" "QET"' in data
    assert '?U?' not in data


def test_full_conversion_records_missing_name_end_tag_sanitation(tmp_path: Path):
    qet = tmp_path / "10_electric"
    scope = qet / "91_en_60617" / "en_60617_06"
    scope.mkdir(parents=True)
    (qet / "qet_labels.xml").write_text(
        '<labels><category name="91_en_60617"><category name="en_60617_06"/></category></labels>',
        encoding="utf-8",
    )
    (scope / "machine.elmt").write_text(
        '<definition><names>'
        '<name lang="ca">Màquina, símbol general:'
        '<name lang="de">Maschine, allgemein</name>'
        '<name lang="en">Machine, general</name>'
        '</names><description><ellipse x="-10" y="-10" width="20" height="20"/></description></definition>',
        encoding="utf-8",
    )

    checked.install()
    output = tmp_path / "out.kicad_sym"
    report = tmp_path / "report.json"
    stats = checked.core.convert_library(
        qet, qet / "qet_labels.xml", ["91_en_60617"], output, report
    )
    data = output.read_text(encoding="utf-8")

    assert stats.converted == 1
    assert stats.errors == []
    assert "missing_name_end_tag_sanitized" in data
    assert '(property "Value" "Maschine, allgemein"' in data
