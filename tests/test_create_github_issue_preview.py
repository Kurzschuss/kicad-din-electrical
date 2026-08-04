from tools.create_github_issue_preview import (
    build_issue_preview,
    extract_issue_title,
    redact_sensitive_text,
)


def test_extract_issue_title_uses_test_name() -> None:
    report = "# Automatischer Fehlerbericht\n\n- **Prüfung:** Python-Syntaxprüfung\n"
    assert extract_issue_title(report) == "[Fehlerbericht] Python-Syntaxprüfung"


def test_redaction_masks_windows_user_and_secrets() -> None:
    text = (
        r"Arbeitsordner: C:\Users\Uwe Zimprich\Documents\Projekt" + "\n"
        "TOKEN=geheim\n"
        "api_key: abc123\n"
    )
    cleaned = redact_sensitive_text(text)
    assert r"C:\Users\<Benutzer>\Documents\Projekt" in cleaned
    assert "Uwe Zimprich" not in cleaned
    assert "TOKEN=<MASKIERT>" in cleaned
    assert "api_key=<MASKIERT>" in cleaned
    assert "geheim" not in cleaned
    assert "abc123" not in cleaned


def test_build_issue_preview_is_local_only() -> None:
    title, body = build_issue_preview(
        "# Automatischer Fehlerbericht\n\n- **Prüfung:** Pytest\n"
    )
    assert title == "[Fehlerbericht] Pytest"
    assert "Lokale Vorschau" in body
    assert "nichts veröffentlicht" in body
