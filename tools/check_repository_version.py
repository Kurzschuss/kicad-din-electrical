from __future__ import annotations

import argparse
import json
import os
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable, Sequence
from urllib.parse import urlparse

CommandRunner = Callable[[Sequence[str]], subprocess.CompletedProcess[str]]
OFFICIAL_REPOSITORY = "Kurzschuss/kicad-din-electrical"
WHITELIST_FILE = Path("config/authorized_developers.json")


@dataclass(frozen=True)
class VersionResult:
    status: str
    current: bool
    message: str
    local_commit: str = ""
    remote_commit: str = ""
    branch: str = ""
    ahead: int = 0
    behind: int = 0
    remote_url: str = ""
    official_remote: bool = False
    clean_worktree: bool = False
    developer_mode: bool = False
    authenticated_user: str = ""
    developer_authorized: bool = False


def run_command(args: Sequence[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, text=True, encoding="utf-8", errors="replace", capture_output=True, check=False)


def run_git(args: Sequence[str]) -> subprocess.CompletedProcess[str]:
    return run_command(["git", *args])


def _value(runner: CommandRunner, args: Sequence[str]) -> str:
    result = runner(args)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "Git-Befehl fehlgeschlagen")
    return result.stdout.strip()


def normalize_repository(url: str) -> str:
    value = url.strip().removesuffix(".git")
    if value.startswith("git@github.com:"):
        return value.split(":", 1)[1].strip("/").lower()
    parsed = urlparse(value)
    if parsed.hostname and parsed.hostname.lower() == "github.com":
        return parsed.path.strip("/").lower()
    return ""


def load_authorized_developers(path: Path = WHITELIST_FILE) -> set[str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    users = data.get("github_users", [])
    return {str(user).strip().lower() for user in users if str(user).strip()}


def authenticated_github_user(command_runner: CommandRunner = run_command) -> str:
    result = command_runner(["gh", "api", "user", "--jq", ".login"])
    return result.stdout.strip() if result.returncode == 0 else ""


def classify_repository_state(*, local_commit: str, remote_commit: str, branch: str, ahead: int,
                              behind: int, remote_url: str, clean_worktree: bool,
                              developer_mode: bool = False, authenticated_user: str = "",
                              authorized_users: set[str] | None = None) -> VersionResult:
    official = normalize_repository(remote_url) == OFFICIAL_REPOSITORY.lower()
    authorized = authenticated_user.lower() in (authorized_users or set()) if authenticated_user else False
    common = dict(local_commit=local_commit, remote_commit=remote_commit, branch=branch,
                  ahead=ahead, behind=behind, remote_url=remote_url,
                  official_remote=official, clean_worktree=clean_worktree,
                  developer_mode=developer_mode, authenticated_user=authenticated_user,
                  developer_authorized=authorized)
    if not official:
        return VersionResult("nicht_offizielles_repository", False,
            "Die GitHub-Meldung ist nur aus dem offiziellen Repository zulässig.", **common)
    if behind > 0:
        return VersionResult("veraltet", False,
            f"Der lokale Stand ist {behind} Commit(s) hinter origin/main. Bitte zuerst aktualisieren und erneut testen.", **common)
    if local_commit == remote_commit and clean_worktree:
        return VersionResult("original_aktuell", True,
            "Die unveränderte offizielle Originalversion ist aktuell.", **common)
    if developer_mode and authorized:
        return VersionResult("entwickler_freigegeben", True,
            "Entwicklermodus durch authentifizierten Whitelist-Benutzer freigegeben.", **common)
    if developer_mode and not authorized:
        return VersionResult("entwicklermodus_nicht_autorisiert", False,
            "Der Entwicklermodus ist aktiviert, aber der authentifizierte GitHub-Benutzer ist nicht freigegeben.", **common)
    return VersionResult("lokal_veraendert", False,
        "Die Arbeitskopie oder Historie weicht von der aktuellen Originalversion ab. Eine GitHub-Meldung bleibt gesperrt.", **common)


def check_repository_version(git_runner: CommandRunner = run_git,
                             command_runner: CommandRunner = run_command) -> VersionResult:
    try:
        fetch = git_runner(["fetch", "--quiet", "origin", "main"])
        if fetch.returncode != 0:
            raise RuntimeError(fetch.stderr.strip() or fetch.stdout.strip() or "GitHub nicht erreichbar")
        local_commit = _value(git_runner, ["rev-parse", "HEAD"])
        remote_commit = _value(git_runner, ["rev-parse", "origin/main"])
        branch = _value(git_runner, ["branch", "--show-current"]) or "(detached HEAD)"
        remote_url = _value(git_runner, ["remote", "get-url", "origin"])
        counts = _value(git_runner, ["rev-list", "--left-right", "--count", "HEAD...origin/main"])
        ahead, behind = (int(value) for value in counts.split())
        clean = not _value(git_runner, ["status", "--porcelain", "--untracked-files=normal"])
        developer_mode = os.getenv("KICAD_DIN_DEVELOPER_MODE", "").strip().lower() in {"1", "true", "ja", "yes"}
        user = authenticated_github_user(command_runner) if developer_mode else ""
        users = load_authorized_developers() if developer_mode else set()
        return classify_repository_state(local_commit=local_commit, remote_commit=remote_commit,
            branch=branch, ahead=ahead, behind=behind, remote_url=remote_url,
            clean_worktree=clean, developer_mode=developer_mode,
            authenticated_user=user, authorized_users=users)
    except (RuntimeError, ValueError, OSError, json.JSONDecodeError) as exc:
        return VersionResult("unbekannt", False,
            f"Die Originalität und Aktualität konnten nicht sicher bestätigt werden. GitHub-Meldung gesperrt. Grund: {exc}")


def write_result(result: VersionResult, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(asdict(result), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Prüft Aktualität und Originalität des Repositorys.")
    parser.add_argument("--output", type=Path, default=Path("build/VERSIONSPRUEFUNG.json"))
    args = parser.parse_args()
    result = check_repository_version()
    write_result(result, args.output)
    print("Repositoryprüfung")
    print(f"Status: {result.status}")
    if result.branch:
        print(f"Branch: {result.branch}")
    if result.authenticated_user:
        print(f"GitHub-Benutzer: {result.authenticated_user}")
    print(result.message)
    print(f"Ergebnisdatei: {args.output}")
    return 0 if result.current else 2


if __name__ == "__main__":
    raise SystemExit(main())
