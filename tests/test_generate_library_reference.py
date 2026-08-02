from pathlib import Path

from tools.generate_library_reference import (
    check_files,
    footprint_libraries,
    render_footprint_index,
    render_symbol_index,
    symbol_libraries,
    symbol_names,
)


def test_symbol_libraries_are_sorted_and_filtered(tmp_path: Path):
    (tmp_path / "Z_B.kicad_sym").write_text("", encoding="utf-8")
    (tmp_path / "Z_A.kicad_sym").write_text("", encoding="utf-8")
    (tmp_path / "README.md").write_text("", encoding="utf-8")

    assert [path.name for path in symbol_libraries(tmp_path)] == [
        "Z_A.kicad_sym",
        "Z_B.kicad_sym",
    ]


def test_footprint_libraries_are_sorted_and_only_directories(tmp_path: Path):
    (tmp_path / "Z_B.pretty").mkdir()
    (tmp_path / "Z_A.pretty").mkdir()
    (tmp_path / "Z_File.pretty").write_text("", encoding="utf-8")

    assert [path.name for path in footprint_libraries(tmp_path)] == [
        "Z_A.pretty",
        "Z_B.pretty",
    ]


def test_symbol_names_reads_only_top_level_symbols(tmp_path: Path):
    library = tmp_path / "Z_Test.kicad_sym"
    library.write_text(
        '''(kicad_symbol_lib (version 20231120)
  (symbol "Main_B"
    (symbol "Main_B_0_1" (rectangle (start 0 0) (end 1 1))))
  (symbol "Main_A"
    (symbol "Main_A_1_1" (pin_names (offset 0))))
)\n''',
        encoding="utf-8",
    )

    assert symbol_names(library) == ["Main_A", "Main_B"]


def test_symbol_names_handles_escaped_quotes_and_duplicates(tmp_path: Path):
    library = tmp_path / "Z_Test.kicad_sym"
    library.write_text(
        '(kicad_symbol_lib (symbol "Name\\\"A") (symbol "Name\\\"A"))\n',
        encoding="utf-8",
    )

    assert symbol_names(library) == ['Name"A']


def test_render_symbol_index_contains_status_symbols_and_footprints(tmp_path: Path):
    symbol_root = tmp_path / "symbols"
    footprint_root = tmp_path / "footprints"
    symbol_root.mkdir()
    footprint_root.mkdir()

    empty = symbol_root / "Z_Empty.kicad_sym"
    filled = symbol_root / "Z_Filled.kicad_sym"
    empty.write_text("(kicad_symbol_lib)\n", encoding="utf-8")
    filled.write_text(
        '(kicad_symbol_lib (symbol "Switch") (symbol "Lamp"))\n',
        encoding="utf-8",
    )
    pretty = footprint_root / "Z_Filled.pretty"
    pretty.mkdir()
    (pretty / "One.kicad_mod").write_text("", encoding="utf-8")
    (pretty / "Two.kicad_mod").write_text("", encoding="utf-8")

    text = render_symbol_index([empty, filled], footprint_root)

    assert "**Anzahl der Bibliotheken:** 2" in text
    assert "`Z_Empty.kicad_sym` — vorbereitet, noch leer" in text
    assert "`Z_Empty.pretty` fehlt" in text
    assert "`Z_Filled.kicad_sym` — 2 Symbol(e)" in text
    assert "`Z_Filled.pretty` mit 2 Footprint(s)" in text
    assert "Symbol: `Lamp`" in text
    assert "Symbol: `Switch`" in text


def test_render_footprint_index_lists_empty_and_filled_libraries(tmp_path: Path):
    empty = tmp_path / "Z_Empty.pretty"
    filled = tmp_path / "Z_Filled.pretty"
    empty.mkdir()
    filled.mkdir()
    (filled / "Z_One.kicad_mod").write_text("", encoding="utf-8")
    (filled / "Z_Two.kicad_mod").write_text("", encoding="utf-8")

    text = render_footprint_index([empty, filled])

    assert "`Z_Empty.pretty` — vorbereitet, noch leer" in text
    assert "`Z_Filled.pretty` — 2 Footprint(s)" in text
    assert "`Z_One.kicad_mod`" in text
    assert "`Z_Two.kicad_mod`" in text


def test_check_files_detects_current_and_outdated_content(tmp_path: Path):
    current = tmp_path / "current.md"
    current.write_text("aktuell", encoding="utf-8")

    assert check_files({current: "aktuell"}) is True
    assert check_files({current: "neu"}) is False
    assert check_files({tmp_path / "missing.md": "neu"}) is False
