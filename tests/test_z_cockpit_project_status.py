from pathlib import Path

from tools.z_cockpit import collect_project_status


def test_project_status_contains_expected_german_sections(tmp_path: Path) -> None:
    statuses = collect_project_status(tmp_path)
    assert [item.status_id for item in statuses] == [
        "geraetekatalog",
        "symbole",
        "footprints",
        "dokumentation",
        "ruleset",
    ]
    assert [item.label_de for item in statuses] == [
        "Gerätekatalog",
        "Symbolbibliothek",
        "Footprints",
        "Dokumentation",
        "Repository-Schutz",
    ]
    assert all(item.available is False for item in statuses)


def test_project_status_detects_existing_project_parts(tmp_path: Path) -> None:
    paths = (
        tmp_path / "data" / "devices",
        tmp_path / "symbols" / "Z_MCB.kicad_sym",
        tmp_path / "footprints" / "Z_DIN_Module_18mm.pretty",
        tmp_path / "docs" / "03_Developer" / "Z_COCKPIT.md",
        tmp_path / ".github" / "rulesets" / "main-branch-protection-v1.json",
    )
    for path in paths:
        if path.suffix:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("test", encoding="utf-8")
        else:
            path.mkdir(parents=True, exist_ok=True)

    statuses = collect_project_status(tmp_path)
    assert all(item.available is True for item in statuses)
    ruleset = next(item for item in statuses if item.status_id == "ruleset")
    assert "noch nicht aktiviert" in ruleset.detail_de
