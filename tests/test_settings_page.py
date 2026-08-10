from tools.z_cockpit.project_model import ProjectState
from tools.z_cockpit.settings_page import (
    CockpitSettingsSnapshot,
    collect_settings,
    settings_page_html,
)


def test_collect_settings_uses_project_state_as_source_of_truth():
    project = ProjectState(
        name="projekt-test",
        display_name="Projekt Test",
        language="de",
        phase="Entwicklung",
        target_release="2.0",
        milestones=(),
    )

    settings = collect_settings(project)

    assert settings.project_name == "projekt-test"
    assert settings.display_name == "Projekt Test"
    assert settings.language == "de"
    assert settings.phase == "Entwicklung"
    assert settings.target_release == "2.0"
    assert settings.project_state_path == "project_state.yaml"
    assert settings.device_catalog_path == "data/devices/"
    assert settings.cockpit_output_path == "docs/site/z-cockpit.html"


def test_settings_page_contains_read_only_project_values_and_local_ui_controls():
    html = settings_page_html(
        CockpitSettingsSnapshot(
            project_name="kicad-din-electrical",
            display_name="KiCad DIN Electrical Suite",
            language="de",
            phase="Entwicklung",
            target_release="1.0",
        )
    )

    assert 'id="page-einstellungen"' in html
    assert "Projektwerte werden aus den vorhandenen Repository-Quellen gelesen" in html
    assert "KiCad DIN Electrical Suite" in html
    assert "project_state.yaml" in html
    assert "data/devices/" in html
    assert "symbols/" in html
    assert "footprints/" in html
    assert "docs/site/z-cockpit.html" in html
    assert 'id="setting-theme"' in html
    assert 'id="setting-density"' in html
    assert 'id="setting-remember-page"' in html
    assert 'id="setting-developer-details"' in html
    assert 'id="settings-reset"' in html
    assert "Browser localStorage" in html
    assert "Diese Optionen ändern keine Repositorydateien" in html


def test_settings_page_persists_only_browser_preferences():
    html = settings_page_html(
        CockpitSettingsSnapshot(
            project_name="projekt",
            display_name="Projekt",
            language="de",
            phase="Entwicklung",
            target_release="1.0",
        )
    )

    assert 'const KEY="z-cockpit.settings.v1"' in html
    assert "localStorage.getItem(KEY)" in html
    assert "localStorage.setItem(KEY" in html
    assert "localStorage.removeItem(KEY)" in html
    assert "cockpit-compact" in html
    assert "cockpitTheme" in html
    assert "Zuletzt geöffneten Cockpit-Bereich" in html


def test_settings_page_escapes_repository_values():
    html = settings_page_html(
        CockpitSettingsSnapshot(
            project_name="<projekt>",
            display_name="<script>alert(1)</script>",
            language="de&test",
            phase="<Phase>",
            target_release="1.0<beta>",
        )
    )

    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in html
    assert "&lt;projekt&gt;" in html
    assert "de&amp;test" in html
    assert "1.0&lt;beta&gt;" in html
