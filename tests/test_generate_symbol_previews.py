from pathlib import Path

from tools.generate_symbol_previews import (
    generated_files,
    parse_pins,
    parse_polylines,
    parse_rectangles,
    render_svg,
    symbol_names,
)


def sample_symbol() -> str:
    return '''(kicad_symbol_lib (version 20231120)
  (symbol "Switch"
    (symbol "Switch_0_1"
      (rectangle (start -2.54 2.54) (end 2.54 -2.54))
      (polyline
        (pts (xy -2.54 0) (xy 0 0) (xy 2.54 -1.27))
      )
    )
    (symbol "Switch_1_1"
      (pin passive line (at -5.08 0 0) (length 2.54))
      (pin passive line (at 5.08 0 180) (length 2.54))
    )
  )
)\n'''


def test_parser_reads_only_top_level_symbol_name():
    assert symbol_names(sample_symbol()) == ["Switch"]


def test_parser_reads_rectangles_pins_and_polylines():
    rectangles = parse_rectangles(sample_symbol())
    pins = parse_pins(sample_symbol())
    polylines = parse_polylines(sample_symbol())

    assert len(rectangles) == 1
    assert rectangles[0].x1 == -2.54
    assert len(pins) == 2
    assert pins[1].angle == 180
    assert len(polylines) == 1
    assert polylines[0].points == ((-2.54, 0.0), (0.0, 0.0), (2.54, -1.27))


def test_svg_contains_accessible_title_and_graphics():
    svg = render_svg(
        "Z_Test",
        "Switch",
        parse_rectangles(sample_symbol()),
        parse_pins(sample_symbol()),
        parse_polylines(sample_symbol()),
    )

    assert "<title>Z_Test: Switch</title>" in svg
    assert "<rect" in svg
    assert svg.count("<line") == 2
    assert "<polyline" in svg
    assert "Switch</text>" in svg


def test_generator_skips_empty_libraries(tmp_path: Path):
    (tmp_path / "Z_Empty.kicad_sym").write_text("(kicad_symbol_lib)\n", encoding="utf-8")
    (tmp_path / "Z_Test.kicad_sym").write_text(sample_symbol(), encoding="utf-8")

    files = generated_files(tmp_path)

    assert len(files) == 1
    path = next(iter(files))
    assert path.name == "Switch.svg"
    assert path.parent.name == "Z_Test"
