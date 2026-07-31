"""Tests that failed project saves do not replace existing files."""
from pathlib import Path

import pytest

from .din_editor_project_bundle import DinProjectBundleError, _save_json_atomic


def test_atomic_save_failure_preserves_existing_file(monkeypatch, tmp_path):
    target = tmp_path / "project.din.json"
    target.write_text("original\n", encoding="utf-8")

    def fail_replace(self, destination):
        raise OSError("simulated replace failure")

    monkeypatch.setattr(Path, "replace", fail_replace)

    with pytest.raises(DinProjectBundleError, match="cannot be saved"):
        _save_json_atomic({"version": 2}, target)

    assert target.read_text(encoding="utf-8") == "original\n"
    assert not list(tmp_path.glob(f".{target.name}.*.tmp"))
