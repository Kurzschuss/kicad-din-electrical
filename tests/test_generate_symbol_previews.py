from pathlib import Path

from tools.generate_symbol_previews import (
    Pin,
    Polyline,
    _preview_projector,
    generated_files,
    parse_pins,
    parse_polylines,
    parse_rectangles,
    render_svg,
    symbol_blocks,
    symbol_names,
)


def sample_symbol() -> str:
    return '''(kicad_symbol_lib (version 20231120)
  (symbol "Switch"
    (symbol "Switch_0_1"
      (rectangle (start -2.54 2.54) (end 2.54 -2.54))
      (polyline (pts (xy -2.54 0) (xy 0 1.27) (xy 2.54 0))
        (stroke (width 0.254) (type default)) (fill (type none)))
    )
    (symbol "Switch_1_1"
      (pin passive line (at -5.08 0 0) (length 2.54))
      (pin passive line (at 5.08 0 180) (length 2.54))
    )
  )
)\n'''


def sample_multi_symbol() -> str:
    return '''(kicad_symbol_lib (version 20231120)
  (symbol "First"
    (symbol "First_0_1"
      (rectangle (start -2.54 2.54) (end 2.54 -2.54))
    )
  )
  (symbol "Second"
    (symbol "Second_0_1"
      (polyline (pts (xy -1.27 0) (xy 0 1.27) (xy 1.27 0))
        (stroke (width 0.254) (type default)) (fill (type none)))
    )
  )
)\n'''


def test_parser_reads_only_top_level_symbol_name():
    assert symbol_names(sample_symbol()) == ["Switch"]


def test_parser_reads_rectangles_pins_and_polylines():
    block = symbol_blocks(sample_symbol())["Switch"]
    rectangles = parse_rectangles(block)
    pins = parse_pins(block)
    polylines = parse_polylines(block)

    assert len(rectangles) == 1
    assert rectangles[0].x1 == -2.54
    assert len(pins) == 2
    assert pins[1].angle == 180
    assert len(polylines) == 1
    assert polylines[0].points[1] == (0.0, 1.27)


def test_svg_contains_accessible_title_and_graphics():
    block = symbol_blocks(sample_symbol())["Switch"]
    svg = render_svg(
        "Z_Test", "Switch", parse_rectangles(block), parse_pins(block), parse_polylines(block)
    )

    assert "<title>Z_Test: Switch</title>" in svg
    assert "<rect" in svg
    assert "<polyline" in svg
    assert svg.count("<line") == 2
    assert "Switch</text>" in svg


def test_preview_projector_auto_fits_wide_and_tall_geometry_with_margin():
    pins = [
        Pin(0.0, 7.62, 270.0, 2.54),
        Pin(0.0, -7.62, 90.0, 2.54),
    ]
    polylines = [Polyline(((-10.16, 0.0), (10.16, 0.0)))]
    project = _preview_projector([], pins, polylines)

    for x, y in [(-10.16, 0.0), (10.16, 0.0), (0.0, 7.62), (0.0, -7.62)]:
        projected_x, projected_y = project(x, y)
        assert 10.0 <= projected_x <= 230.0
        assert 10.0 <= projected_y <= 146.0


def test_multiple_top_level_symbols_do_not_share_geometry(tmp_path: Path):
    (tmp_path / "Z_Multi.kicad_sym").write_text(sample_multi_symbol(), encoding="utf-8")

    files = generated_files(tmp_path)
    rendered = {path.name: content for path, content in files.items()}

    assert sorted(rendered) == ["First.svg", "Second.svg"]
    assert "<rect" in rendered["First.svg"]
    assert "<polyline" not in rendered["First.svg"]
    assert "<polyline" in rendered["Second.svg"]


def test_generator_skips_empty_libraries(tmp_path: Path):
    (tmp_path / "Z_Empty.kicad_sym").write_text("(kicad_symbol_lib)\n", encoding="utf-8")
    (tmp_path / "Z_Test.kicad_sym").write_text(sample_symbol(), encoding="utf-8")

    files = generated_files(tmp_path)

    assert len(files) == 1
    path = next(iter(files))
    assert path.name == "Switch.svg"
    assert path.parent.name == "Z_Test"
