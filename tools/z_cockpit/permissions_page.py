from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from html import escape
import json
from pathlib import Path
from typing import Iterable

from distributions.projectos_authorization import ProjectOSAuthorizationEvaluator
from distributions.projectos_project_bundle_v4 import load_projectos_bundle_details
from distributions.projectos_user_management_persistence import ProjectOSUserManagementState
from tools.validate_device_catalog import REPO_ROOT


DEVELOPER_WHITELIST_PATH = REPO_ROOT / "config" / "authorized_developers.json"

_SOURCE_LABELS = {
    "role": "Rolle",
    "direct": "Direkte Zuweisung",
    "delegation": "Delegation",
    "deny": "DENY",
    "exception": "Ausnahme",
    "whitelist": "Whitelist",
    "blacklist": "Blacklist",
}
_EFFECT_LABELS = {"allow": "Erlauben", "deny": "Sperren"}
_DECISION_LABELS = {
    "allow": "Erlaubt",
    "deny": "Verweigert",
    "not_granted": "Nicht erteilt",
    "user_deactivated": "Benutzer deaktiviert",
}
_STATUS_LABELS = {
    "active": "Aktiv",
    "scheduled": "Geplant",
    "expired": "Abgelaufen",
    "revoked": "Widerrufen",
}


@dataclass(frozen=True)
class RepositoryDeveloperWhitelist:
    source_path: str
    schema_version: int | None
    github_users: tuple[str, ...]
    available: bool


@dataclass(frozen=True)
class PermissionAssignmentView:
    assignment_id: str
    user_id: str
    user_name: str
    permission: str
    source_type: str
    source_label: str
    effect: str
    effect_label: str
    scope: str
    risk_class: str
    valid_from: str | None
    valid_until: str | None
    source_reference: str | None
    status: str
    status_label: str
    effective_decision: str
    effective_decision_label: str
    effective_sources: tuple[str, ...]


@dataclass(frozen=True)
class PermissionsSnapshot:
    project_id: str | None
    assignments: tuple[PermissionAssignmentView, ...]
    developer_whitelist: RepositoryDeveloperWhitelist
    source_available: bool
    source_label: str
    evaluated_at: str
    read_only: bool = True

    @property
    def whitelist_count(self) -> int:
        return sum(item.source_type == "whitelist" for item in self.assignments)

    @property
    def blacklist_count(self) -> int:
        return sum(item.source_type in {"blacklist", "deny"} for item in self.assignments)

    @property
    def exception_count(self) -> int:
        return sum(item.source_type == "exception" for item in self.assignments)


def load_repository_developer_whitelist(
    path: str | Path = DEVELOPER_WHITELIST_PATH,
) -> RepositoryDeveloperWhitelist:
    source = Path(path)
    if not source.is_file():
        return RepositoryDeveloperWhitelist(
            source_path=str(source), schema_version=None, github_users=(), available=False
        )
    try:
        data = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"Entwickler-Whitelist kann nicht gelesen werden: {source}") from exc
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        raise ValueError("Entwickler-Whitelist: nicht unterstützte schema_version")
    users = data.get("github_users")
    if not isinstance(users, list) or any(not isinstance(item, str) or not item.strip() for item in users):
        raise ValueError("Entwickler-Whitelist: github_users muss eine Liste nicht leerer Texte sein")
    normalized = tuple(dict.fromkeys(item.strip() for item in users))
    return RepositoryDeveloperWhitelist(
        source_path=str(source), schema_version=1, github_users=normalized, available=True
    )


def _assignment_status(assignment, revoked: bool, current: datetime) -> str:
    if revoked:
        return "revoked"
    if assignment.valid_from and current < datetime.fromisoformat(assignment.valid_from):
        return "scheduled"
    if assignment.valid_until and current > datetime.fromisoformat(assignment.valid_until):
        return "expired"
    return "active"


def collect_permissions(
    state: ProjectOSUserManagementState | None = None,
    *,
    source_label: str | None = None,
    at: datetime | None = None,
    developer_whitelist_path: str | Path = DEVELOPER_WHITELIST_PATH,
) -> PermissionsSnapshot:
    current = at or datetime.now(timezone.utc)
    if current.tzinfo is None or current.utcoffset() is None:
        raise ValueError("Auswertungszeitpunkt muss eine Zeitzone enthalten")
    current = current.astimezone(timezone.utc)
    developer_whitelist = load_repository_developer_whitelist(developer_whitelist_path)

    if state is None:
        return PermissionsSnapshot(
            project_id=None,
            assignments=(),
            developer_whitelist=developer_whitelist,
            source_available=False,
            source_label=source_label or "Keine ProjectOS-Projektdatei angebunden",
            evaluated_at=current.isoformat(),
        )

    users = {item.user_id: item for item in state.users}
    evaluator = ProjectOSAuthorizationEvaluator(
        state.permission_assignments,
        state.permission_revocations,
        state.user_deactivations,
        state.user_reactivations,
    )
    effective_revocations = {
        item.assignment_id
        for item in state.permission_revocations
        if item.is_effective(current)
    }
    rows: list[PermissionAssignmentView] = []
    for assignment in state.permission_assignments:
        user = users.get(assignment.user_id)
        if user is None:
            raise ValueError("Berechtigungszuweisung referenziert unbekannte user_id")
        result = evaluator.evaluate(user, assignment.permission, scope=assignment.scope, at=current)
        status = _assignment_status(assignment, assignment.assignment_id in effective_revocations, current)
        effective_source_types = tuple(
            dict.fromkeys(str(item["source_type"]) for item in result["effective_sources"])
        )
        rows.append(
            PermissionAssignmentView(
                assignment_id=assignment.assignment_id,
                user_id=user.user_id,
                user_name=user.display_name,
                permission=assignment.permission,
                source_type=assignment.source_type,
                source_label=_SOURCE_LABELS.get(assignment.source_type, assignment.source_type),
                effect=assignment.effect,
                effect_label=_EFFECT_LABELS.get(assignment.effect, assignment.effect),
                scope=assignment.scope,
                risk_class=assignment.risk_class,
                valid_from=assignment.valid_from,
                valid_until=assignment.valid_until,
                source_reference=assignment.source_reference,
                status=status,
                status_label=_STATUS_LABELS[status],
                effective_decision=str(result["decision"]),
                effective_decision_label=_DECISION_LABELS.get(str(result["decision"]), str(result["decision"])),
                effective_sources=tuple(_SOURCE_LABELS.get(item, item) for item in effective_source_types),
            )
        )
    rows.sort(key=lambda item: (item.user_name.casefold(), item.permission.casefold(), item.source_label.casefold()))
    return PermissionsSnapshot(
        project_id=state.project_id,
        assignments=tuple(rows),
        developer_whitelist=developer_whitelist,
        source_available=True,
        source_label=source_label or "ProjectOSUserManagementState",
        evaluated_at=current.isoformat(),
    )


def load_permissions_bundle(
    path: str | Path,
    *,
    at: datetime | None = None,
    developer_whitelist_path: str | Path = DEVELOPER_WHITELIST_PATH,
) -> PermissionsSnapshot:
    source = Path(path)
    _, _, project_id, _, state = load_projectos_bundle_details(source)
    if state is None:
        return collect_permissions(
            source_label=f"{source} · keine Benutzerverwaltung enthalten",
            at=at,
            developer_whitelist_path=developer_whitelist_path,
        )
    if project_id is not None and state.project_id != project_id:
        raise ValueError("Benutzerverwaltung gehört zu einer anderen Projekt-ID")
    return collect_permissions(
        state,
        source_label=str(source),
        at=at,
        developer_whitelist_path=developer_whitelist_path,
    )


def _json_attr(values: Iterable[str]) -> str:
    return escape(json.dumps(tuple(values), ensure_ascii=False), quote=True)


def _options(values: Iterable[str]) -> str:
    return "".join(
        f'<option value="{escape(value, quote=True)}">{escape(value)}</option>'
        for value in values
    )


def _developer_whitelist_html(item: RepositoryDeveloperWhitelist) -> str:
    users = "".join(f'<li><code>{escape(user)}</code></li>' for user in item.github_users)
    if not users:
        users = '<li>Keine freigegebenen GitHub-Benutzer eingetragen.</li>'
    schema = str(item.schema_version) if item.schema_version is not None else "–"
    status = "Vorhanden" if item.available else "Fehlt"
    return (
        '<section class="permissions-developer-whitelist">'
        '<h3>Repository-Entwickler-Whitelist</h3>'
        '<dl class="permissions-properties">'
        f'<dt>Status</dt><dd>{status}</dd>'
        f'<dt>Schema</dt><dd>{escape(schema)}</dd>'
        f'<dt>Quelle</dt><dd><code>config/authorized_developers.json</code></dd>'
        f'<dt>Einträge</dt><dd>{len(item.github_users)}</dd>'
        '</dl>'
        f'<ul class="permissions-developer-users">{users}</ul>'
        '<p class="permissions-note"><strong>Getrennte Sicherheitsquelle:</strong> Diese Liste steuert '
        'repositorybezogene Entwicklerfreigaben und ist nicht die ProjectOS-Benutzer-Whitelist.</p>'
        '</section>'
    )


def _inspector_template(item: PermissionAssignmentView, index: int) -> str:
    effective_sources = ", ".join(item.effective_sources) if item.effective_sources else "–"
    return (
        f'<template id="permissions-inspector-{index}">'
        '<dl class="permissions-properties">'
        f'<dt>Benutzer</dt><dd>{escape(item.user_name)}</dd>'
        f'<dt>Benutzer-ID</dt><dd><code>{escape(item.user_id)}</code></dd>'
        f'<dt>Recht</dt><dd><code>{escape(item.permission)}</code></dd>'
        f'<dt>Zuweisungs-ID</dt><dd><code>{escape(item.assignment_id)}</code></dd>'
        f'<dt>Quelle</dt><dd>{escape(item.source_label)}</dd>'
        f'<dt>Wirkung</dt><dd>{escape(item.effect_label)}</dd>'
        f'<dt>Status</dt><dd>{escape(item.status_label)}</dd>'
        f'<dt>Effektive Entscheidung</dt><dd><strong>{escape(item.effective_decision_label)}</strong></dd>'
        f'<dt>Effektive Herkunft</dt><dd>{escape(effective_sources)}</dd>'
        f'<dt>Scope</dt><dd><code>{escape(item.scope)}</code></dd>'
        f'<dt>Risikoklasse</dt><dd>{escape(item.risk_class)}</dd>'
        f'<dt>Gültig ab</dt><dd>{escape(item.valid_from or "–")}</dd>'
        f'<dt>Gültig bis</dt><dd>{escape(item.valid_until or "–")}</dd>'
        f'<dt>Quellenreferenz</dt><dd>{escape(item.source_reference or "–")}</dd>'
        '</dl>'
        '<div class="permissions-note"><strong>Priorität:</strong> Ein wirksames DENY/Blacklist sperrt den Zugriff '
        'auch dann, wenn parallel eine Whitelist- oder andere ALLOW-Quelle existiert.</div>'
        '</template>'
    )


def permissions_page_html(snapshot: PermissionsSnapshot | None = None) -> str:
    state = collect_permissions() if snapshot is None else snapshot
    users = tuple(sorted({item.user_name for item in state.assignments}, key=str.casefold))
    sources = tuple(sorted({item.source_label for item in state.assignments}, key=str.casefold))
    effects = tuple(label for label in ("Erlauben", "Sperren") if any(item.effect_label == label for item in state.assignments))
    statuses = tuple(label for label in ("Aktiv", "Geplant", "Abgelaufen", "Widerrufen") if any(item.status_label == label for item in state.assignments))

    rows: list[str] = []
    templates: list[str] = []
    for index, item in enumerate(state.assignments):
        rows.append(
            f'<tr class="permissions-row" tabindex="0" data-index="{index}" '
            f'data-user="{escape(item.user_name, quote=True)}" '
            f'data-source="{escape(item.source_label, quote=True)}" '
            f'data-effect="{escape(item.effect_label, quote=True)}" '
            f'data-status="{escape(item.status_label, quote=True)}" '
            f'data-search="{escape((item.user_name + " " + item.user_id + " " + item.permission).casefold(), quote=True)}">'
            f'<th scope="row"><strong>{escape(item.user_name)}</strong><br><code>{escape(item.user_id)}</code></th>'
            f'<td><code>{escape(item.permission)}</code></td>'
            f'<td>{escape(item.source_label)}</td><td>{escape(item.effect_label)}</td>'
            f'<td>{escape(item.status_label)}</td><td>{escape(item.effective_decision_label)}</td></tr>'
        )
        templates.append(_inspector_template(item, index))

    if not rows:
        rows.append(
            '<tr><td colspan="6" class="permissions-empty">Keine ProjectOS-Berechtigungen geladen. '
            'Für echte Projektdaten das Z_Cockpit mit <code>--project-bundle &lt;projektdatei&gt;</code> erzeugen.</td></tr>'
        )

    source_state = "angebunden" if state.source_available else "nicht angebunden"
    return (
        '<style>'
        '#page-berechtigungen.active{position:absolute;inset:0;display:flex;flex-direction:column;min-height:0;overflow:hidden;padding:0}'
        '.permissions-workspace{display:grid;grid-template-columns:minmax(0,1fr) 400px;height:100%;min-height:0;overflow:hidden}'
        '.permissions-main{min-width:0;min-height:0;padding:1rem;display:flex;flex-direction:column;overflow:hidden}'
        '.permissions-main>.cockpit-page-title{margin:0 0 .85rem}'
        '.permissions-source{padding:.65rem .75rem;border:1px solid #8885;border-radius:.4rem;margin:0 0 .8rem;flex:0 0 auto;font-size:.9rem}'
        '.permissions-filters{display:grid;grid-template-columns:minmax(180px,2fr) repeat(4,minmax(125px,1fr));gap:.6rem;margin-bottom:.8rem;flex:0 0 auto}'
        '.permissions-table-wrap{min-height:0;overflow:auto;border:1px solid #8886;border-radius:.4rem;flex:1 1 auto}'
        '.permissions-table{width:100%;min-width:900px;border-collapse:collapse}'
        '.permissions-table th,.permissions-table td{padding:.55rem .65rem;border-bottom:1px solid #8884;text-align:left;white-space:nowrap}'
        '.permissions-table thead th{position:sticky;top:0;background:Canvas;z-index:2}'
        '.permissions-row{cursor:pointer}.permissions-row:hover{background:#2878c812}.permissions-row.selected{background:#2878c81f;font-weight:700}'
        '.permissions-inspector{min-height:0;overflow:auto;border-left:1px solid #8886;padding:1rem}'
        '.permissions-inspector>.cockpit-page-title{margin:0 0 .85rem}'
        '.permissions-properties{display:grid;grid-template-columns:minmax(120px,.9fr) minmax(0,1.4fr);gap:.45rem .7rem}'
        '.permissions-properties dt{font-weight:700}.permissions-properties dd{margin:0;overflow-wrap:anywhere}'
        '.permissions-note{padding:.7rem;border:1px solid #c58a0066;border-left:5px solid #c58a00;border-radius:.4rem;margin:.8rem 0;font-size:.9rem}'
        '.permissions-developer-whitelist{border-top:1px solid #8885;margin-top:1rem;padding-top:.9rem}'
        '.permissions-developer-whitelist h3{margin:.1rem 0 .65rem}.permissions-developer-users{margin:.5rem 0;padding-left:1.4rem}'
        '.permissions-change-path{border-top:1px solid #8885;margin-top:1rem;padding-top:.9rem;font-size:.9rem}'
        '.permissions-change-path h3{margin:.1rem 0 .5rem}.permissions-empty{white-space:normal!important;padding:1rem!important}'
        '@media(max-width:1050px){#page-berechtigungen.active{position:static;overflow:auto}.permissions-workspace{grid-template-columns:1fr;height:auto}.permissions-inspector{border-left:0;border-top:1px solid #8886}.permissions-filters{grid-template-columns:repeat(2,minmax(140px,1fr))}}'
        '</style>'
        '<section class="page" id="page-berechtigungen"><div class="permissions-workspace">'
        '<div class="permissions-main">'
        '<h2 class="cockpit-page-title">Berechtigungen <small class="cockpit-page-description">'
        '(ProjectOS-Whitelist, Blacklist und Ausnahmen; Repository-Entwickler-Whitelist strikt getrennt.)</small></h2>'
        f'<div class="permissions-source">ProjectOS-Quelle: <strong>{escape(state.source_label)}</strong> · {source_state} · '
        f'Whitelist {state.whitelist_count} · Blacklist/DENY {state.blacklist_count} · Ausnahmen {state.exception_count}</div>'
        '<div class="permissions-filters">'
        '<label>Suche<input id="permissions-filter-search" type="search" placeholder="Benutzer, ID oder Recht"></label>'
        f'<label>Benutzer<select id="permissions-filter-user"><option value="">Alle</option>{_options(users)}</select></label>'
        f'<label>Quelle<select id="permissions-filter-source"><option value="">Alle</option>{_options(sources)}</select></label>'
        f'<label>Wirkung<select id="permissions-filter-effect"><option value="">Alle</option>{_options(effects)}</select></label>'
        f'<label>Status<select id="permissions-filter-status"><option value="">Alle</option>{_options(statuses)}</select></label>'
        '</div>'
        '<div class="permissions-table-wrap"><table class="permissions-table" id="permissions-overview">'
        '<thead><tr><th>Benutzer</th><th>Recht</th><th>Quelle</th><th>Wirkung</th><th>Status</th><th>Effektiv</th></tr></thead>'
        f'<tbody>{"".join(rows)}</tbody></table></div></div>'
        '<aside class="permissions-inspector"><h2 class="cockpit-page-title">Eigenschaften</h2>'
        '<div id="permissions-inspector-content"><p>Bitte eine Berechtigungszuweisung auswählen.</p></div>'
        f'{_developer_whitelist_html(state.developer_whitelist)}'
        '<section class="permissions-change-path"><h3>Kontrollierte Änderungswege</h3>'
        '<p><strong>ProjectOS:</strong> Änderungen müssen über <code>ProjectOSUserManagementChangeService</code> '
        'und die fail-closed Command-Autorisierung laufen. Das statische Cockpit schreibt keine Rechte.</p>'
        '<p><strong>Repository:</strong> Änderungen an <code>config/authorized_developers.json</code> erfolgen als '
        'versionierte Repository-Änderung und werden anschließend durch Validatoren und CI geprüft.</p></section>'
        '</aside></div>'
        f'{"".join(templates)}'
        '</section>'
        '<script type="text/javascript">(()=>{'
        'const page=document.getElementById("page-berechtigungen");if(!page)return;'
        'const rows=[...page.querySelectorAll(".permissions-row")];'
        'const search=page.querySelector("#permissions-filter-search");const user=page.querySelector("#permissions-filter-user");'
        'const source=page.querySelector("#permissions-filter-source");const effect=page.querySelector("#permissions-filter-effect");'
        'const status=page.querySelector("#permissions-filter-status");const inspector=page.querySelector("#permissions-inspector-content");'
        'function select(row){rows.forEach(item=>item.classList.remove("selected"));row.classList.add("selected");'
        'const template=page.querySelector(`#permissions-inspector-${row.dataset.index}`);if(template)inspector.innerHTML=template.innerHTML}'
        'function filter(){const q=(search.value||"").trim().toLocaleLowerCase("de");rows.forEach(row=>{'
        'const visible=(!q||row.dataset.search.includes(q))&&(!user.value||row.dataset.user===user.value)&&'
        '(!source.value||row.dataset.source===source.value)&&(!effect.value||row.dataset.effect===effect.value)&&'
        '(!status.value||row.dataset.status===status.value);row.hidden=!visible});'
        'const current=rows.find(row=>row.classList.contains("selected")&&!row.hidden);if(!current){const first=rows.find(row=>!row.hidden);if(first)select(first)}}'
        '[search,user,source,effect,status].forEach(control=>control.addEventListener(control===search?"input":"change",filter));'
        'rows.forEach(row=>{row.addEventListener("click",()=>select(row));row.addEventListener("keydown",event=>{if(event.key==="Enter"||event.key===" "){event.preventDefault();select(row)}})});'
        'if(rows.length)select(rows[0]);filter();'
        '})();</script>'
    )
