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
    assert all("footprint_preview_status" in item for item in devices)
    assert all(isinstance(item["footprint_preview_available"], bool) for item in devices)
    assert all("three_d_preview_status" in item for item in devices)
    assert all(isinstance(item["three_d_preview_available"], bool) for item in devices)
    assert all(isinstance(item["model"], bool) for item in devices)
    assert all("rcd_type" in item for item in devices)
    assert all("residual_current" in item for item in devices)


def test_generic_manufacturer_is_shown_in_german():
    device = next(item for item in cockpit_devices() if item["id"] == "generic.mcb-1p-b16-template")
    assert device["manufacturer"] == "Herstellerneutral"
    assert device["name"] == "Leitungsschutzschalter"
    assert device["current"] == "16 A"
    assert device["curve"] == "B"
    assert device["symbol_preview_url"] == "symbol-previews/Z_MCB/MCB.svg"
    assert device["symbol_preview_available"] is True
    assert device["footprint"]
    assert device["footprint_preview_status"] in {"Kontur", "Platzhalter", "Fehlt", "Nicht zugeordnet"}
    assert device["three_d_preview_status"] in {
        "Modell",
        "Modellreferenz fehlt",
        "Hüllkörper",
        "Fehlt",
        "Nicht zugeordnet",
    }


def test_rcd_values_are_exposed_for_cockpit_filtering():
    device = next(
        item
        for item in cockpit_devices()
        if item["id"] == "generic.rcd-2p-b-bplus-template-series.b40-30ma"
    )
    assert device["rcd_type"] == "B"
    assert device["residual_current"] == "30 mA"
    assert device["current"] == "40 A"
    assert device["curve"] == "–"


def test_summary_uses_real_catalog_values():
    devices = cockpit_devices()
    summary = cockpit_summary(devices)
    assert summary["devices"] == len(devices)
    assert summary["families"] >= 1
    assert summary["manufacturers"] >= 1
    assert 0 <= summary["checked"] <= summary["devices"]
    assert 0 <= summary["models"] <= summary["devices"]
    assert 0 <= summary["three_d_previews"] <= summary["devices"]


def test_navigation_is_generated_from_registered_pages():
    navigation = navigation_html()
    assert 'data-page="start"' in navigation
    assert 'data-page="geraete"' in navigation
    assert 'data-page="bibliotheken"' in navigation
    assert 'data-page="hersteller"' in navigation
    assert 'data-page="diagnose"' in navigation
    assert 'data-page="benutzer"' in navigation
    assert 'data-page="berechtigungen"' in navigation
    assert 'data-page="fehlerbericht"' in navigation
    assert 'data-page="dokumentation"' in navigation
    assert 'data-page="einstellungen"' in navigation
    assert "Bibliotheken" in navigation
    assert "Hersteller" in navigation
    assert "Qualität" in navigation
    assert "Diagnose" in navigation
    assert "Benutzer" in navigation
    assert "Berechtigungen" in navigation
    assert "Fehler melden" in navigation
    assert "Dokumentation" in navigation
    assert "Einstellungen" in navigation
    assert "Sicherheit" in navigation
    assert "– geplant" not in navigation
    assert 'data-page="bibliotheken" title="Symbole, Footprints und Modelle">Bibliotheken</button>' in navigation
    assert 'data-page="hersteller" title="Hersteller, Serien und Katalogzuordnungen">Hersteller</button>' in navigation
    assert 'data-page="qualitaet" title="Tests, Regeln und Qualitätsberichte">Qualität</button>' in navigation
    assert 'data-page="diagnose" title="Fehler, Warnungen und Prüfdetails">Diagnose</button>' in navigation
    assert 'data-page="benutzer" title="ProjectOS-Benutzer, Rollen, Rechte und Lifecycle">Benutzer</button>' in navigation
    assert 'data-page="berechtigungen" title="ProjectOS-Whitelist, Blacklist, Ausnahmen und Entwicklerfreigaben">Berechtigungen</button>' in navigation
    assert 'data-page="fehlerbericht" title="Strukturierter Fehlerbericht und GitHub-Issue-Vorbereitung">Fehler melden</button>' in navigation
    assert 'data-page="dokumentation" title="Projekt- und Entwicklerdokumentation">Dokumentation</button>' in navigation
    assert 'data-page="einstellungen" title="Sprache, Pfade und Entwickleroptionen">Einstellungen</button>' in navigation


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


def test_all_registered_pages_are_implemented_without_placeholders():
    assert placeholder_pages_html() == ""


def test_rendered_cockpit_contains_navigation_dashboard_quality_security_previews_and_catalog_data():
    html = render_html(cockpit_devices())
    assert 'lang="de"' in html
    assert "Projektstatus" in html
    assert "Gerätefamilien" in html
    assert "Geprüfte Geräte" in html
    assert "3D-Modelle" in html
    assert "3D-Vorschauen" in html
    assert "Fortschritt bis Version 1.0" in html
    assert "Gesamtfortschritt" in html
    assert "Bibliotheken" in html
    assert 'id="page-bibliotheken"' in html
    assert 'class="cards library-summary"' not in html
    assert 'class="library-page-title"' in html
    assert 'id="library-filter-name"' in html
    assert 'id="library-filter-preview"' in html
    assert 'id="library-filter-three-d"' in html
    assert 'class="library-card library-inline-detail"' in html
    assert 'class="library-table"' in html
    assert "Gerätezuordnungen" in html
    assert "Vorschaupaare" in html
    assert html.count('id="page-bibliotheken"') == 1
    assert 'id="page-hersteller"' in html
    assert html.count('id="page-hersteller"') == 1
    assert 'id="manufacturer-overview"' in html
    assert 'id="manufacturer-page-filter-name"' in html
    assert 'class="manufacturer-inspector"' in html
    assert "Herstellerneutral" in html
    assert "Read-only Übersicht aus dem technischen Gerätekatalog" in html
    assert 'id="page-qualitaet"' in html
    assert html.count('id="page-qualitaet"') == 1
    assert "Bibliotheksgesundheit" in html
    assert "Projektkonsistenz" in html
    assert 'data-check="PRJ-001"' in html
    assert 'class="cards project-validation-summary"' in html
    assert 'class="cards quality-summary"' in html
    assert 'class="quality-card"' in html
    assert 'role="progressbar"' in html
    assert "Gesundheitswert" in html
    assert "Warnungen" in html
    assert "Fehler" in html
    assert 'id="page-diagnose"' in html
    assert html.count('id="page-diagnose"') == 1
    assert 'id="diagnostic-overview"' in html
    assert 'id="diagnostic-filter-severity"' in html
    assert 'id="diagnostic-filter-source"' in html
    assert 'id="diagnostic-filter-area"' in html
    assert 'class="diagnostic-inspector"' in html
    assert "Arbeitsliste aus ProjectOS-Projektvalidator und repositoryweiter Projektanalyse" in html
    assert "Laufzeit-Wissensgraphdiagnosen" in html
    assert 'id="page-benutzer"' in html
    assert html.count('id="page-benutzer"') == 1
    assert 'id="user-management-overview"' in html
    assert 'id="user-management-filter-search"' in html
    assert 'id="user-management-filter-status"' in html
    assert 'id="user-management-filter-role"' in html
    assert 'id="user-management-filter-permission"' in html
    assert 'class="user-management-inspector"' in html
    assert "Keine ProjectOS-Benutzer geladen" in html
    assert "--project-bundle" in html
    assert 'id="page-berechtigungen"' in html
    assert html.count('id="page-berechtigungen"') == 1
    assert 'id="permissions-overview"' in html
    assert 'id="permissions-filter-search"' in html
    assert 'id="permissions-filter-user"' in html
    assert 'id="permissions-filter-source"' in html
    assert 'id="permissions-filter-effect"' in html
    assert 'id="permissions-filter-status"' in html
    assert "Repository-Entwickler-Whitelist" in html
    assert "config/authorized_developers.json" in html
    assert "ProjectOSUserManagementChangeService" in html
    assert "Das statische Cockpit schreibt keine Rechte" in html
    assert 'id="page-fehlerbericht"' in html
    assert html.count('id="page-fehlerbericht"') == 1
    assert 'id="issue-report-category"' in html
    assert 'id="issue-report-title"' in html
    assert 'id="issue-report-description"' in html
    assert 'id="issue-report-preview"' in html
    assert 'id="issue-confirm-review"' in html
    assert 'id="issue-report-github" disabled' in html
    assert "GitHub-Issue vorbereiten" in html
    assert "Benutzer-/Berechtigungsbestände" in html
    assert "bug_report.yml" in html
    assert 'id="page-dokumentation"' in html
    assert html.count('id="page-dokumentation"') == 1
    assert 'id="documentation-overview"' in html
    assert 'id="documentation-filter-search"' in html
    assert 'id="documentation-filter-category"' in html
    assert 'class="documentation-inspector"' in html
    assert "Durchsuchbarer Index der vorhandenen Markdown-Dokumentation" in html
    assert "keine zweite Dokumentationsdatenbank" in html
    assert "docs/README.md" in html
    assert 'id="page-einstellungen"' in html
    assert html.count('id="page-einstellungen"') == 1
    assert 'id="setting-theme"' in html
    assert 'id="setting-density"' in html
    assert 'id="setting-remember-page"' in html
    assert 'id="setting-developer-details"' in html
    assert 'id="settings-reset"' in html
    assert "Projektwerte aus Repository-Quellen" in html
    assert "Diese Optionen ändern keine Repositorydateien" in html
    assert "3dmodels/Z_3DModell.3dshapes/" in html
    assert "z-cockpit.settings.v1" in html
    assert 'class="cockpit-page-title"' in html
    assert 'class="cockpit-page-description"' in html
    assert "function compactPageHeadings()" in html
    assert "Z_Cockpit" in html
    assert "Repository-Sicherheit" in html
    assert "Nächste Aufgaben" in html
    assert "Keine ausführbare Aufgabe offen." in html
    assert "Blockiert" in html
    assert "Entwicklungsnavigator" in html
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
    assert "Dieser Bereich befindet sich im Aufbau." not in html
    assert "Gerätefamilie" in html
    assert "Hersteller" in html
    assert "Charakteristik" in html
    assert "RCD-Typ" in html
    assert "IΔn" in html
    assert 'id="rcd_type"' in html
    assert 'id="residual_current"' in html
    assert "generic.mcb-1p-b16-template" in html
    assert "generic.rcd-2p-b-bplus-template-series.b40-30ma" in html
    assert '\"rcd_type\": \"B\"' in html
    assert '\"residual_current\": \"30 mA\"' in html
    assert '\"symbol_preview_url\": \"symbol-previews/Z_MCB/MCB.svg\"' in html
    assert '\"symbol_preview_available\": true' in html
    assert '\"footprint_preview_status\"' in html
    assert '\"three_d_preview_status\"' in html
    assert '\"three_d_preview_available\"' in html
    assert 'id="symbol-preview"' in html
    assert 'id="footprint-preview"' in html
    assert 'id="three-d-preview"' in html
    assert 'alt="Symbolvorschau ${item.symbol}"' in html
    assert 'alt="Footprintvorschau ${item.footprint}"' in html
    assert 'alt="3D-Vorschau ${item.footprint}"' in html
    assert "Für dieses Symbol ist keine Vorschau verfügbar." in html
    assert "Für diesen Footprint ist keine Vorschau verfügbar." in html
    assert "Footprint vorhanden, aber noch ohne darstellbare Geometrie." in html
    assert "Technische SVG-Schnellansicht" in html
    assert "Technische Hüllkörper-Vorschau" in html
    assert "Datenquellen: Gerätekatalog, KiCad-Bibliotheken, 3D-Modellreferenzen, project_state.yaml und ProjectOS" in html
    assert "Z_Cockpit 1.2" in html
