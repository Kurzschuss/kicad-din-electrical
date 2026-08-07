from pathlib import Path


FOOTPRINT = Path("footprints/Z_MCB.pretty/Z_MCB_1P_18mm.kicad_mod")


def test_mcb_1p_footprint_uses_18mm_reference_outline() -> None:
    content = FOOTPRINT.read_text(encoding="utf-8")

    assert '(start -9 -45)' in content
    assert '(end 9 45)' in content
    assert '(fp_text reference "Q**"' in content


def test_mcb_1p_footprint_references_project_original_wrl_model_portably() -> None:
    content = FOOTPRINT.read_text(encoding="utf-8")

    assert '${Z_PROJECTOS_3DMODEL_DIR}/Z_MCB_1P/generated/Z_MCB_1P.wrl' in content
    assert '${PROJECTOS_3DMODEL_DIR}' not in content
    assert '${KIPRJMOD}' not in content
    assert 'C:/Users/' not in content
    assert '(offset (xyz 0 0 0))' in content
    assert '(scale (xyz 1 1 1))' in content
    assert '(rotate (xyz 0 0 0))' in content


def test_mcb_1p_footprint_does_not_reference_external_manufacturer_assets() -> None:
    content = FOOTPRINT.read_text(encoding="utf-8").casefold()

    assert "traceparts" not in content
    assert "siemens" not in content
    assert "hager" not in content
    assert "abb" not in content
