from __future__ import annotations

import sys
import xml.etree.ElementTree as ET
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))

import qet_xml


def test_literal_less_than_inside_qet_name_is_escaped_and_preserved_as_text():
    source = (
        '<definition><names>'
        '<name lang="ca">Calentador-acumulador d\'aigua<</name>'
        '<name lang="es">Calentador-acum. agua</name>'
        '</names><description><line x1="0" y1="0" x2="1" y2="1"/></description></definition>'
    )

    sanitized, info = qet_xml.sanitize_qet_xml(source)
    root = ET.fromstring(sanitized)

    assert root.find("names/name").text == "Calentador-acumulador d'aigua<"
    assert info.escaped_name_literal_lt == 1
    assert "literal_lt_in_name_text_sanitized" in info.markers
    assert '<description><line x1="0" y1="0" x2="1" y2="1" /></description>' in ET.tostring(root, encoding="unicode")


def test_valid_name_text_is_unchanged():
    source = '<definition><names><name lang="de">Wärmetauscher</name></names></definition>'

    sanitized, info = qet_xml.sanitize_qet_xml(source)

    assert sanitized == source
    assert info.changed is False
    assert info.escaped_name_literal_lt == 0
    assert info.markers == []


def test_name_sibling_repair_runs_before_literal_less_than_repair():
    source = (
        '<definition><names>'
        '<name lang="de">Erster Name'
        '<name lang="en">Second<</name>'
        '</names></definition>'
    )

    sanitized, info = qet_xml.sanitize_qet_xml(source)
    root = ET.fromstring(sanitized)
    names = root.findall("names/name")

    assert [node.text for node in names] == ["Erster Name", "Second<"]
    assert info.inserted_name_end_tags == 1
    assert info.escaped_name_literal_lt == 1
    assert info.markers == [
        "missing_name_end_tag_sanitized",
        "literal_lt_in_name_text_sanitized",
    ]
