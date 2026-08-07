from pathlib import Path


FOOTPRINT_1P = Path("footprints/Z_MCB.pretty/Z_MCB_1P_18mm.kicad_mod")
FOOTPRINT_3P = Path("footprints/Z_MCB.pretty/Z_MCB_3P_54mm.kicad_mod")


def test_mcb_1p_footprint_is_104x18_with_centered_connection_pads() -> None:
    content = FOOTPRINT_1P.read_text(encoding="utf-8")

    assert '(start -9 -52)' in content
    assert '(end 9 52)' in content
    assert '(at 0 -47)' in content
    assert '(at 0 47)' in content
    assert '(size 6 6)' in content
    assert '(drill 4)' in content


def test_mcb_3p_footprint_is_104x54_with_six_pads_on_18mm_grid() -> None:
    content = FOOTPRINT_3P.read_text(encoding="utf-8")

    assert '(start -27 -52)' in content
    assert '(end 27 52)' in content
    for point in (
        '(-18 -47)', '(0 -47)', '(18 -47)',
        '(-18 47)', '(0 47)', '(18 47)',
    ):
        assert point in content
    assert content.count('(drill 4)') == 6
    assert content.count('(size 6 6)') == 6


def test_mcb_footprints_reference_projectos_wrl_models_portably() -> None:
    one = FOOTPRINT_1P.read_text(encoding="utf-8")
    three = FOOTPRINT_3P.read_text(encoding="utf-8")

    assert '${Z_PROJECTOS_3DMODEL_DIR}/Z_MCB_1P/generated/Z_MCB_1P.wrl' in one
    assert '${Z_PROJECTOS_3DMODEL_DIR}/Z_MCB_3P/generated/Z_MCB_3P.wrl' in three
    for content in (one, three):
        assert '${PROJECTOS_3DMODEL_DIR}' not in content
        assert '${KIPRJMOD}' not in content
        assert 'C:/Users/' not in content
        assert '(offset (xyz 0 0 0))' in content
        assert '(scale (xyz 1 1 1))' in content
        assert '(rotate (xyz 0 0 0))' in content


def test_mcb_footprints_do_not_reference_external_manufacturer_assets() -> None:
    content = (FOOTPRINT_1P.read_text(encoding="utf-8") + FOOTPRINT_3P.read_text(encoding="utf-8")).casefold()

    assert "traceparts" not in content
    assert "siemens" not in content
    assert "hager" not in content
    assert "abb" not in content
