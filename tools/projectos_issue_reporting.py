"""Fail-closed GitHub-Issue-Automatik für ProjectOS.

Eine automatische Meldung ist nur zulässig, wenn
- der Repositoryprüfer den aktuellen offiziellen Stand freigibt,
- ein mit ``gh`` authentifizierter GitHub-Benutzer vorhanden ist,
- dieser eindeutig einem aktiven ProjectOS-Benutzer zugeordnet ist und
- ``github.issue.auto_submit`` effektiv erlaubt ist.

Vor dem Schreiben wird zuerst nach der stabilen ProjectOS-Fingerprint-Markierung
und danach konservativ nach bereits manuell angelegten Issues mit identischem
Titel plus technischer Referenz gesucht. Ein Treffer erzeugt kein zweites Issue,
sondern eine nachvollziehbare Wiederholungsmeldung am bestehenden Issue.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile
from typing import Callable, Sequence

from distributions.projectos_authorization import ProjectOSAuthorizationEvaluator
from tools.check_repository_version import OFFICIAL_REPOSITORY, VersionResult, check_repository_version, run_command
from tools.projectos_governance import load_manager

CommandRunner = Callable[[Sequence[str]], subprocess.CompletedProcess[str]]
DEFAULT_RESULT_PATH = Path("build/Z_ISSUE_REPORTING_RESULT.json")
AUTO_PERMISSION = "github.issue.auto_submit"
MAX_REPORT_BYTES = 64 * 1024
_REPORT_MARKER_RE = re.compile(r"<!--\s*z-report\s+fingerprint=([0-9a-f]{64})\s+reporter=([A-Za-z0-9-]+)\s*-->")
_DUP_MARKER_RE = re.compile(r"<!--\s*z-duplicate-report\s+fingerprint=([0-9a-f]{64})\s+reporter=([A-Za-z0-9-]+)\s*-->")
_SECRET_PATTERNS = (
    re.compile(r"ghp_[A-Za-z0-9]{20,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"(?i)\b(?:password|passwd|token|secret|api[_-]?key)\s*[:=]\s*\S+"),
)


@dataclass(frozen=True)
class ReportIdentity:
    user_id: str
    display_name: str
    github_login: str
    weight: int


@dataclass(frozen=True)
class AutoReportGate:
    allowed: bool
    reasons: tuple[str, ...]
    repository_status: str
    repository_message: str
    official_remote: bool
    current: bool
    clean_worktree: bool
    behind: int
    branch: str
    authenticated_github_user: str
    project_user: ReportIdentity | None
    permission_decision: str


@dataclass(frozen=True)
class DuplicateSummary:
    found: bool
    issue_number: int | None = None
    issue_url: str = ""
    issue_title: str = ""
    issue_state: str = ""
    original_reporter: str = ""
    reporters: tuple[str, ...] = ()
    report_count: int = 0
    match_type: str = ""


@dataclass(frozen=True)
class AutoReportResult:
    status: str
    fingerprint: str
    title: str
    github_login: str
    project_user_id: str
    issue_number: int | None
    issue_url: str
    duplicate: bool
    report_count: int
    reporters: tuple[str, ...]
    message: str
    checked_at: str


def _run_json(runner: CommandRunner, args: Sequence[str]) -> object:
    result = runner(args)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "GitHub-Befehl fehlgeschlagen")
    try:
        return json.loads(result.stdout or "null")
    except json.JSONDecodeError as exc:
        raise RuntimeError("GitHub-Antwort ist kein gültiges JSON") from exc


def _project_user_for_login(project_path: str | Path, login: str):
    manager = load_manager(project_path)
    matches = [
        user for user in manager.user_management.users
        if user.github_login and user.github_login.casefold() == login.casefold()
    ]
    if len(matches) != 1:
        return manager, None
    return manager, matches[0]


def evaluate_auto_report_gate(
    project_path: str | Path,
    *,
    repository: VersionResult | None = None,
) -> AutoReportGate:
    repo = check_repository_version() if repository is None else repository
    reasons: list[str] = []
    if not repo.official_remote:
        reasons.append("Kein offizielles Repository; Forks oder andere Remotes dürfen nicht automatisch melden.")
    if repo.behind > 0:
        reasons.append(f"Lokaler Stand ist {repo.behind} Commit(s) veraltet.")
    if not repo.current:
        reasons.append(repo.message or "Repositorystand ist nicht freigegeben.")
    if not repo.authenticated_user:
        reasons.append("Kein mit gh authentifizierter GitHub-Benutzer vorhanden.")

    project_user = None
    permission_decision = "not_checked"
    if repo.authenticated_user:
        manager, user = _project_user_for_login(project_path, repo.authenticated_user)
        if user is None:
            reasons.append("Der GitHub-Benutzer ist keinem eindeutigen ProjectOS-Benutzer zugeordnet.")
        else:
            project_user = ReportIdentity(
                user_id=user.user_id,
                display_name=user.display_name,
                github_login=user.github_login or "",
                weight=user.weight,
            )
            state = manager.user_management
            auth = ProjectOSAuthorizationEvaluator(
                state.permission_assignments,
                state.permission_revocations,
                state.user_deactivations,
                state.user_reactivations,
            ).evaluate(user, AUTO_PERMISSION, scope="project")
            permission_decision = str(auth["decision"])
            if not auth["allowed"]:
                reasons.append(
                    f"ProjectOS-Recht {AUTO_PERMISSION} ist nicht erlaubt ({permission_decision})."
                )
    return AutoReportGate(
        allowed=not reasons,
        reasons=tuple(dict.fromkeys(reasons)),
        repository_status=repo.status,
        repository_message=repo.message,
        official_remote=repo.official_remote,
        current=repo.current,
        clean_worktree=repo.clean_worktree,
        behind=repo.behind,
        branch=repo.branch,
        authenticated_github_user=repo.authenticated_user,
        project_user=project_user,
        permission_decision=permission_decision,
    )


def read_report(path: str | Path) -> str:
    source = Path(path)
    data = source.read_bytes()
    if len(data) > MAX_REPORT_BYTES:
        raise ValueError("Fehlerbericht ist größer als 64 KiB")
    text = data.decode("utf-8").strip()
    if not text:
        raise ValueError("Fehlerbericht ist leer")
    for pattern in _SECRET_PATTERNS:
        if pattern.search(text):
            raise PermissionError("Fehlerbericht enthält ein mögliches Geheimnis/Zugangstoken und wird nicht automatisch gesendet")
    return text


def _field(report: str, label: str) -> str:
    match = re.search(rf"(?mi)^-\s*{re.escape(label)}:\s*(.+?)\s*$", report)
    return match.group(1).strip() if match else ""


def report_title(report: str) -> str:
    match = re.search(r"(?m)^#\s+Fehlerbericht:\s*(.+?)\s*$", report)
    value = match.group(1).strip() if match else "Fehlerbericht"
    return value[:180]


def _normalized(value: str) -> str:
    return re.sub(r"\s+", " ", str(value).casefold()).strip()


def report_fingerprint(report: str) -> str:
    title = _normalized(report_title(report))
    category = _normalized(_field(report, "Kategorie"))
    reference = _normalized(_field(report, "Technische Referenz"))
    canonical = "\n".join((category, reference, title))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _list_issues(query: str, runner: CommandRunner) -> list[dict]:
    data = _run_json(runner, [
        "gh", "issue", "list", "--repo", OFFICIAL_REPOSITORY,
        "--state", "all", "--search", query,
        "--json", "number,title,state,author,createdAt,url,body", "--limit", "100",
    ])
    if not isinstance(data, list):
        raise RuntimeError("GitHub-Issue-Suche lieferte kein Array")
    return [item for item in data if isinstance(item, dict)]


def _issue_rows(
    fingerprint: str,
    runner: CommandRunner,
    *,
    title: str = "",
    reference: str = "",
) -> tuple[list[dict], str]:
    marker = f"z-report fingerprint={fingerprint}"
    marked = [
        item for item in _list_issues(marker, runner)
        if marker in str(item.get("body", ""))
    ]
    if marked:
        return marked, "fingerprint"

    # Bereits manuell angelegte Issues besitzen noch keinen ProjectOS-Marker.
    # Deshalb erfolgt eine konservative zweite Suche: Titel muss normalisiert exakt
    # übereinstimmen; eine vorhandene technische Referenz muss zusätzlich im Titel
    # oder Body vorkommen. So wird ein ähnlicher Fehler nicht vorschnell zusammengelegt.
    normalized_title = _normalized(title)
    if not normalized_title:
        return [], ""
    manual_candidates = _list_issues(f'"{title[:180]}" in:title', runner)
    normalized_reference = _normalized(reference)
    manual: list[dict] = []
    for item in manual_candidates:
        if _normalized(str(item.get("title", ""))) != normalized_title:
            continue
        if normalized_reference:
            haystack = _normalized(f"{item.get('title', '')} {item.get('body', '')}")
            if normalized_reference not in haystack:
                continue
        manual.append(item)
    return manual, "manual_title_reference" if manual else ""


def duplicate_summary(
    fingerprint: str,
    *,
    title: str = "",
    reference: str = "",
    runner: CommandRunner = run_command,
) -> DuplicateSummary:
    rows, match_type = _issue_rows(
        fingerprint,
        runner,
        title=title,
        reference=reference,
    )
    if not rows:
        return DuplicateSummary(found=False)
    rows.sort(key=lambda item: int(item.get("number", 0)))
    issue = rows[0]
    body = str(issue.get("body", ""))
    marker = _REPORT_MARKER_RE.search(body)
    original_reporter = marker.group(2) if marker else str((issue.get("author") or {}).get("login", ""))
    number = int(issue.get("number", 0))
    comments_data = _run_json(runner, [
        "gh", "issue", "view", str(number), "--repo", OFFICIAL_REPOSITORY,
        "--json", "comments",
    ])
    comments = comments_data.get("comments", []) if isinstance(comments_data, dict) else []
    duplicate_reporters: list[str] = []
    for comment in comments if isinstance(comments, list) else []:
        if not isinstance(comment, dict):
            continue
        match = _DUP_MARKER_RE.search(str(comment.get("body", "")))
        if match and match.group(1) == fingerprint:
            duplicate_reporters.append(match.group(2))
    reporters = tuple(dict.fromkeys([value for value in (original_reporter, *duplicate_reporters) if value]))
    return DuplicateSummary(
        found=True,
        issue_number=number,
        issue_url=str(issue.get("url", "")),
        issue_title=str(issue.get("title", "")),
        issue_state=str(issue.get("state", "")),
        original_reporter=original_reporter,
        reporters=reporters,
        report_count=1 + len(duplicate_reporters),
        match_type=match_type,
    )


def _write_result(result: AutoReportResult, path: str | Path = DEFAULT_RESULT_PATH) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(asdict(result), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def submit_auto_report(
    project_path: str | Path,
    report_path: str | Path,
    *,
    runner: CommandRunner = run_command,
    result_path: str | Path = DEFAULT_RESULT_PATH,
) -> AutoReportResult:
    # Repository- und Benutzerprüfung wird unmittelbar vor dem GitHub-Schreibzugriff neu ausgeführt.
    gate = evaluate_auto_report_gate(project_path)
    if not gate.allowed or gate.project_user is None:
        raise PermissionError("Automatische GitHub-Meldung gesperrt: " + "; ".join(gate.reasons))
    report = read_report(report_path)
    fingerprint = report_fingerprint(report)
    title = report_title(report)
    reference = _field(report, "Technische Referenz")
    duplicate = duplicate_summary(
        fingerprint,
        title=title,
        reference=reference,
        runner=runner,
    )
    login = gate.authenticated_github_user
    timestamp = datetime.now(timezone.utc).isoformat()

    if duplicate.found and duplicate.issue_number is not None:
        comment = (
            f"Erneut automatisch gemeldet durch ProjectOS von **{login}**.\n\n"
            f"- Fingerprint: `{fingerprint}`\n"
            f"- Zeitpunkt (UTC): `{timestamp}`\n"
            f"- ProjectOS-Benutzer: `{gate.project_user.user_id}`\n"
            f"- Dublettenabgleich: `{duplicate.match_type or 'fingerprint'}`\n\n"
            f"<!-- z-duplicate-report fingerprint={fingerprint} reporter={login} -->"
        )
        result = runner([
            "gh", "issue", "comment", str(duplicate.issue_number), "--repo", OFFICIAL_REPOSITORY,
            "--body", comment,
        ])
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "Dublettenkommentar konnte nicht gesendet werden")
        reporters = tuple(dict.fromkeys((*duplicate.reporters, login)))
        final = AutoReportResult(
            status="duplicate_reported",
            fingerprint=fingerprint,
            title=title,
            github_login=login,
            project_user_id=gate.project_user.user_id,
            issue_number=duplicate.issue_number,
            issue_url=duplicate.issue_url,
            duplicate=True,
            report_count=duplicate.report_count + 1,
            reporters=reporters,
            message=f"Fehler war bereits als Issue #{duplicate.issue_number} gemeldet; Wiederholungsmeldung wurde ergänzt.",
            checked_at=timestamp,
        )
        _write_result(final, result_path)
        return final

    marker = f"<!-- z-report fingerprint={fingerprint} reporter={login} -->"
    body = report.rstrip() + "\n\n## ProjectOS-Meldekennung\n\n" + (
        f"- Fingerprint: `{fingerprint}`\n"
        f"- Automatischer Reporter: `{login}`\n"
        f"- ProjectOS-Benutzer-ID: `{gate.project_user.user_id}`\n"
        f"- Zeitpunkt (UTC): `{timestamp}`\n\n{marker}\n"
    )
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".md", delete=False) as handle:
        temp = Path(handle.name)
        handle.write(body)
    try:
        result = runner([
            "gh", "issue", "create", "--repo", OFFICIAL_REPOSITORY,
            "--title", title, "--body-file", str(temp),
        ])
    finally:
        temp.unlink(missing_ok=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "GitHub-Issue konnte nicht erstellt werden")
    url = result.stdout.strip().splitlines()[-1].strip() if result.stdout.strip() else ""
    number_match = re.search(r"/(\d+)(?:\?.*)?$", url)
    number = int(number_match.group(1)) if number_match else None
    final = AutoReportResult(
        status="created",
        fingerprint=fingerprint,
        title=title,
        github_login=login,
        project_user_id=gate.project_user.user_id,
        issue_number=number,
        issue_url=url,
        duplicate=False,
        report_count=1,
        reporters=(login,),
        message="Neues GitHub-Issue wurde automatisch erstellt.",
        checked_at=timestamp,
    )
    _write_result(final, result_path)
    return final
