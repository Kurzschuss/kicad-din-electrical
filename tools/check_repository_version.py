from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable, Sequence


CommandRunner = Callable[[Sequence[str]], subprocess.CompletedProcess[str]]


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


def run_git(args: Sequence[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )


def _value(runner: CommandRunner, args: Sequence[str]) -> str:
    result = runner(args)
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "Git-Befehl fehlgeschlagen"
        raise RuntimeError(detail)
    return result.stdout.strip()


def classify_version_state(
    *,
    local_commit: str,
    remote_commit: str,
    branch: str,
    remote_is_ancestor: bool,
    ahead: int,
    behind: int,
) -> VersionResult:
    if local_commit == remote_commit:
        return VersionResult(
            status="aktuell",
            current=True,
            message="Der lokale Stand entspricht dem aktuellen Stand auf GitHub.",
            local_commit=local_commit,
            remote_commit=remote_commit,
            branch=branch,
            ahead=ahead,
            behind=behind,
        )
    if remote_is_ancestor:
        return VersionResult(
            status="aktuell_mit_lokalen_aenderungen",
            current=True,
            message=(
                "Der aktuelle GitHub-main-Stand ist vollständig enthalten. "
                "Der lokale Branch besitzt zusätzliche Commits."
            ),
            local_commit=local_commit,
            remote_commit=remote_commit,
            branch=branch,
            ahead=ahead,
            behind=behind,
        )
    return VersionResult(
        status="veraltet",
        current=False,
        message=(
            f"Der lokale Stand enthält den aktuellen GitHub-main-Stand nicht "
            f"({behind} Commit(s) zurück). Bitte zuerst aktualisieren und erneut testen."
        ),
        local_commit=local_commit,
        remote_commit=remote_commit,
        branch=branch,
        ahead=ahead,
        behind=behind,
    )


def check_repository_version(runner: CommandRunner = run_git) -> VersionResult:
    try:
        fetch = runner(["fetch", "--quiet", "origin", "main"])
        if fetch.returncode != 0:
            detail = fetch.stderr.strip() or fetch.stdout.strip() or "GitHub nicht erreichbar"
            raise RuntimeError(detail)

        local_commit = _value(runner, ["rev-parse", "HEAD"])
        remote_commit = _value(runner, ["rev-parse", "origin/main"])
        branch = _value(runner, ["branch", "--show-current"]) or "(detached HEAD)"
        counts = _value(runner, ["rev-list", "--left-right", "--count", "HEAD...origin/main"])
        ahead_text, behind_text = counts.split()
        ahead, behind = int(ahead_text), int(behind_text)
        ancestor = runner(["merge-base", "--is-ancestor", "origin/main", "HEAD"])
        if ancestor.returncode not in (0, 1):
            raise RuntimeError(ancestor.stderr.strip() or "Abstammung konnte nicht geprüft werden")

        return classify_version_state(
            local_commit=local_commit,
            remote_commit=remote_commit,
            branch=branch,
            remote_is_ancestor=ancestor.returncode == 0,
            ahead=ahead,
            behind=behind,
        )
    except (RuntimeError, ValueError) as exc:
        return VersionResult(
            status="unbekannt",
            current=False,
            message=(
                "Die Aktualität konnte nicht sicher bestätigt werden. "
                f"Eine GitHub-Meldung bleibt gesperrt. Grund: {exc}"
            ),
        )


def write_result(result: VersionResult, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(asdict(result), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Prüft, ob der lokale Stand den aktuellen origin/main-Stand enthält."
    )
    parser.add_argument("--output", type=Path, default=Path("build/VERSIONSPRUEFUNG.json"))
    args = parser.parse_args()

    result = check_repository_version()
    write_result(result, args.output)

    print("Versionsprüfung")
    print(f"Status: {result.status}")
    if result.branch:
        print(f"Branch: {result.branch}")
    if result.local_commit:
        print(f"Lokal:  {result.local_commit}")
    if result.remote_commit:
        print(f"GitHub: {result.remote_commit}")
    if result.ahead or result.behind:
        print(f"Voraus: {result.ahead} / Zurück: {result.behind}")
    print(result.message)
    print(f"Ergebnisdatei: {args.output}")
    return 0 if result.current else 2


if __name__ == "__main__":
    raise SystemExit(main())
