from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "tools" / "audit_qet_source.py"
sys.path.insert(0, str(MODULE_PATH.parent))
SPEC = importlib.util.spec_from_file_location("audit_qet_source", MODULE_PATH)
assert SPEC and SPEC.loader
mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = mod
SPEC.loader.exec_module(mod)


def test_audit_reports_only_missing_german_names_and_zero_pin_count(tmp_path: Path):
    qet = tmp_path / "10_electric"
    scope = qet / "10_allpole" / "test"
    scope.mkdir(parents=True)
    (scope / "german.elmt").write_text(
        '<definition><names><name lang="de">Motor</name><name lang="en">Motor</name></names>'
        '<description><terminal name="1"/></description></definition>',
        encoding="utf-8",
    )
    (scope / "english.elmt").write_text(
        '<definition><names><name lang="en">Push button</name><name lang="fr">Bouton poussoir</name></names>'
        '<description><terminal name="1"/><terminal name="2"/></description></definition>',
        encoding="utf-8",
    )
    (scope / "graphic.elmt").write_text(
        '<definition><names><name lang="de">Grafik</name><name lang="en">Graphic</name></names>'
        '<description><line x1="0" y1="0" x2="10" y2="0"/></description></definition>',
        encoding="utf-8",
    )

    report = mod.audit(qet, ["10_allpole"])

    assert report["source_files"] == 3
    assert report["zero_pin_symbols"] == 1
    assert report["missing_german_names"] == 1
    assert report["parse_errors"] == []
    assert report["items"] == [
        {
            "path": "10_electric/10_allpole/test/english.elmt",
            "category": "10_electric / 10_allpole / test",
            "filename": "english.elmt",
            "names": {"en": "Push button", "fr": "Bouton poussoir"},
            "terminal_count": 2,
        }
    ]


def test_audit_uses_actual_collection_root_for_paths_and_categories(tmp_path: Path):
    qet = tmp_path / "20_logic"
    scope = qet / "2020_flow_chart" / "test"
    scope.mkdir(parents=True)
    (scope / "english.elmt").write_text(
        '<definition><names><name lang="en">Decision</name></names><description/></definition>',
        encoding="utf-8",
    )

    report = mod.audit(qet, ["2020_flow_chart"])

    assert report["items"] == [
        {
            "path": "20_logic/2020_flow_chart/test/english.elmt",
            "category": "20_logic / 2020_flow_chart / test",
            "filename": "english.elmt",
            "names": {"en": "Decision"},
            "terminal_count": 0,
        }
    ]


def test_audit_reports_parse_errors_without_stopping(tmp_path: Path):
    qet = tmp_path / "10_electric"
    scope = qet / "10_allpole" / "test"
    scope.mkdir(parents=True)
    (scope / "bad.elmt").write_text("<definition>", encoding="utf-8")
    (scope / "ok.elmt").write_text(
        '<definition><names><name lang="en">Only English</name></names><description/></definition>',
        encoding="utf-8",
    )

    report = mod.audit(qet, ["10_allpole"])

    assert report["source_files"] == 2
    assert report["zero_pin_symbols"] == 1
    assert report["missing_german_names"] == 1
    assert len(report["parse_errors"]) == 1
    assert report["parse_errors"][0]["path"].endswith("bad.elmt")
