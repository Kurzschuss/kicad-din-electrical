from pathlib import Path

from tools.z_cockpit.library_browser import LibrarySymbol, SymbolLibrary
from tools.z_cockpit.quality_engine import evaluate_libraries, evaluate_library


def library(*symbols: LibrarySymbol, name: str = "Z_Test") -> SymbolLibrary:
    return SymbolLibrary(
        name=name,
        file=Path(f"symbols/{name}.kicad_sym"),
        symbols=tuple(symbols),
        symbol_count=len(symbols),
        device_count=sum(symbol.device_count for symbol in symbols),
        footprint_count=sum(symbol.footprint_available for symbol in symbols),
        complete_preview_count=sum(
            symbol.symbol_preview_available and symbol.footprint_preview_available
            for symbol in symbols
        ),
    )


def symbol(
    reference: str = "Z_Test:Demo",
    *,
    devices: tuple[str, ...] = ("demo.device",),
    symbol_preview: bool = True,
    footprint_name: str | None = "Z_Demo",
    footprint_available: bool = True,
    footprint_preview: bool = True,
) -> LibrarySymbol:
    return LibrarySymbol(
        reference=reference,
        name=reference.split(":", 1)[1],
        device_ids=devices,
        device_count=len(devices),
        symbol_preview_available=symbol_preview,
        footprint_name=footprint_name,
        footprint_available=footprint_available,
        footprint_preview_available=footprint_preview,
    )


def test_complete_library_scores_one_hundred_percent():
    result = evaluate_library(library(symbol()))
    assert result.score == 100
    assert result.status == "ok"
    assert result.checks_total == 5
    assert result.checks_passed == 5
    assert result.warning_count == 0
    assert result.error_count == 0
    assert result.issues == ()


def test_missing_footprint_is_error_and_missing_previews_are_warnings():
    result = evaluate_library(
        library(
            symbol(
                devices=(),
                symbol_preview=False,
                footprint_name=None,
                footprint_available=False,
                footprint_preview=False,
            )
        )
    )
    assert result.score == 0
    assert result.status == "error"
    assert result.error_count == 1
    assert result.warning_count == 4
    assert {issue.check_id for issue in result.issues} == {
        "device_mapping",
        "footprint_exists",
        "symbol_preview",
        "footprint_preview",
        "complete_preview_pair",
    }
    assert all(issue.symbol_reference == "Z_Test:Demo" for issue in result.issues)


def test_warning_only_result_has_warning_status():
    result = evaluate_library(library(symbol(devices=())))
    assert result.score == 80
    assert result.status == "warning"
    assert result.error_count == 0
    assert result.warning_count == 1


def test_empty_library_is_not_penalized():
    result = evaluate_library(library())
    assert result.score == 100
    assert result.status == "ok"
    assert result.checks_total == 0


def test_multiple_libraries_are_sorted_stably():
    results = evaluate_libraries((library(symbol(reference="Z_B:B"), name="Z_B"), library(symbol(reference="Z_A:A"), name="Z_A")))
    assert [result.library_name for result in results] == ["Z_A", "Z_B"]
