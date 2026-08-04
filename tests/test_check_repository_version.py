from tools.check_repository_version import classify_version_state


def test_exact_main_state_is_current() -> None:
    result = classify_version_state(
        local_commit="abc",
        remote_commit="abc",
        branch="main",
        remote_is_ancestor=True,
        ahead=0,
        behind=0,
    )
    assert result.current is True
    assert result.status == "aktuell"


def test_feature_branch_with_latest_main_is_current() -> None:
    result = classify_version_state(
        local_commit="feature",
        remote_commit="main",
        branch="feature/test",
        remote_is_ancestor=True,
        ahead=3,
        behind=0,
    )
    assert result.current is True
    assert result.status == "aktuell_mit_lokalen_aenderungen"


def test_branch_without_latest_main_is_blocked() -> None:
    result = classify_version_state(
        local_commit="old",
        remote_commit="new",
        branch="main",
        remote_is_ancestor=False,
        ahead=0,
        behind=4,
    )
    assert result.current is False
    assert result.status == "veraltet"
    assert "4 Commit(s) zurück" in result.message
