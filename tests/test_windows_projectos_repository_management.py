from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUN_TESTS = ROOT / "run_tests.bat"
MANAGER = ROOT / "tools/windows/manage_projectos_repository.ps1"


def test_run_tests_exposes_repository_management_menu() -> None:
    content = RUN_TESTS.read_text(encoding="utf-8")

    assert "[R] Repository installieren / Version pruefen / aktualisieren" in content
    assert ":repository_manager" in content
    assert ":repository_install" in content
    assert ":repository_update" in content
    assert ":refresh_repository_status" in content


def test_run_tests_shows_local_and_remote_repository_versions() -> None:
    content = RUN_TESTS.read_text(encoding="utf-8")

    assert "PROJECTOS_GIT_EXE" in content
    assert "PROJECTOS_REPO_LOCAL_COMMIT" in content
    assert "PROJECTOS_REPO_REMOTE_COMMIT" in content
    assert "PROJECTOS_REPO_STATUS" in content
    assert "PROJECTOS_REPO_AHEAD" in content
    assert "PROJECTOS_REPO_BEHIND" in content


def test_run_tests_distinguishes_repository_source_and_kicad_runtime() -> None:
    content = RUN_TESTS.read_text(encoding="utf-8")

    assert "Repository-Quelle" in content
    assert "KiCad-Laufzeit" in content
    assert "3D-Quelle Repository" in content
    assert "3D-Modelle KiCad" in content
    assert "PROJECTOS_REPOSITORY_ROOT" in content
    assert "PROJECTOS_MODEL_SOURCE_DIR" in content


def test_repository_manager_uses_safe_default_install_location() -> None:
    content = MANAGER.read_text(encoding="utf-8")

    assert "GitHub\\kicad-din-electrical" in content
    assert "[Environment]::GetFolderPath('MyDocuments')" in content
    assert "clone --branch $DefaultBranch --single-branch" in content


def test_repository_manager_finds_git_in_standard_and_github_desktop_paths() -> None:
    content = MANAGER.read_text(encoding="utf-8")

    assert "Resolve-GitExecutable" in content
    assert "Git\\cmd\\git.exe" in content
    assert "GitHubDesktop" in content
    assert "resources\\app\\git\\cmd\\git.exe" in content
    assert "PROJECTOS_GIT_EXE" in content


def test_repository_update_is_fast_forward_only_and_protects_local_changes() -> None:
    content = MANAGER.read_text(encoding="utf-8")

    assert "status --porcelain" in content
    assert "BLOCKED_DIRTY" in content
    assert "pull --ff-only" in content
    assert "BLOCKED_NON_FF" in content


def test_repository_manager_compares_local_and_github_commits() -> None:
    content = MANAGER.read_text(encoding="utf-8")

    assert "fetch origin --quiet" in content
    assert "rev-list --left-right --count" in content
    assert "PROJECTOS_REPO_LOCAL_COMMIT" in content
    assert "PROJECTOS_REPO_REMOTE_COMMIT" in content
    assert "REMOTE_UNAVAILABLE" in content
