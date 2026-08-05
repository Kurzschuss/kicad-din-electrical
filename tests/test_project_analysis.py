from pathlib import Path

from tools.z_cockpit.library_browser import LibrarySymbol, SymbolLibrary
from tools.z_cockpit.project_analysis import analyze_project


def _symbol(
    reference: str,
    *,
    device_ids: tuple[str, ...] = (),
    footprint: bool = True,
    symbol_preview: bool = True,
    footprint_preview: bool = True,
) -> LibrarySymbol:
    return LibrarySymbol(
        reference=reference,
        name=reference.split(":", 1)[1],
        device_ids=device_ids,
        device_count=len(device_ids),
        symbol_preview_available=symbol_preview,
        footprint_name="Z_Test:FP" if footprint else None,
        footprint_available=footprint,
        footprint_preview_available=footprint_preview,
    )


def _library(*symbols: LibrarySymbol) -> SymbolLibrary:
    return SymbolLibrary(
        name="Z_Test",
        file=Path("symbols/Z_Test.kicad_sym"),
        symbols=tuple(symbols),
        symbol_count=len(symbols),
        device_count=sum(item.device_count for item in symbols),
        footprint_count=sum(item.footprint_available for item in symbols),
        complete_preview_count=sum(
            item.symbol_preview_available and item.footprint_preview_available for item in symbols
        ),
    )


def test_complete_project_has_no_findings():
    devices = ({"id": "device-1", "symbol": "Z_Test:Switch"},)
    libraries = (_library(_symbol("Z_Test:Switch", device_ids=("device-1",))),)

    result = analyze_project(devices, libraries)

    assert result.status == "ok"
    assert result.error_count == 0
    assert result.warning_count == 0
    assert result.device_count == 1
    assert result.symbol_count == 1
    assert result.findings == ()


def test_duplicate_device_ids_and_unknown_symbols_are_errors():
    devices = (
        {"id": "duplicate", "symbol": "Z_Test:Missing"},
        {"id": "duplicate", "symbol": "Z_Test:Missing"},
    )

    result = analyze_project(devices, (_library(),))

    checks = [item.check_id for item in result.findings]
    assert result.status == "error"
    assert "device_id_duplicate" in checks
    assert checks.count("symbol_reference_unknown") == 2


def test_missing_id_and_symbol_reference_are_errors():
    result = analyze_project(({"id": "", "symbol": ""},), (_library(),))

    checks = {item.check_id for item in result.findings}
    assert checks == {"device_id_missing", "symbol_reference_missing"}
    assert result.error_count == 2


def test_missing_footprint_and_previews_are_reported():
    devices = ({"id": "device-1", "symbol": "Z_Test:Switch"},)
    libraries = (
        _library(
            _symbol(
                "Z_Test:Switch",
                device_ids=("device-1",),
                footprint=False,
                symbol_preview=False,
                footprint_preview=False,
            )
        ),
    )

    result = analyze_project(devices, libraries)

    findings = {item.check_id: item for item in result.findings}
    assert findings["footprint_missing"].severity == "error"
    assert findings["symbol_preview_missing"].severity == "warning"
    assert findings["footprint_preview_missing"].severity == "warning"
    assert all(item.recommendation_de for item in result.findings)


def test_unused_symbols_are_warnings_and_results_are_stably_sorted():
    libraries = (
        _library(
            _symbol("Z_Test:Zulu"),
            _symbol("Z_Test:Alpha"),
        ),
    )

    result = analyze_project((), libraries)

    assert result.status == "warning"
    assert result.warning_count == 2
    assert [item.reference for item in result.findings] == ["Z_Test:Alpha", "Z_Test:Zulu"]
    assert all(item.check_id == "symbol_unused" for item in result.findings)
