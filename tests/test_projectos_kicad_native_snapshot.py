from __future__ import annotations

import pytest

from projectos import (
    KiCadAssetType,
    KiCadNativeSnapshotBuilder,
    NativeKiCadSource,
)


def test_reads_native_symbol_library_with_pins() -> None:
    content = b'''(kicad_symbol_lib (version 20231120) (generator kicad_symbol_editor)
      (symbol "DIN_MCB"
        (symbol "DIN_MCB_1_1"
          (pin passive line (at 0 0 0) (length 2.54) (name "1") (number "1"))
          (pin passive line (at 0 5.08 0) (length 2.54) (name "2") (number "2")))))'''
    result = KiCadNativeSnapshotBuilder().build((
        NativeKiCadSource("ProjectOS", "symbols/projectos.kicad_sym", content),
    ))

    assert result.source_count == 1
    assert len(result.items) == 1
    assert result.items[0].asset_type is KiCadAssetType.SYMBOL
    assert result.items[0].qualified_name == "ProjectOS:DIN_MCB"
    assert result.items[0].pin_numbers == ("1", "2")
    assert len(result.items[0].checksum_sha256 or "") == 64


def test_reads_footprint_and_model_independently() -> None:
    result = KiCadNativeSnapshotBuilder().build((
        NativeKiCadSource(
            "ProjectOS",
            "footprints/DIN_1TE.kicad_mod",
            b'(footprint "DIN_1TE" (version 20240108) (generator pcbnew))',
        ),
        NativeKiCadSource("ProjectOS_3D", "models/DIN_1TE.step", b"ISO-10303-21;"),
    ))

    assert [item.asset_type for item in result.items] == [
        KiCadAssetType.FOOTPRINT,
        KiCadAssetType.MODEL_3D,
    ]
    assert [item.qualified_name for item in result.items] == [
        "ProjectOS:DIN_1TE",
        "ProjectOS_3D:DIN_1TE",
    ]


def test_symbol_library_does_not_require_footprint_source() -> None:
    result = KiCadNativeSnapshotBuilder().build((
        NativeKiCadSource(
            "ProjectOS",
            "symbols/logic.kicad_sym",
            b'(kicad_symbol_lib (version 20231120) (symbol "LogicOnly"))',
        ),
    ))

    assert len(result.items) == 1
    assert result.items[0].asset_type is KiCadAssetType.SYMBOL


def test_rejects_unsupported_file_type() -> None:
    with pytest.raises(ValueError, match="ERR-KICAD-0025"):
        KiCadNativeSnapshotBuilder().build((
            NativeKiCadSource("ProjectOS", "symbols/legacy.lib", b"legacy"),
        ))


def test_rejects_duplicate_library_entry() -> None:
    source = NativeKiCadSource(
        "ProjectOS",
        "footprints/DIN_1TE.kicad_mod",
        b'(footprint "DIN_1TE")',
    )
    with pytest.raises(ValueError, match="ERR-KICAD-0026"):
        KiCadNativeSnapshotBuilder().build((source, source))


def test_rejects_unsafe_source_path() -> None:
    with pytest.raises(ValueError, match="ERR-KICAD-0024"):
        NativeKiCadSource("ProjectOS", "../outside.kicad_sym", b"")


def test_rejects_invalid_symbol_library() -> None:
    with pytest.raises(ValueError, match="ERR-KICAD-0027"):
        KiCadNativeSnapshotBuilder().build((
            NativeKiCadSource("ProjectOS", "symbols/bad.kicad_sym", b'(footprint "Wrong")'),
        ))
