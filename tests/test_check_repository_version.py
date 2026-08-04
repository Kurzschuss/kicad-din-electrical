from tools.check_repository_version import classify_repository_state, normalize_repository


def test_official_remote_formats_are_recognized() -> None:
    assert normalize_repository("https://github.com/Kurzschuss/kicad-din-electrical.git") == "kurzschuss/kicad-din-electrical"
    assert normalize_repository("git@github.com:Kurzschuss/kicad-din-electrical.git") == "kurzschuss/kicad-din-electrical"


def test_clean_exact_original_is_allowed() -> None:
    result = classify_repository_state(
        local_commit="abc", remote_commit="abc", branch="main", ahead=0, behind=0,
        remote_url="https://github.com/Kurzschuss/kicad-din-electrical.git",
        clean_worktree=True,
    )
    assert result.current is True
    assert result.status == "original_aktuell"


def test_modified_worktree_is_blocked_for_normal_user() -> None:
    result = classify_repository_state(
        local_commit="abc", remote_commit="abc", branch="main", ahead=0, behind=0,
        remote_url="https://github.com/Kurzschuss/kicad-din-electrical.git",
        clean_worktree=False,
    )
    assert result.current is False
    assert result.status == "lokal_veraendert"


def test_fork_is_blocked() -> None:
    result = classify_repository_state(
        local_commit="abc", remote_commit="abc", branch="main", ahead=0, behind=0,
        remote_url="https://github.com/AnderePerson/kicad-din-electrical.git",
        clean_worktree=True,
    )
    assert result.current is False
    assert result.status == "nicht_offizielles_repository"


def test_authorized_developer_mode_allows_feature_branch() -> None:
    result = classify_repository_state(
        local_commit="feature", remote_commit="main", branch="feature/test", ahead=2, behind=0,
        remote_url="git@github.com:Kurzschuss/kicad-din-electrical.git",
        clean_worktree=False, developer_mode=True, authenticated_user="Kurzschuss",
        authorized_users={"kurzschuss"},
    )
    assert result.current is True
    assert result.status == "entwickler_freigegeben"


def test_developer_mode_without_whitelist_is_blocked() -> None:
    result = classify_repository_state(
        local_commit="feature", remote_commit="main", branch="feature/test", ahead=2, behind=0,
        remote_url="git@github.com:Kurzschuss/kicad-din-electrical.git",
        clean_worktree=False, developer_mode=True, authenticated_user="AnderePerson",
        authorized_users={"kurzschuss"},
    )
    assert result.current is False
    assert result.status == "entwicklermodus_nicht_autorisiert"


def test_outdated_state_is_always_blocked() -> None:
    result = classify_repository_state(
        local_commit="old", remote_commit="new", branch="main", ahead=0, behind=4,
        remote_url="https://github.com/Kurzschuss/kicad-din-electrical.git",
        clean_worktree=True, developer_mode=True, authenticated_user="Kurzschuss",
        authorized_users={"kurzschuss"},
    )
    assert result.current is False
    assert result.status == "veraltet"
