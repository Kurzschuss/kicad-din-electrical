import pytest

from tools.z_cockpit.security_page import (
    security_page_html,
    security_state_label,
    security_table_html,
)
from tools.z_cockpit.security_status import SecurityItem


def sample_items() -> tuple[SecurityItem, ...]:
    return (
        SecurityItem("version", "Versionsprüfung", "vorhanden", "Prüfung vorhanden"),
        SecurityItem("repository", "Repository-Zustand", "laufzeitpruefung", "Wird zur Laufzeit geprüft"),
        SecurityItem("ruleset", "GitHub-Ruleset", "vorbereitet", "Noch nicht aktiviert"),
        SecurityItem("codeowners", "CODEOWNERS", "fehlt", "Datei fehlt"),
    )


def test_security_state_labels_are_german():
    assert security_state_label("vorhanden") == "Vorhanden"
    assert security_state_label("fehlt") == "Fehlt"
    assert security_state_label("vorbereitet") == "Vorbereitet"
    assert security_state_label("laufzeitpruefung") == "Laufzeitprüfung"


def test_unknown_security_state_is_rejected():
    with pytest.raises(ValueError, match="Unbekannter Sicherheitszustand"):
        security_state_label("aktiv")


def test_security_table_contains_all_states_and_details():
    html = security_table_html(sample_items())
    assert 'data-security="version"' in html
    assert 'data-state="laufzeitpruefung"' in html
    assert "Versionsprüfung" in html
    assert "Laufzeitprüfung" in html
    assert "Vorbereitet" in html
    assert "Noch nicht aktiviert" in html
    assert "Fehlt" in html


def test_security_page_uses_library_style_heading_and_warns_about_ruleset():
    html = security_page_html(sample_items())
    assert 'id="page-sicherheit"' in html
    assert '<h2 class="cockpit-page-title">Sicherheit ' in html
    assert 'class="cockpit-page-description"' in html
    assert "Lokal prüfbare Schutzmechanismen" in html
    assert "nicht als bestätigt dargestellt" in html
    assert "bedeutet nicht" in html
    assert "bereits aktiviert" in html
    assert "<h2>Sicherheit</h2><p>" not in html