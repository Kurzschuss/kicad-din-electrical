from pathlib import Path

import pytest

from tools.generate_symbol_previews import parse_polylines, symbol_blocks


MCB_PATH = Path("symbols/Z_MCB.kicad_sym")


def test_mcb_3p_shows_two_horizontal_strokes_in_each_pole_gap():
    block = symbol_blocks(MCB_PATH.read_text(encoding="utf-8"))["MCB_3P"]
    polylines = parse_polylines(block)
    points = {polyline.points for polyline in polylines}

    expected_strokes = {
        # Zwischen Pol 1 und Pol 2: freier Trennungsstrich + Kontaktstrich zu Pol 2.
        ((6.985, -1.27), (8.255, -1.27)),
        ((10.16, -1.27), (11.43, -1.27)),
        # Zwischen Pol 2 und Pol 3: freier Trennungsstrich + Kontaktstrich zu Pol 3.
        ((14.605, -1.27), (15.875, -1.27)),
        ((17.78, -1.27), (19.05, -1.27)),
    }

    assert expected_strokes.issubset(points)

    short_horizontal_strokes = [
        polyline
        for polyline in polylines
        if len(polyline.points) == 2
        and all(y == pytest.approx(-1.27) for _, y in polyline.points)
        and abs(polyline.points[1][0] - polyline.points[0][0]) == pytest.approx(1.27)
    ]
    assert len(short_horizontal_strokes) == 4

    # Die beiden zusätzlichen Kontaktstriche enden genau am jeweiligen schrägen Kontakt.
    assert ((10.16, -1.27), (11.43, -1.27)) in points
    assert ((17.78, -1.27), (19.05, -1.27)) in points
