from tools.generate_z_cockpit import (
    cockpit_devices,
    cockpit_summary,
    navigation_html,
    placeholder_pages_html,
    project_status_html,
    render_html,
)


def test_cockpit_uses_catalog_devices():
    devices = cockpit_devices()
    assert devices
    assert any(item["id"] == "generic.mcb-1p-b16-template" for item in devices)
    assert all(item["family"] for item in devices)
    assert all(item["symbol"] for item in devices)
    assert all(item["symbol_preview_url"] for item in devices)
    assert all(isinstance(item["symbol_preview_available"], bool) for item in devices)


def test_generic_manufacturer_is_shown_in_german():
    device = next(item for item in cockpit_devices() if item["id"] == "generic.mcb-1p-b16-template")
    assert device["manufacturer"] == "Herstellerneutral"
    assert device["name"] == "Leitungsschutzschalter"
    assert device["current"] == "16 A"
    assert device["curve"] == "B"
    assert device["symbol_preview_url"] == "symbol-previews/Z_MCB/MCB.svg"
    assert device["symbol_preview_available"] is True


def test_summary_uses_real_catalog_values():
    devices = cockpit_devices()
    summary = cockpit_summary(devices)
    assert summary["devices"] == len(devices)
    assert summary["families"] >= 1
    assert summary["manufacturers"] >= 1
    assert 0 <= summary["checked"] <= summary["devices"]


def test_navigation_is_generated_from_registered_pages():
    navigation = navigation_html()
    assert 'data-page="start"' in navigation
    assert 'data-page="geraete"' in navigation
    assert "Bibliotheken" in navigation
    assert "Qualität" in navigation
    assert "Sicherheit" in navigation


def test_project_status_cards_distinguish_present_and_prepared_components():
    cards = project_status_html()
    assert 'data-status="geraetekatalog"' in cards
    assert 'data-status="symbole"' in cards
    assert 'data-status="footprints"' in cards
    assert 'data-status="dokumentation"' in cards
    assert 'data-status="ruleset"' in cards
    assert "Vorhanden" in cards
    assert "Vorbereitet" in cards
    assert "noch nicht aktiviert" in cards


def test_security_is_not_generated_as_placeholder():
    placeholders = placeholder_pages_html()
    assert 'id="page-sicherheit"' not in placeholders
    assert 'id="page-diagnose"' in placeholders


def test_rendered_cockpit_contains_navigation_dashboard_navigator_security_preview_and_catalog_data():
    html = render_html(cockpit_devices())
    assert 'lang="de"' in html
    assert "Projektstatus" in html
    assert "Gerätefamilien" in html
    assert "Geprüfte Geräte" in html
    assert "Fortschritt bis Version 1.0" in html
    assert "Gesamtfortschritt" in html
    assert "Bibliotheken" in html
    assert "Z_Cockpit" in html
    assert "Repository-Sicherheit" in html
    assert "Nächste Aufgaben" in html
    assert "Geplant" in html
    assert "Blockiert" in html
    assert "Entwicklungsnavigator" in html
    assert "Als Nächstes empfohlen" in html
    assert "Symbolvorschau anbinden" in html
    assert "Später nach Freigabe" in html
    assert "GitHub-Ruleset gemeinsam prüfen und aktivieren" in html
    assert "Projektbestandteile" in html
    assert 'class="status-card prepared" data-status="ruleset"' in html
    assert 'id="page-geraete"' in html
    assert 'id="page-sicherheit"' in html
    assert 'class="security-table"' in html
    assert 'data-security="versionspruefung"' in html
    assert 'data-security="entwickler_whitelist"' in html
    assert 'data-security="codeowners"' in html
    assert 'data-security="repository_zustand"' in html
    assert 'data-security="ruleset"' in html
    assert "Laufzeitprüfung" in html
    assert "Eine vorhandene Ruleset-Vorlage bedeutet nicht" in html
    assert 'id="page-diagnose"' in html
    assert "Dieser Bereich befindet sich im Aufbau." in html
    assert "Gerätefamilie" in html
    assert "Hersteller" in html
    assert "Charakteristik" in html
    assert "generic.mcb-1p-b16-template" in html
    assert '"symbol_preview_url": "symbol-previews/Z_MCB/MCB.svg"' in html
    assert '"symbol_preview_available": true' in html
    assert 'alt="Symbolvorschau ${item.symbol}"' in html
    assert "Für dieses Symbol ist keine Vorschau verfügbar." in html
    assert "Technische SVG-Schnellansicht" in html
    assert "Datenquellen: Gerätekatalog und project_state.yaml" in html
    assert "Z_Cockpit 0.8" in html
