from pathlib import Path

from tools.generate_library_reference import (
    check_files,
    footprint_libraries,
    render_footprint_index,
    render_symbol_index,
    symbol_libraries,
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


def test_render_symbol_index_contains_count_and_names(tmp_path: Path):
    libraries = [tmp_path / "Z_A.kicad_sym", tmp_path / "Z_B.kicad_sym"]
    text = render_symbol_index(libraries)

    assert "**Anzahl der Bibliotheken:** 2" in text
    assert "`Z_A.kicad_sym`" in text
    assert "`Z_B.kicad_sym`" in text


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
