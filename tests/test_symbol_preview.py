from pathlib import Path

import pytest

from tools.z_cockpit.symbol_preview import parse_symbol_reference, symbol_preview


def test_parse_symbol_reference():
    assert parse_symbol_reference("Z_MCB:MCB") == ("Z_MCB", "MCB")


@pytest.mark.parametrize("reference", ["", "Z_MCB", ":MCB", "Z_MCB:", "A:B:C"])
def test_rejects_invalid_symbol_reference(reference: str):
    with pytest.raises(ValueError):
        parse_symbol_reference(reference)


@pytest.mark.parametrize("reference", ["../Z_MCB:MCB", "Z_MCB:../MCB", "Z/MBC:MCB", "Z_MCB:M\\CB"])
def test_rejects_unsafe_symbol_reference(reference: str):
    with pytest.raises(ValueError):
        parse_symbol_reference(reference)


def test_symbol_preview_points_to_existing_svg(tmp_path: Path):
    preview_file = tmp_path / "docs" / "site" / "symbol-previews" / "Z_MCB" / "MCB.svg"
    preview_file.parent.mkdir(parents=True)
    preview_file.write_text("<svg/>", encoding="utf-8")

    preview = symbol_preview("Z_MCB:MCB", repo_root=tmp_path)

    assert preview.library == "Z_MCB"
    assert preview.symbol == "MCB"
    assert preview.relative_url == "symbol-previews/Z_MCB/MCB.svg"
    assert preview.file_path == preview_file
    assert preview.available is True


def test_symbol_preview_marks_missing_svg(tmp_path: Path):
    preview = symbol_preview("Z_MCB:MCB", repo_root=tmp_path)
    assert preview.available is False
