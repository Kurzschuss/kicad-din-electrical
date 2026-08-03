import json
from pathlib import Path

import pytest

from tools.quality.run_quality import (
    filter_findings,
    main,
    render_console,
    render_html,
    render_markdown,
)
from tools.quality.rule_engine import Finding


MCB = Path("symbols/Z_MCB.kicad_sym")


def test_release_profile_accepts_z_mcb(tmp_path, capsys):
    json_output = tmp_path / "quality.json"
    summary_output = tmp_path / "summary.md"
    html_output = tmp_path / "quality.html"

    result = main(
        [
            "--profile",
            "release",
            "--json-output",
            str(json_output),
            "--html-output",
            str(html_output),
            "--summary-output",
            str(summary_output),
            str(MCB),
        ]
    )

    assert result == 0
    assert "Z_ quality report" in capsys.readouterr().out
    payload = json.loads(json_output.read_text(encoding="utf-8"))
    assert {item["status"] for item in payload} == {"z_conform"}
    assert {item["scope"] for item in payload} == {"symbol"}
    assert "| `ZSYM-001` |" in summary_output.read_text(encoding="utf-8")
    html = html_output.read_text(encoding="utf-8")
    assert "<!doctype html>" in html
    assert "ZSYM-001" in html
    assert "symbol" in html


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
        scope="symbol",
        category="geometry",
    )

    console = render_console([finding], "development")
    markdown = render_markdown([finding], "development")
    html = render_html([finding], "development")

    assert "Documented explanation." in console
    assert "Concrete recommendation." in console
    assert "needs_rework" in markdown
    assert "ZSYM-999" in markdown
    assert "Documented explanation." in html
    assert "Concrete recommendation." in html
    assert "geometry" in html


def test_filters_combine_status_category_and_scope():
    findings = [
        Finding("A", "ZSYM-1", "A", "error", "needs_rework", 1, 2, "x", "y", scope="symbol", category="geometry"),
        Finding("B", "ZFP-1", "B", "warning", "z_conform", True, True, "x", "y", scope="footprint", category="geometry"),
        Finding("C", "ZFP-2", "C", "error", "needs_rework", True, False, "x", "y", scope="footprint", category="presentation"),
    ]

    filtered = filter_findings(
        findings,
        statuses=["needs_rework"],
        categories=["presentation"],
        scopes=["footprint"],
    )
    assert [finding.rule_id for finding in filtered] == ["ZFP-2"]


def test_html_escapes_untrusted_values():
    finding = Finding(
        "<element>", "ZSYM-X", "<title>", "warning", "needs_rework",
        "<expected>", "<actual>", "<explanation>", "<recommendation>",
        scope="symbol", category="test",
    )
    html = render_html([finding], "<profile>")
    assert "&lt;element&gt;" in html
    assert "&lt;profile&gt;" in html
    assert "<element>" not in html
