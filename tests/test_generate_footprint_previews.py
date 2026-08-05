from pathlib import Path

from tools.generate_footprint_previews import (
    FootprintRectangle,
    check_previews,
    footprint_name,
    generated_files,
    parse_rectangles,
    render_svg,
    write_previews,
)


SAMPLE = '''(footprint "Z_DIN_Module_18mm" (version 20240108)
  (fp_rect
    (start -9 -45)
    (end 9 45)
    (stroke (width 0.1) (type default))
    (fill none)
    (layer "F.Fab")
  )
  (fp_rect
    (start -9 -45)
    (end 9 45)
    (stroke (width 0.05) (type default))
    (fill none)
    (layer "F.CrtYd")
  )
)'''


def test_extracts_footprint_name():
    assert footprint_name(SAMPLE, "fallback") == "Z_DIN_Module_18mm"
    assert footprint_name("(version 1)", "fallback") == "fallback"


def test_parses_supported_rectangles():
    rectangles = parse_rectangles(SAMPLE)
    assert rectangles == [
        FootprintRectangle(-9.0, -45.0, 9.0, 45.0, "F.Fab"),
        FootprintRectangle(-9.0, -45.0, 9.0, 45.0, "F.CrtYd"),
    ]


def test_rendered_svg_is_accessible_and_distinguishes_courtyard():
    svg = render_svg("Z_DIN_Module_18mm", parse_rectangles(SAMPLE))
    assert 'role="img"' in svg
    assert "<title>Footprint: Z_DIN_Module_18mm</title>" in svg
    assert 'stroke-dasharray="5 4"' in svg
    assert "Z_DIN_Module_18mm" in svg


def test_empty_footprint_gets_clear_message():
    svg = render_svg("Empty", [])
    assert "Keine unterstützte Footprint-Geometrie" in svg


def test_generated_files_follow_deterministic_output_path(tmp_path: Path):
    source = tmp_path / "footprints" / "Z_Test.pretty" / "Z_Test.kicad_mod"
    source.parent.mkdir(parents=True)
    source.write_text(SAMPLE.replace("Z_DIN_Module_18mm", "Z_Test"), encoding="utf-8")
    output = tmp_path / "site" / "footprint-previews"

    files = generated_files(tmp_path / "footprints", output)

    assert list(files) == [output / "Z_Test.svg"]
    assert "Footprint: Z_Test" in files[output / "Z_Test.svg"]


def test_write_and_check_previews(tmp_path: Path):
    output = tmp_path / "previews"
    files = {output / "Z_Test.svg": "<svg/>\n"}
    assert check_previews(files, output) is False
    write_previews(files)
    assert check_previews(files, output) is True
    (output / "unexpected.svg").write_text("<svg/>\n", encoding="utf-8")
    assert check_previews(files, output) is False
