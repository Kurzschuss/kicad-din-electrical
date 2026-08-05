from pathlib import Path

from tools.z_cockpit import collect_security_status, page_by_id


def test_security_page_is_registered_as_implemented() -> None:
    page = page_by_id("sicherheit")
    assert page.implemented is True
    assert page.label_de == "Sicherheit"


def test_missing_components_are_reported(tmp_path: Path) -> None:
    items = {item.security_id: item for item in collect_security_status(tmp_path)}
    assert items["versionspruefung"].state == "fehlt"
    assert items["entwickler_whitelist"].state == "fehlt"
    assert items["codeowners"].state == "fehlt"
    assert items["ruleset"].state == "fehlt"
    assert items["repository_zustand"].state == "laufzeitpruefung"


def test_existing_components_and_prepared_ruleset(tmp_path: Path) -> None:
    paths = (
        tmp_path / "tools" / "check_repository_version.py",
        tmp_path / "config" / "authorized_developers.json",
        tmp_path / ".github" / "CODEOWNERS",
        tmp_path / ".github" / "rulesets" / "main-branch-protection-v1.json",
    )
    for path in paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("test", encoding="utf-8")

    items = {item.security_id: item for item in collect_security_status(tmp_path)}
    assert items["versionspruefung"].state == "vorhanden"
    assert items["entwickler_whitelist"].state == "vorhanden"
    assert items["codeowners"].state == "vorhanden"
    assert items["ruleset"].state == "vorbereitet"
    assert "noch nicht bestätigt" in items["ruleset"].detail_de
