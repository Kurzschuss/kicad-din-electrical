from __future__ import annotations

from dataclasses import dataclass
from html import escape
import json
from pathlib import Path
from typing import Iterable

import projectos

from tools.validate_device_catalog import REPO_ROOT

from .diagnostics_page import DiagnosticEntry, DiagnosticsSnapshot, collect_diagnostics
from .project_model import ProjectState, load_project_state
from .security_status import SecurityItem, collect_security_status


VERSION_RESULT_PATH = REPO_ROOT / "build" / "VERSIONSPRUEFUNG.json"
GITHUB_ISSUE_URL = "https://github.com/Kurzschuss/kicad-din-electrical/issues/new?template=bug_report.yml"


@dataclass(frozen=True)
class RepositoryReportState:
    available: bool
    status: str
    current: bool
    message: str
    local_commit: str = ""
    branch: str = ""
    ahead: int = 0
    behind: int = 0
    official_remote: bool = False
    clean_worktree: bool = False
    developer_mode: bool = False
    developer_authorized: bool = False


@dataclass(frozen=True)
class IssueReportSnapshot:
    project_name: str
    target_release: str
    projectos_version: str
    diagnostics: tuple[DiagnosticEntry, ...]
    diagnostic_error_count: int
    diagnostic_warning_count: int
    security_items: tuple[SecurityItem, ...]
    repository: RepositoryReportState


_CATEGORIES = (
    "Allgemeiner Programmfehler",
    "Z_Cockpit-Oberfläche",
    "Gerätedaten",
    "Symbol",
    "Footprint",
    "Vorschau / 3D",
    "Projektvalidator / Qualität",
    "Benutzer / Berechtigungen",
    "Sicherheit",
    "Dokumentation",
)


def load_repository_report_state(path: Path = VERSION_RESULT_PATH) -> RepositoryReportState:
    """Liest nur das Ergebnis der expliziten Repositoryprüfung; führt selbst keinen Netzwerkzugriff aus."""
    if not path.is_file():
        return RepositoryReportState(
            available=False,
            status="nicht_geprueft",
            current=False,
            message="Repositoryprüfung wurde noch nicht ausgeführt.",
        )
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return RepositoryReportState(
            available=False,
            status="ungueltig",
            current=False,
            message="Repositoryprüfergebnis konnte nicht gelesen werden.",
        )
    return RepositoryReportState(
        available=True,
        status=str(data.get("status", "unbekannt")),
        current=bool(data.get("current", False)),
        message=str(data.get("message", "")),
        local_commit=str(data.get("local_commit", "")),
        branch=str(data.get("branch", "")),
        ahead=int(data.get("ahead", 0) or 0),
        behind=int(data.get("behind", 0) or 0),
        official_remote=bool(data.get("official_remote", False)),
        clean_worktree=bool(data.get("clean_worktree", False)),
        developer_mode=bool(data.get("developer_mode", False)),
        developer_authorized=bool(data.get("developer_authorized", False)),
    )


def collect_issue_report(
    *,
    diagnostics: DiagnosticsSnapshot | None = None,
    security_items: Iterable[SecurityItem] | None = None,
    project: ProjectState | None = None,
    version_result_path: Path = VERSION_RESULT_PATH,
) -> IssueReportSnapshot:
    diagnostic_state = collect_diagnostics() if diagnostics is None else diagnostics
    security_state = tuple(collect_security_status() if security_items is None else security_items)
    project_state = load_project_state() if project is None else project
    return IssueReportSnapshot(
        project_name=project_state.display_name,
        target_release=project_state.target_release,
        projectos_version=projectos.__version__,
        diagnostics=diagnostic_state.entries,
        diagnostic_error_count=diagnostic_state.error_count,
        diagnostic_warning_count=diagnostic_state.warning_count,
        security_items=security_state,
        repository=load_repository_report_state(version_result_path),
    )


def _options(values: Iterable[str]) -> str:
    return "".join(
        f'<option value="{escape(value, quote=True)}">{escape(value)}</option>'
        for value in values
    )


def _context_payload(snapshot: IssueReportSnapshot) -> dict[str, object]:
    diagnostics = [
        {
            "severity": item.severity,
            "source": item.source,
            "code": item.code,
            "area": item.area,
            "reference": item.reference,
            "message": item.message_de,
        }
        for item in snapshot.diagnostics[:25]
    ]
    security = [
        {
            "id": item.security_id,
            "label": item.label_de,
            "state": item.state,
            "detail": item.detail_de,
        }
        for item in snapshot.security_items
    ]
    repository = {
        "available": snapshot.repository.available,
        "status": snapshot.repository.status,
        "current": snapshot.repository.current,
        "message": snapshot.repository.message,
        "local_commit": snapshot.repository.local_commit,
        "branch": snapshot.repository.branch,
        "ahead": snapshot.repository.ahead,
        "behind": snapshot.repository.behind,
        "official_remote": snapshot.repository.official_remote,
        "clean_worktree": snapshot.repository.clean_worktree,
        "developer_mode": snapshot.repository.developer_mode,
        "developer_authorized": snapshot.repository.developer_authorized,
    }
    return {
        "project": {
            "name": snapshot.project_name,
            "target_release": snapshot.target_release,
            "projectos_version": snapshot.projectos_version,
            "cockpit_version": "1.1",
        },
        "diagnostics": diagnostics,
        "diagnostic_total": len(snapshot.diagnostics),
        "diagnostic_errors": snapshot.diagnostic_error_count,
        "diagnostic_warnings": snapshot.diagnostic_warning_count,
        "security": security,
        "repository": repository,
        "github_issue_url": GITHUB_ISSUE_URL,
    }


def issue_report_page_html(snapshot: IssueReportSnapshot | None = None) -> str:
    """Rendert einen lokalen, datensparsamen Fehlerbericht- und GitHub-Vorbereitungsworkflow."""
    state = collect_issue_report() if snapshot is None else snapshot
    context_json = json.dumps(_context_payload(state), ensure_ascii=False).replace("</", "<\\/")
    repository_label = "bereit" if state.repository.current else "gesperrt"
    repository_detail = state.repository.message or "Kein Detail verfügbar."

    return (
        '<style>'
        '#page-fehlerbericht.active{position:absolute;inset:0;display:flex;flex-direction:column;min-height:0;overflow:hidden;padding:0}'
        '.issue-report-workspace{display:grid;grid-template-columns:minmax(0,1fr) 430px;height:100%;min-height:0;overflow:hidden}'
        '.issue-report-main{min-width:0;min-height:0;padding:1rem;display:flex;flex-direction:column;overflow:hidden}'
        '.issue-report-main>.cockpit-page-title{margin:0 0 .8rem}'
        '.issue-report-scroll{min-height:0;overflow:auto;padding-right:.35rem;scrollbar-gutter:stable}'
        '.issue-report-grid{display:grid;grid-template-columns:repeat(2,minmax(180px,1fr));gap:.7rem}'
        '.issue-report-grid .wide{grid-column:1/-1}'
        '.issue-report-grid input,.issue-report-grid select,.issue-report-grid textarea{width:100%;padding:.5rem;font:inherit}'
        '.issue-report-grid textarea{min-height:92px;resize:vertical}'
        '.issue-report-context{margin-top:1rem;border:1px solid #8886;border-radius:.45rem;padding:.8rem}'
        '.issue-report-context h3{margin:.1rem 0 .65rem}'
        '.issue-report-checks{display:grid;gap:.45rem}'
        '.issue-report-checks label{display:flex;grid-template-columns:none;align-items:flex-start;gap:.5rem;font-size:.9rem}'
        '.issue-report-checks input{margin-top:.2rem}'
        '.issue-report-privacy{margin-top:1rem;padding:.75rem;border:1px solid #c58a0088;border-left:5px solid #c58a00;border-radius:.4rem}'
        '.issue-report-repository{margin-top:.8rem;padding:.7rem;border:1px solid #8886;border-radius:.4rem}'
        '.issue-report-repository[data-ready="true"]{border-left:5px solid #2e8b57}'
        '.issue-report-repository[data-ready="false"]{border-left:5px solid #b33a3a}'
        '.issue-report-inspector{min-width:0;min-height:0;height:100%;padding:1rem;display:flex;flex-direction:column;overflow:hidden;border-left:1px solid #8886}'
        '.issue-report-inspector>h2{margin:0 0 .6rem;flex:0 0 auto}'
        '#issue-report-preview{width:100%;min-height:0;flex:1 1 auto;resize:none;padding:.7rem;font:12px/1.45 ui-monospace,SFMono-Regular,Consolas,monospace;white-space:pre-wrap}'
        '.issue-report-actions{display:grid;grid-template-columns:1fr 1fr;gap:.55rem;margin-top:.7rem;flex:0 0 auto}'
        '.issue-report-actions button{padding:.6rem;cursor:pointer}'
        '.issue-report-confirm{display:flex;align-items:flex-start;gap:.5rem;margin-top:.7rem;font-size:.88rem}'
        '.issue-report-status{margin:.55rem 0 0;font-size:.86rem;min-height:1.2em}'
        '@media(max-width:1050px){.issue-report-workspace{grid-template-columns:1fr}.issue-report-inspector{height:45vh;border-left:0;border-top:1px solid #8886}.issue-report-grid{grid-template-columns:1fr}}'
        '</style>'
        '<section class="page" id="page-fehlerbericht">'
        '<div class="issue-report-workspace"><div class="issue-report-main">'
        '<h2 class="cockpit-page-title">Fehler melden <span class="cockpit-page-description">(strukturierter Bericht und GitHub-Issue-Vorbereitung)</span></h2>'
        '<div class="issue-report-scroll">'
        '<div class="issue-report-grid">'
        f'<label>Kategorie<select id="issue-report-category">{_options(_CATEGORIES)}</select></label>'
        '<label>Technische Referenz<input id="issue-report-reference" placeholder="z. B. Geräte-ID, Symbol, Footprint oder PRJ-Code"></label>'
        '<label class="wide">Kurztitel<input id="issue-report-title" placeholder="Kurze, eindeutige Fehlerbeschreibung"></label>'
        '<label class="wide">Beschreibung<textarea id="issue-report-description" placeholder="Was ist passiert?"></textarea></label>'
        '<label class="wide">Schritte zur Reproduktion<textarea id="issue-report-steps" placeholder="1. ...&#10;2. ..."></textarea></label>'
        '<label>Erwartetes Verhalten<textarea id="issue-report-expected"></textarea></label>'
        '<label>Tatsächliches Verhalten<textarea id="issue-report-actual"></textarea></label>'
        '</div>'
        '<section class="issue-report-context"><h3>Technische Informationen</h3>'
        '<div class="issue-report-checks">'
        '<label><input type="checkbox" id="issue-include-project" checked>Projekt-/ProjectOS-Version und Zielrelease aufnehmen</label>'
        '<label><input type="checkbox" id="issue-include-diagnostics" checked>Diagnosezusammenfassung und relevante Prüf-/Analysecodes aufnehmen</label>'
        '<label><input type="checkbox" id="issue-include-security" checked>Sicherheitsstatus ohne Benutzer- oder Zugangsdaten aufnehmen</label>'
        '<label><input type="checkbox" id="issue-include-repository" checked>Ergebnis der expliziten Repositoryprüfung aufnehmen</label>'
        '</div></section>'
        f'<div class="issue-report-repository" data-ready="{str(state.repository.current).lower()}"><strong>GitHub-Meldung: {repository_label}</strong><br>{escape(repository_detail)}'
        '<br><small>Die Repositoryprüfung wird mit <code>python -m tools.check_repository_version</code> erzeugt. Der Windows-Z_Cockpit-Starter führt sie automatisch vor dem Öffnen aus.</small></div>'
        '<div class="issue-report-privacy"><strong>Datenschutz:</strong> Benutzer-/Berechtigungsbestände, Passwörter, Tokens, Schlüssel und ungeprüfte Dateiinhalte werden nicht automatisch übernommen. Die Vorschau rechts ist der einzige Inhalt, der kopiert oder als Datei gespeichert wird.</div>'
        '</div></div>'
        '<section class="issue-report-inspector"><h2>Berichtsvorschau</h2>'
        '<textarea id="issue-report-preview" aria-label="Fehlerbericht Vorschau"></textarea>'
        '<label class="issue-report-confirm"><input type="checkbox" id="issue-confirm-review">Ich habe den Bericht geprüft und sensible bzw. unnötige Angaben entfernt.</label>'
        '<div class="issue-report-actions">'
        '<button type="button" id="issue-report-refresh">Bericht aktualisieren</button>'
        '<button type="button" id="issue-report-copy">Kopieren</button>'
        '<button type="button" id="issue-report-download">Als .md speichern</button>'
        '<button type="button" id="issue-report-github" disabled>GitHub-Issue vorbereiten</button>'
        '</div><p class="issue-report-status" id="issue-report-status"></p></section>'
        '</div>'
        f'<script type="application/json" id="issue-report-context">{context_json}</script>'
        '</section>'
        '<script type="text/javascript">(()=>{'
        'const root=document.getElementById("page-fehlerbericht");if(!root)return;'
        'const ctx=JSON.parse(document.getElementById("issue-report-context").textContent);'
        'const q=id=>document.getElementById(id);const preview=q("issue-report-preview");const confirm=q("issue-confirm-review");const github=q("issue-report-github");const status=q("issue-report-status");'
        'let previousPage="Start";document.querySelectorAll(".page-link").forEach(button=>button.addEventListener("click",()=>{if(button.dataset.page==="fehlerbericht"){const active=document.querySelector(".page.active");if(active&&active.id!=="page-fehlerbericht")previousPage=active.id.replace("page-","");}}));'
        'function value(id){return q(id).value.trim();}function checked(id){return q(id).checked;}'
        'function section(title,text){return text?`## ${title}\n\n${text}\n\n`:"";}'
        'function build(){let out=`# Fehlerbericht: ${value("issue-report-title")||"Ohne Titel"}\n\n`;out+=`- Kategorie: ${value("issue-report-category")}\n- Cockpit-Kontext: ${previousPage}\n`;if(value("issue-report-reference"))out+=`- Technische Referenz: ${value("issue-report-reference")}\n`;out+="\n";out+=section("Beschreibung",value("issue-report-description"));out+=section("Schritte zur Reproduktion",value("issue-report-steps"));out+=section("Erwartetes Verhalten",value("issue-report-expected"));out+=section("Tatsächliches Verhalten",value("issue-report-actual"));'
        'if(checked("issue-include-project")){out+="## Projektstand\n\n";out+=`- Projekt: ${ctx.project.name}\n- ProjectOS: ${ctx.project.projectos_version}\n- Z_Cockpit: ${ctx.project.cockpit_version}\n- Zielrelease: ${ctx.project.target_release}\n\n`;}'
        'if(checked("issue-include-diagnostics")){out+="## Diagnose\n\n";out+=`- Fehler: ${ctx.diagnostic_errors}\n- Warnungen: ${ctx.diagnostic_warnings}\n`;ctx.diagnostics.forEach(item=>{out+=`- [${item.code}] ${item.area} · ${item.reference}: ${item.message}\n`;});if(ctx.diagnostic_total>ctx.diagnostics.length)out+=`- Weitere Befunde nicht eingebettet: ${ctx.diagnostic_total-ctx.diagnostics.length}\n`;out+="\n";}'
        'if(checked("issue-include-security")){out+="## Sicherheitsstatus\n\n";ctx.security.forEach(item=>{out+=`- ${item.label}: ${item.state} — ${item.detail}\n`;});out+="\n";}'
        'if(checked("issue-include-repository")){const r=ctx.repository;out+="## Repositoryprüfung\n\n";out+=`- Status: ${r.status}\n- Meldung: ${r.message}\n`;if(r.branch)out+=`- Branch: ${r.branch}\n`;if(r.local_commit)out+=`- Commit: ${r.local_commit}\n`;out+=`- Offizielles Remote: ${r.official_remote?"ja":"nein"}\n- Arbeitskopie sauber: ${r.clean_worktree?"ja":"nein"}\n- Ahead/Behind: ${r.ahead}/${r.behind}\n\n`;}'
        'out+="## Datenschutzprüfung\n\nDer Bericht wurde vor der Weitergabe im Z_Cockpit sichtbar geprüft. Benutzer-/Berechtigungsbestände, Tokens, Schlüssel und Zugangsdaten wurden nicht automatisch aufgenommen.\n";preview.value=out;update();return out;}'
        'function update(){github.disabled=!(confirm.checked&&ctx.repository.current&&value("issue-report-title")&&value("issue-report-description"));}'
        '["issue-report-category","issue-report-reference","issue-report-title","issue-report-description","issue-report-steps","issue-report-expected","issue-report-actual","issue-include-project","issue-include-diagnostics","issue-include-security","issue-include-repository"].forEach(id=>q(id).addEventListener("input",build));confirm.addEventListener("change",update);q("issue-report-refresh").addEventListener("click",build);'
        'q("issue-report-copy").addEventListener("click",async()=>{try{await navigator.clipboard.writeText(preview.value);status.textContent="Bericht wurde in die Zwischenablage kopiert.";}catch(_){preview.select();document.execCommand("copy");status.textContent="Bericht wurde kopiert.";}});'
        'q("issue-report-download").addEventListener("click",()=>{const blob=new Blob([preview.value],{type:"text/markdown;charset=utf-8"});const url=URL.createObjectURL(blob);const a=document.createElement("a");a.href=url;a.download="z-cockpit-fehlerbericht.md";a.click();URL.revokeObjectURL(url);status.textContent="Lokaler Markdown-Bericht wurde erzeugt.";});'
        'github.addEventListener("click",async()=>{if(github.disabled)return;try{await navigator.clipboard.writeText(preview.value);}catch(_){}const title=encodeURIComponent(value("issue-report-title"));window.open(`${ctx.github_issue_url}&title=${title}`,"_blank","noopener");status.textContent="Bericht kopiert; GitHub-Issue-Formular wurde geöffnet. Das Absenden erfolgt dort ausdrücklich durch den Benutzer.";});'
        'preview.addEventListener("input",update);build();'
        '})();</script>'
    )
