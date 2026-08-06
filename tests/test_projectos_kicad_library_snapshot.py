from __future__ import annotations

import pytest

from projectos import (
    KiCadAssetType,
    KiCadCompleteSnapshotBuilder,
    KiCadLibraryTable,
    KiCadLibraryTableEntry,
    KiCadLibraryTableType,
    KiCadLocalFileSet,
    NativeKiCadSource,
)


def _symbol_table() -> KiCadLibraryTable:
    return KiCadLibraryTable(
        KiCadLibraryTableType.SYMBOL,
        (
            KiCadLibraryTableEntry(
                KiCadLibraryTableType.SYMBOL,
                "ProjectSymbols",
                "KiCad",
                "${KIPRJMOD}/symbols/project.kicad_sym",
                "/project/symbols/project.kicad_sym",
            ),
        ),
    )


def _footprint_table() -> KiCadLibraryTable:
    return KiCadLibraryTable(
        KiCadLibraryTableType.FOOTPRINT,
        (
            KiCadLibraryTableEntry(
                KiCadLibraryTableType.FOOTPRINT,
                "ProjectFootprints",
                "KiCad",
                "${KIPRJMOD}/footprints/project.pretty",
                "/project/footprints/project.pretty",
            ),
        ),
    )


def test_builds_complete_snapshot_from_tables_and_files() -> None:
    files = KiCadLocalFileSet({
        "/project/symbols/project.kicad_sym": b'''(kicad_symbol_lib (version 20231120)
          (symbol "DIN_MCB" (symbol "DIN_MCB_1_1"
            (pin passive line (name "1") (number "1")))))''',
        "/project/footprints/project.pretty/DIN_1TE.kicad_mod": b'(footprint "DIN_1TE")',
    })

    result = KiCadCompleteSnapshotBuilder(files).build(
        symbol_table=_symbol_table(),
        footprint_table=_footprint_table(),
        model_sources=(NativeKiCadSource("Project3D", "DIN_1TE.step", b"ISO-10303-21;"),),
    )

    assert result.symbol_library_count == 1
    assert result.footprint_library_count == 1
    assert result.model_source_count == 1
    assert {item.asset_type for item in result.items} == {
        KiCadAssetType.SYMBOL,
        KiCadAssetType.FOOTPRINT,
        KiCadAssetType.MODEL_3D,
    }


def test_symbol_table_without_footprint_table_is_valid() -> None:
    files = KiCadLocalFileSet({
        "/project/symbols/project.kicad_sym": b'(kicad_symbol_lib (version 20231120) (symbol "LogicOnly"))',
    })

    result = KiCadCompleteSnapshotBuilder(files).build(symbol_table=_symbol_table())

    assert len(result.items) == 1
    assert result.items[0].asset_type is KiCadAssetType.SYMBOL
    assert result.footprint_library_count == 0


def test_footprint_table_without_symbol_table_is_valid() -> None:
    files = KiCadLocalFileSet({
        "/project/footprints/project.pretty/DIN_1TE.kicad_mod": b'(footprint "DIN_1TE")',
    })

    result = KiCadCompleteSnapshotBuilder(files).build(footprint_table=_footprint_table())

    assert len(result.items) == 1
    assert result.items[0].asset_type is KiCadAssetType.FOOTPRINT
    assert result.symbol_library_count == 0


def test_rejects_declared_but_missing_symbol_library() -> None:
    with pytest.raises(ValueError, match="ERR-KICAD-0047"):
        KiCadCompleteSnapshotBuilder(KiCadLocalFileSet({})).build(symbol_table=_symbol_table())


def test_rejects_empty_declared_footprint_library() -> None:
    files = KiCadLocalFileSet({
        "/project/footprints/project.pretty/readme.txt": b"keine footprints",
    })
    with pytest.raises(ValueError, match="ERR-KICAD-0050"):
        KiCadCompleteSnapshotBuilder(files).build(footprint_table=_footprint_table())


def test_ignores_nested_footprint_directories() -> None:
    files = KiCadLocalFileSet({
        "/project/footprints/project.pretty/sub/nested.kicad_mod": b'(footprint "Nested")',
    })
    with pytest.raises(ValueError, match="ERR-KICAD-0050"):
        KiCadCompleteSnapshotBuilder(files).build(footprint_table=_footprint_table())
