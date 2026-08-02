from pathlib import Path

from tools.validate_device_catalog import load_device, validate_catalog, validate_device


def make_symbol(root: Path) -> None:
    root.mkdir(parents=True)
    (root / "Z_Test.kicad_sym").write_text(
        '(kicad_symbol_lib\n  (symbol "Test")\n)\n', encoding="utf-8"
    )


def valid_device() -> dict[str, object]:
    return {
        "id": "generic.test",
        "manufacturer": "Generic",
        "series": "Template",
        "part_number": "TEST-1",
        "device_type": "Testgerät",
        "function_group": "Test",
        "symbol": "Z_Test:Test",
        "footprint_policy": "optional",
        "source_status": "template",
    }


def test_loads_json_compatible_yaml(tmp_path: Path):
    path = tmp_path / "device.yaml"
    path.write_text('{"id": "generic.test"}\n', encoding="utf-8")
    assert load_device(path)["id"] == "generic.test"


def test_valid_device_without_footprint_is_allowed(tmp_path: Path):
    symbols = tmp_path / "symbols"
    make_symbol(symbols)
    assert validate_device(valid_device(), symbol_root=symbols, footprint_root=tmp_path) == []


def test_required_policy_needs_footprint(tmp_path: Path):
    symbols = tmp_path / "symbols"
    make_symbol(symbols)
    device = valid_device()
    device["footprint_policy"] = "required"
    errors = validate_device(device, symbol_root=symbols, footprint_root=tmp_path)
    assert "footprint_policy required verlangt einen Footprint" in errors


def test_none_policy_rejects_footprint(tmp_path: Path):
    symbols = tmp_path / "symbols"
    make_symbol(symbols)
    footprints = tmp_path / "footprints" / "Z_Test.pretty"
    footprints.mkdir(parents=True)
    (footprints / "Test.kicad_mod").write_text("(footprint \"Test\")\n", encoding="utf-8")
    device = valid_device()
    device["footprint_policy"] = "none"
    device["footprint"] = "Z_Test:Test"
    errors = validate_device(device, symbol_root=symbols, footprint_root=tmp_path / "footprints")
    assert "footprint_policy none darf keinen Footprint besitzen" in errors


def test_catalog_rejects_duplicate_ids(tmp_path: Path):
    symbols = tmp_path / "symbols"
    make_symbol(symbols)
    devices = tmp_path / "devices"
    devices.mkdir()
    text = '''{
      "id": "generic.test",
      "manufacturer": "Generic",
      "series": "Template",
      "part_number": "TEST-1",
      "device_type": "Testgerät",
      "function_group": "Test",
      "symbol": "Z_Test:Test",
      "footprint_policy": "optional"
    }\n'''
    (devices / "a.yaml").write_text(text, encoding="utf-8")
    (devices / "b.yaml").write_text(text, encoding="utf-8")
    errors = validate_catalog(devices, symbol_root=symbols, footprint_root=tmp_path)
    assert any("Doppelte Geräte-ID" in error for error in errors)
