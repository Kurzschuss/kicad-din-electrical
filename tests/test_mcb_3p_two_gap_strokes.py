from pathlib import Path

import pytest

from tools.generate_symbol_previews import parse_polylines, symbol_blocks


MCB_PATH = Path("symbols/Z_MCB.kicad_sym")


def test_mcb_3p_shows_two_horizontal_strokes_in_each_pole_gap():
    block = symbol_blocks(MCB_PATH.read_text(encoding="utf-8"))["MCB_3P"]
    polylines = parse_polylines(block)
    points = {polyline.points for polyline in polylines}

    free_separator_strokes = {
        ((6.985, -1.27), (8.255, -1.27)),
        ((14.605, -1.27), (15.875, -1.27)),
    }
    contact_strokes = {
        ((8.89, -1.27), (11.43, -1.27)),
        ((16.51, -1.27), (19.05, -1.27)),
    }

    assert free_separator_strokes.issubset(points)
    assert contact_strokes.issubset(points)

    free_short_strokes = [
        polyline
        for polyline in polylines
        if len(polyline.points) == 2
        and all(y == pytest.approx(-1.27) for _, y in polyline.points)
        and abs(polyline.points[1][0] - polyline.points[0][0]) == pytest.approx(1.27)
    ]
    contact_short_strokes = [
        polyline
        for polyline in polylines
        if len(polyline.points) == 2
        and all(y == pytest.approx(-1.27) for _, y in polyline.points)
        and abs(polyline.points[1][0] - polyline.points[0][0]) == pytest.approx(2.54)
    ]

    assert len(free_short_strokes) == 2
    assert len(contact_short_strokes) == 2

    # Die Kontaktstriche enden exakt am jeweiligen schrägen Schaltkontakt.
    assert ((8.89, -1.27), (11.43, -1.27)) in points
    assert ((16.51, -1.27), (19.05, -1.27)) in points
