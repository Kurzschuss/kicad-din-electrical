from pathlib import Path

from tools.generate_z_cockpit import cockpit_devices, render_html
from tools.z_cockpit.editor_links import editor_links_html


ROOT = Path(__file__).resolve().parents[1]


def test_editor_links_cover_device_and_library_inspectors_without_rebuilding_layout():
    html = editor_links_html()

    assert 'kicad-z://${kind}' in html
    assert "Symbol-Editor öffnen" in html
    assert "Footprint direkt öffnen" in html
    assert '#devices tbody tr' in html
    assert '.library-symbol-row' in html
    assert '#library-symbol-inspector .library-inspector-fixed' in html
    assert 'data-kicad-editor-actions="1"' in html
    assert "library-device-id-scroll" not in html
    assert "eval(" not in html
    assert "window.open(" not in html


def test_generated_cockpit_contains_local_editor_integration():
    html = render_html(cockpit_devices())

    assert "Symbol-Editor öffnen" in html
    assert "Footprint direkt öffnen" in html
    assert "Lokale Windows-Integration" in html
    assert "kicad-z://${kind}" in html


def test_protocol_registration_is_per_user_and_points_to_fixed_handler():
    script = (ROOT / "tools" / "windows" / "register_z_kicad_protocol.ps1").read_text(encoding="utf-8")

    assert "HKCU:\\Software\\Classes\\kicad-z" in script
    assert "HKLM:" not in script
    assert "open_kicad_from_cockpit.ps1" in script
    assert "URL Protocol" in script
    assert '"%1"' in script


def test_protocol_handler_accepts_only_repository_identifiers_and_known_actions():
    script = (ROOT / "tools" / "windows" / "open_kicad_from_cockpit.ps1").read_text(encoding="utf-8")

    assert "if ($parsed.Scheme -ne 'kicad-z')" in script
    assert "'footprint' {" in script
    assert "'symbol' {" in script
    assert "'^[A-Za-z0-9_.+-]+$'" in script
    assert "footprints\\{0}.pretty\\{0}.kicad_mod" in script
    assert "symbols\\{0}.kicad_sym" in script
    assert "Select-String -LiteralPath $libraryFile -SimpleMatch $needle -Quiet" in script
    assert "Invoke-Expression" not in script
    assert "cmd /c" not in script.lower()


def test_footprint_uses_supported_fpedit_file_open_and_symbol_uses_manager_hotkey():
    script = (ROOT / "tools" / "windows" / "open_kicad_from_cockpit.ps1").read_text(encoding="utf-8")

    assert "-ArgumentList @('-f', 'fpedit'" in script
    assert "Set-Clipboard -Value $Reference" in script
    assert "$shell.SendKeys('^l')" in script


def test_windows_cockpit_launcher_registers_editor_protocol_nonblocking():
    launcher = (ROOT / "tools" / "windows" / "open_z_cockpit.bat").read_text(encoding="utf-8")

    assert "register_z_kicad_protocol.ps1" in launcher
    assert "KiCad-Editorlinks konnten nicht registriert werden" in launcher
    assert "Das Z_Cockpit wird trotzdem geoeffnet" in launcher
