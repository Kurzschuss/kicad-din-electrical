import json
from pathlib import Path

import pytest

from tools.quality.run_quality import main, render_console, render_markdown
from tools.quality.rule_engine import Finding


MCB = Path("symbols/Z_MCB.kicad_sym")


def test_release_profile_accepts_z_mcb(tmp_path, capsys):
    json_output = tmp_path / "quality.json"
    summary_output = tmp_path / "summary.md"

    result = main(
        [
            "--profile",
            "release",
            "--json-output",
            str(json_output),
            "--summary-output",
            str(summary_output),
            str(MCB),
        ]
    )

    assert result == 0
    assert "Z_ quality report" in capsys.readouterr().out
    payload = json.loads(json_output.read_text(encoding="utf-8"))
    assert {item["status"] for item in payload} == {"z_conform"}
    assert "| `ZSYM-001` |" in summary_output.read_text(encoding="utf-8")


def test_unknown_profile_fails_clearly():
    with pytest.raises(SystemExit, match="Unknown profile"):
        main(["--profile", "does-not-exist", str(MCB)])


def test_missing_symbol_fails_clearly():
    with pytest.raises(SystemExit, match="Symbol file not found"):
        main(["symbols/Z_DOES_NOT_EXIST.kicad_sym"])


def test_renderers_keep_explanation_and_recommendation_visible():
    finding = Finding(
        element="symbols/Z_Test.kicad_sym",
        rule_id="ZSYM-999",
        title="Test rule",
        severity="warning",
        status="needs_rework",
        expected=100,
        actual=150,
        explanation="Documented explanation.",
        recommendation="Concrete recommendation.",
    )

    console = render_console([finding], "development")
    markdown = render_markdown([finding], "development")

    assert "Documented explanation." in console
    assert "Concrete recommendation." in console
    assert "needs_rework" in markdown
    assert "ZSYM-999" in markdown
