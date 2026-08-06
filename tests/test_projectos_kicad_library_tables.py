from __future__ import annotations

import pytest

from projectos import (
    KiCadLibraryTableParser,
    KiCadLibraryTableType,
    KiCadVariableContext,
)


def context() -> KiCadVariableContext:
    return KiCadVariableContext(
        variables={
            "KIPRJMOD": "/projects/panel",
            "KICAD9_SYMBOL_DIR": "/opt/kicad/share/symbols",
            "KICAD9_FOOTPRINT_DIR": "/opt/kicad/share/footprints",
        },
        allowed_roots=("/projects/panel", "/opt/kicad/share"),
    )


def test_reads_symbol_library_table_and_preserves_fields() -> None:
    table = KiCadLibraryTableParser().parse(
        table_type=KiCadLibraryTableType.SYMBOL,
        context=context(),
        content='''(sym_lib_table
          (version 7)
          (lib (name "Device") (type "KiCad")
               (uri "${KICAD9_SYMBOL_DIR}/Device.kicad_sym")
               (options "") (descr "KiCad standard devices"))
          (lib (name "ProjectOS") (type "KiCad")
               (uri "${KIPRJMOD}/symbols/projectos.kicad_sym")
               (options "locked") (descr "Projektbibliothek")))''',
    )

    assert len(table.entries) == 2
    assert table.get("device") is not None
    assert table.entries[0].resolved_path == "/opt/kicad/share/symbols/Device.kicad_sym"
    assert table.entries[0].description == "KiCad standard devices"
    assert table.entries[1].resolved_path == "/projects/panel/symbols/projectos.kicad_sym"
    assert table.entries[1].options == "locked"


def test_reads_footprint_table_with_relative_project_path() -> None:
    table = KiCadLibraryTableParser().parse(
        table_type=KiCadLibraryTableType.FOOTPRINT,
        context=context(),
        content='''(fp_lib_table
          (lib (name "ProjectFootprints") (type "KiCad")
               (uri "footprints/ProjectOS.pretty") (options "") (descr "")))''',
    )

    assert table.entries[0].resolved_path == "/projects/panel/footprints/ProjectOS.pretty"


def test_symbol_and_footprint_tables_remain_independent() -> None:
    symbol_table = KiCadLibraryTableParser().parse(
        table_type=KiCadLibraryTableType.SYMBOL,
        context=context(),
        content='''(sym_lib_table
          (lib (name "LogicOnly") (type "KiCad")
               (uri "${KIPRJMOD}/symbols/logic.kicad_sym") (options "") (descr "")))''',
    )

    assert len(symbol_table.entries) == 1
    assert symbol_table.entries[0].name == "LogicOnly"


def test_rejects_unknown_variable() -> None:
    with pytest.raises(ValueError, match="ERR-KICAD-0041"):
        KiCadLibraryTableParser().parse(
            table_type=KiCadLibraryTableType.SYMBOL,
            context=context(),
            content='''(sym_lib_table
              (lib (name "Unknown") (type "KiCad")
                   (uri "${UNKNOWN_DIR}/x.kicad_sym") (options "") (descr "")))''',
        )


def test_rejects_path_outside_allowed_roots() -> None:
    unsafe = KiCadVariableContext(
        variables={"KIPRJMOD": "/projects/panel", "EXTERNAL": "/private/secret"},
        allowed_roots=("/projects/panel",),
    )
    with pytest.raises(ValueError, match="ERR-KICAD-0043"):
        KiCadLibraryTableParser().parse(
            table_type=KiCadLibraryTableType.SYMBOL,
            context=unsafe,
            content='''(sym_lib_table
              (lib (name "External") (type "KiCad")
                   (uri "${EXTERNAL}/x.kicad_sym") (options "") (descr "")))''',
        )


def test_rejects_duplicate_library_names_case_insensitively() -> None:
    with pytest.raises(ValueError, match="ERR-KICAD-0039"):
        KiCadLibraryTableParser().parse(
            table_type=KiCadLibraryTableType.SYMBOL,
            context=context(),
            content='''(sym_lib_table
              (lib (name "ProjectOS") (type "KiCad")
                   (uri "${KIPRJMOD}/a.kicad_sym") (options "") (descr ""))
              (lib (name "projectos") (type "KiCad")
                   (uri "${KIPRJMOD}/b.kicad_sym") (options "") (descr "")))''',
        )


def test_rejects_wrong_table_type() -> None:
    with pytest.raises(ValueError, match="ERR-KICAD-0038"):
        KiCadLibraryTableParser().parse(
            table_type=KiCadLibraryTableType.FOOTPRINT,
            context=context(),
            content="(sym_lib_table)",
        )


def test_rejects_nonlocal_uri() -> None:
    with pytest.raises(ValueError, match="ERR-KICAD-0040"):
        KiCadLibraryTableParser().parse(
            table_type=KiCadLibraryTableType.SYMBOL,
            context=context(),
            content='''(sym_lib_table
              (lib (name "Remote") (type "KiCad")
                   (uri "https://example.invalid/x.kicad_sym") (options "") (descr "")))''',
        )
