from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Iterable

from distributions.projectos_authorization import (
    ProjectOSAuthorizationEvaluator,
    ProjectOSPermissionAssignment,
    ProjectOSUserProfile,
)
from distributions.projectos_project_bundle_v4 import load_projectos_bundle_details
from distributions.projectos_user_lifecycle import ProjectOSUserLifecycleEvaluator
from distributions.projectos_user_management_persistence import ProjectOSUserManagementState
from distributions.projectos_user_project_roles import ProjectOSUserProjectRoleRegistry


_ROLE_LABELS = {
    "project_lead": "Projektleiter",
    "deputy": "Stellvertretung",
    "trusted_person": "Vertrauensperson",
    "successor": "Nachfolger",
}
_SOURCE_LABELS = {
    "role": "Rolle",
    "direct": "Direkte Zuweisung",
    "delegation": "Delegation",
    "deny": "DENY",
    "exception": "Ausnahme",
    "whitelist": "Whitelist",
    "blacklist": "Blacklist",
}
_DECISION_LABELS = {
    "allow": "Erlaubt",
    "deny": "Verweigert",
    "not_granted": "Nicht erteilt",
    "user_deactivated": "Benutzer deaktiviert",
}
_LIFECYCLE_LABELS = {"active": "Aktiv", "deactivated": "Deaktiviert"}
_EVENT_LABELS = {"deactivated": "Deaktiviert", "reactivated": "Reaktiviert"}


@dataclass(frozen=True)
class UserPermissionView:
    permission: str
    decision: str
    decision_label: str
    sources: tuple[str, ...]
    source_types: tuple[str, ...]
    risk_classes: tuple[str, ...]
    active_assignment_count: int
    revoked_assignment_count: int


@dataclass(frozen=True)
class UserView:
    user_id: str
    display_name: str
    weight: int
    lifecycle_status: str
    status_label: str
    profile_roles: tuple[str, ...]
    project_roles: tuple[str, ...]
    project_role_labels: tuple[str, ...]
    permissions: tuple[UserPermissionView, ...]
    permission_states: tuple[str, ...]
    lifecycle_events: tuple[dict[str, object], ...]
    permission_assignment_count: int
    permission_revocation_count: int
    project_role_count: int

    @property
    def roles(self) -> tuple[str, ...]:
        return tuple(dict.fromkeys((*self.profile_roles, *self.project_role_labels)))

    @property
    def allowed_count(self) -> int:
        return sum(item.decision == "allow" for item in self.permissions)

    @property
    def denied_count(self) -> int:
        return sum(item.decision in {"deny", "user_deactivated"} for item in self.permissions)


@dataclass(frozen=True)
class UserManagementSnapshot:
    project_id: str | None
    users: tuple[UserView, ...]
    source_available: bool
    source_label: str
    evaluated_at: str
    read_only: bool = True

    @property
    def active_count(self) -> int:
        return sum(item.lifecycle_status == "active" for item in self.users)

    @property
    def deactivated_count(self) -> int:
        return sum(item.lifecycle_status == "deactivated" for item in self.users)

    @property
    def role_count(self) -> int:
        return len({role for item in self.users for role in item.roles})

    @property
    def permission_count(self) -> int:
        return len({permission.permission for item in self.users for permission in item.permissions})


def _role_label(role: str) -> str:
    return _ROLE_LABELS.get(role, role)


def _source_label(source_type: str) -> str:
    return _SOURCE_LABELS.get(source_type, source_type)


def _permissions_for_user(
    user: ProjectOSUserProfile,
    state: ProjectOSUserManagementState,
    evaluator: ProjectOSAuthorizationEvaluator,
    *,
    at: datetime,
) -> tuple[UserPermissionView, ...]:
    names = sorted(
        {
            assignment.permission
            for assignment in state.permission_assignments
            if assignment.user_id == user.user_id
        },
        key=str.casefold,
    )
    rows: list[UserPermissionView] = []
    for permission in names:
        result = evaluator.evaluate(user, permission, scope="project", at=at)
        effective = tuple(result["effective_sources"])
        source_types = tuple(
            dict.fromkeys(str(item["source_type"]) for item in effective)
        )
        sources = tuple(_source_label(item) for item in source_types)
        risk_classes = tuple(
            dict.fromkeys(str(item["risk_class"]) for item in effective)
        )
        decision = str(result["decision"])
        rows.append(
            UserPermissionView(
                permission=permission,
                decision=decision,
                decision_label=_DECISION_LABELS.get(decision, decision),
                sources=sources,
                source_types=source_types,
                risk_classes=risk_classes,
                active_assignment_count=len(result["active_assignments"]),
                revoked_assignment_count=int(result["revocation_count"]),
            )
        )
    return tuple(rows)


def collect_user_management(
    state: ProjectOSUserManagementState | None = None,
    *,
    source_label: str | None = None,
    at: datetime | None = None,
) -> UserManagementSnapshot:
    """Erzeugt eine read-only Cockpit-Sicht aus dem bestehenden ProjectOS-Zustand."""
    current = at or datetime.now(timezone.utc)
    if current.tzinfo is None or current.utcoffset() is None:
        raise ValueError("Auswertungszeitpunkt muss eine Zeitzone enthalten")
    current = current.astimezone(timezone.utc)

    if state is None:
        return UserManagementSnapshot(
            project_id=None,
            users=(),
            source_available=False,
            source_label=source_label or "Keine ProjectOS-Projektdatei angebunden",
            evaluated_at=current.isoformat(),
        )

    lifecycle = ProjectOSUserLifecycleEvaluator(
        deactivations=state.user_deactivations,
        reactivations=state.user_reactivations,
    )
    roles = ProjectOSUserProjectRoleRegistry(
        state.project_roles,
        state.role_assignment_terminations,
    )
    evaluator = ProjectOSAuthorizationEvaluator(
        state.permission_assignments,
        state.permission_revocations,
        state.user_deactivations,
        state.user_reactivations,
    )

    users: list[UserView] = []
    for user in sorted(state.users, key=lambda item: item.display_name.casefold()):
        lifecycle_state = lifecycle.state(user_id=user.user_id, at=current)
        role_state = roles.state(
            project_id=state.project_id,
            user=user,
            scope="project",
            at=current,
        )
        project_roles = tuple(str(item["role_type"]) for item in role_state["active_roles"])
        permissions = _permissions_for_user(user, state, evaluator, at=current)
        permission_states = tuple(dict.fromkeys(item.decision_label for item in permissions))
        users.append(
            UserView(
                user_id=user.user_id,
                display_name=user.display_name,
                weight=user.weight,
                lifecycle_status=str(lifecycle_state["status"]),
                status_label=_LIFECYCLE_LABELS[str(lifecycle_state["status"])],
                profile_roles=tuple(user.roles),
                project_roles=project_roles,
                project_role_labels=tuple(_role_label(role) for role in project_roles),
                permissions=permissions,
                permission_states=permission_states,
                lifecycle_events=tuple(lifecycle_state["event_history"]),
                permission_assignment_count=sum(
                    item.user_id == user.user_id for item in state.permission_assignments
                ),
                permission_revocation_count=sum(
                    item.user_id == user.user_id for item in state.permission_revocations
                ),
                project_role_count=len(role_state["active_roles"]),
            )
        )

    return UserManagementSnapshot(
        project_id=state.project_id,
        users=tuple(users),
        source_available=True,
        source_label=source_label or "ProjectOSUserManagementState",
        evaluated_at=current.isoformat(),
    )


def load_user_management_bundle(
    path: str | Path,
    *,
    at: datetime | None = None,
) -> UserManagementSnapshot:
    """Lädt explizit ein ProjectOS-v4-Projektbundle für die Cockpit-Ansicht."""
    source = Path(path)
    _, _, project_id, _, state = load_projectos_bundle_details(source)
    if state is None:
        return collect_user_management(
            source_label=f"{source} · keine Benutzerverwaltung enthalten",
            at=at,
        )
    if project_id is not None and state.project_id != project_id:
        raise ValueError("Benutzerverwaltung gehört zu einer anderen Projekt-ID")
    return collect_user_management(state, source_label=str(source), at=at)


def _json_attr(values: Iterable[str]) -> str:
    import json

    return escape(json.dumps(tuple(values), ensure_ascii=False), quote=True)


def _options(values: Iterable[str]) -> str:
    return "".join(
        f'<option value="{escape(value, quote=True)}">{escape(value)}</option>'
        for value in values
    )


def _permission_table(user: UserView) -> str:
    if not user.permissions:
        return '<p class="user-management-empty-detail">Keine Rechtezuweisungen für diesen Benutzer vorhanden.</p>'
    rows = []
    for item in user.permissions:
        sources = ", ".join(item.sources) if item.sources else "–"
        risks = ", ".join(item.risk_classes) if item.risk_classes else "–"
        rows.append(
            '<tr>'
            f'<th scope="row"><code>{escape(item.permission)}</code></th>'
            f'<td>{escape(item.decision_label)}</td>'
            f'<td>{escape(sources)}</td>'
            f'<td>{escape(risks)}</td>'
            f'<td>{item.active_assignment_count}</td>'
            f'<td>{item.revoked_assignment_count}</td>'
            '</tr>'
        )
    return (
        '<div class="user-management-permission-wrap"><table class="user-management-permission-table">'
        '<thead><tr><th>Recht</th><th>Entscheidung</th><th>Herkunft</th><th>Risiko</th>'
        '<th>Aktive Quellen</th><th>Widerrufe</th></tr></thead>'
        f'<tbody>{"".join(rows)}</tbody></table></div>'
    )


def _lifecycle_html(user: UserView) -> str:
    if not user.lifecycle_events:
        return '<p class="user-management-empty-detail">Keine Lifecycle-Ereignisse vorhanden.</p>'
    rows = []
    for item in user.lifecycle_events:
        event_type = str(item["event_type"])
        event = item["event"]
        reason = str(event.get("reason", "–")) if isinstance(event, dict) else "–"
        rows.append(
            '<li>'
            f'<strong>{escape(_EVENT_LABELS.get(event_type, event_type))}</strong> · '
            f'<time>{escape(str(item["timestamp"]))}</time><br>'
            f'<span>{escape(reason)}</span>'
            '</li>'
        )
    return f'<ol class="user-management-lifecycle">{"".join(rows)}</ol>'


def _inspector_template(user: UserView, index: int) -> str:
    roles = ", ".join(user.roles) if user.roles else "Keine"
    return (
        f'<template id="user-management-inspector-{index}">'
        '<div class="user-management-inspector-fixed">'
        '<dl class="user-management-properties">'
        f'<dt>Benutzer</dt><dd>{escape(user.display_name)}</dd>'
        f'<dt>Technische ID</dt><dd><code>{escape(user.user_id)}</code></dd>'
        f'<dt>Status</dt><dd>{escape(user.status_label)}</dd>'
        f'<dt>Rollen</dt><dd>{escape(roles)}</dd>'
        f'<dt>Gewichtung</dt><dd>{user.weight}</dd>'
        f'<dt>Rechte</dt><dd>{len(user.permissions)} ({user.allowed_count} erlaubt / {user.denied_count} verweigert)</dd>'
        '</dl>'
        '<div class="user-management-note"><strong>Read-only:</strong> Diese Seite wertet vorhandene ProjectOS-Daten aus. '
        'Schreibende Aktionen werden erst über die bestehenden autorisierten ProjectOS-Services angebunden.</div>'
        '<h3>Effektive Rechte</h3>'
        f'{_permission_table(user)}'
        '</div>'
        '<section class="user-management-lifecycle-section"><h3>Benutzer-Lifecycle</h3>'
        f'{_lifecycle_html(user)}</section>'
        '</template>'
    )


def user_management_page_html(
    snapshot: UserManagementSnapshot | None = None,
) -> str:
    """Rendert Benutzer, Rollen, Rechte und Lifecycle im freigegebenen Cockpit-Muster."""
    state = collect_user_management() if snapshot is None else snapshot
    roles = tuple(sorted({role for item in state.users for role in item.roles}, key=str.casefold))
    permission_states = tuple(
        state_label
        for state_label in ("Erlaubt", "Verweigert", "Benutzer deaktiviert", "Nicht erteilt")
        if any(state_label in item.permission_states for item in state.users)
    )

    rows: list[str] = []
    templates: list[str] = []
    for index, item in enumerate(state.users):
        role_text = ", ".join(item.roles) if item.roles else "–"
        rows.append(
            f'<tr class="user-management-row" tabindex="0" data-index="{index}" '
            f'data-status="{escape(item.status_label, quote=True)}" '
            f'data-roles="{_json_attr(item.roles)}" '
            f'data-permissions="{_json_attr(item.permission_states)}" '
            f'data-search="{escape((item.display_name + " " + item.user_id).casefold(), quote=True)}">'
            f'<th scope="row"><strong>{escape(item.display_name)}</strong><br><code>{escape(item.user_id)}</code></th>'
            f'<td>{escape(item.status_label)}</td><td>{escape(role_text)}</td>'
            f'<td>{item.allowed_count}</td><td>{item.denied_count}</td><td>{len(item.lifecycle_events)}</td></tr>'
        )
        templates.append(_inspector_template(item, index))

    if rows:
        table_rows = "".join(rows)
    else:
        table_rows = (
            '<tr><td colspan="6" class="user-management-empty">'
            'Keine ProjectOS-Benutzer geladen. Für echte Projektdaten das Z_Cockpit mit '
            '<code>--project-bundle &lt;projektdatei&gt;</code> erzeugen.</td></tr>'
        )

    source_state = "angebunden" if state.source_available else "nicht angebunden"
    project_id = state.project_id or "–"
    return (
        '<style>'
        '#page-benutzer.active{position:absolute;inset:0;display:flex;flex-direction:column;min-height:0;overflow:hidden;padding:0}'
        '.user-management-workspace{display:grid;grid-template-columns:minmax(0,1fr) 390px;height:100%;min-height:0;overflow:hidden}'
        '.user-management-main{min-width:0;min-height:0;padding:1rem;display:flex;flex-direction:column;overflow:hidden}'
        '.user-management-main>.cockpit-page-title{margin:0 0 .85rem}'
        '.user-management-source{padding:.65rem .75rem;border:1px solid #8885;border-radius:.4rem;margin:0 0 .8rem;flex:0 0 auto;font-size:.9rem}'
        '.user-management-filters{display:grid;grid-template-columns:minmax(180px,2fr) repeat(3,minmax(125px,1fr));gap:.6rem;margin-bottom:.8rem;flex:0 0 auto}'
        '.user-management-filters input,.user-management-filters select{padding:.45rem;width:100%}'
        '.user-management-table-wrap{flex:1 1 auto;min-height:0;overflow:auto;border:1px solid #8886}'
        '.user-management-table{border-collapse:collapse;width:100%;min-width:850px}'
        '.user-management-table th,.user-management-table td{padding:.5rem .6rem;border-bottom:1px solid #8884;text-align:left;white-space:nowrap}'
        '.user-management-table th[scope="row"]{position:static;background:transparent;white-space:normal;min-width:270px}'
        '.user-management-table thead th{position:sticky;top:0;background:Canvas;z-index:1}'
        '.user-management-row{cursor:pointer}.user-management-row:hover{background:#2878c812}.user-management-row.selected{background:#2878c81f;font-weight:600}'
        '.user-management-result-count{margin:.65rem 0 0;font-size:.9rem;opacity:.8;flex:0 0 auto}'
        '.user-management-inspector{min-width:0;min-height:0;height:100%;padding:1rem;display:flex;flex-direction:column;overflow:hidden;border-left:1px solid #8886}'
        '.user-management-inspector>h2{margin-top:0;flex:0 0 auto}'
        '#user-management-inspector-content{min-height:0;flex:1 1 auto;display:flex;flex-direction:column;overflow:hidden}'
        '.user-management-inspector-fixed{flex:0 0 auto;min-height:0}'
        '.user-management-properties{display:grid;grid-template-columns:1fr 1.45fr;gap:.45rem .7rem;margin:0 0 .8rem}'
        '.user-management-properties dt{font-weight:700}.user-management-properties dd{margin:0;min-width:0;overflow-wrap:anywhere}'
        '.user-management-properties code{white-space:normal;overflow-wrap:anywhere}'
        '.user-management-note{padding:.65rem;border:1px solid #2878c866;border-left:5px solid #2878c8;border-radius:.4rem;margin:.5rem 0 .8rem}'
        '.user-management-inspector-fixed>h3,.user-management-lifecycle-section>h3{margin:.65rem 0 .45rem}'
        '.user-management-permission-wrap{max-height:270px;overflow:auto;border:1px solid #8886;border-radius:.35rem}'
        '.user-management-permission-table{border-collapse:collapse;width:100%;min-width:690px}'
        '.user-management-permission-table th,.user-management-permission-table td{padding:.42rem .5rem;border-bottom:1px solid #8884;text-align:left;white-space:nowrap}'
        '.user-management-permission-table thead th{position:sticky;top:0;background:Canvas}'
        '.user-management-permission-table th[scope="row"]{position:static;background:transparent}'
        '.user-management-lifecycle-section{min-height:0;flex:1 1 auto;display:flex;flex-direction:column;margin-top:.55rem}'
        '.user-management-lifecycle{min-height:0;overflow-y:auto;margin:0;padding:0 0 0 1.35rem;scrollbar-gutter:stable}'
        '.user-management-lifecycle li{margin:.45rem 0;padding:.35rem .25rem;overflow-wrap:anywhere}'
        '.user-management-empty,.user-management-empty-detail{text-align:left;white-space:normal}'
        '@media(max-width:1050px){.user-management-workspace{grid-template-columns:1fr}.user-management-inspector{height:auto;max-height:45vh;overflow:auto;border-left:0;border-top:1px solid #8886}'
        '#user-management-inspector-content{overflow:visible}.user-management-filters{grid-template-columns:repeat(2,minmax(120px,1fr))}.user-management-lifecycle{max-height:15rem}}'
        '</style>'
        '<section class="page" id="page-benutzer"><div class="user-management-workspace">'
        '<div class="user-management-main">'
        '<h2 class="cockpit-page-title">Benutzerverwaltung '
        '<small class="cockpit-page-description">(ProjectOS-Benutzer, Lifecycle, Rollen und effektive Rechte.)</small></h2>'
        f'<div class="user-management-source"><strong>Datenquelle:</strong> {escape(state.source_label)} · {source_state} · '
        f'Projekt-ID <code>{escape(project_id)}</code></div>'
        '<div class="user-management-filters">'
        '<label>Suche<input id="user-management-filter-search" type="search" placeholder="Name oder technische ID"></label>'
        f'<label>Status<select id="user-management-filter-status"><option value="">Alle</option>{_options(("Aktiv", "Deaktiviert"))}</select></label>'
        f'<label>Rolle ({len(roles)})<select id="user-management-filter-role"><option value="">Alle</option>{_options(roles)}</select></label>'
        f'<label>Berechtigung<select id="user-management-filter-permission"><option value="">Alle</option>{_options(permission_states)}</select></label>'
        '</div>'
        '<div class="user-management-table-wrap"><table class="user-management-table" id="user-management-overview">'
        '<thead><tr><th>Benutzer</th><th>Status</th><th>Rollen</th><th>Erlaubt</th><th>Verweigert</th><th>Lifecycle</th></tr></thead>'
        f'<tbody>{table_rows}</tbody></table></div>'
        f'<p class="user-management-result-count" id="user-management-result-count">{len(state.users)} Benutzer · {state.active_count} aktiv · {state.deactivated_count} deaktiviert</p>'
        '</div><section class="user-management-inspector"><h2>Eigenschaften</h2>'
        '<div id="user-management-inspector-content"><p>Benutzer auswählen.</p></div></section>'
        f'{"".join(templates)}</div></section>'
        '<script type="text/javascript">(()=>{'
        'const table=document.getElementById("user-management-overview");if(!table)return;'
        'const rows=[...table.querySelectorAll(".user-management-row")];const inspector=document.getElementById("user-management-inspector-content");'
        'const count=document.getElementById("user-management-result-count");const search=document.getElementById("user-management-filter-search");'
        'const status=document.getElementById("user-management-filter-status");const role=document.getElementById("user-management-filter-role");'
        'const permission=document.getElementById("user-management-filter-permission");let selected=null;'
        'function values(row,key){try{return JSON.parse(row.dataset[key]||"[]");}catch(_){return[];}}'
        'function selectRow(row){rows.forEach(item=>item.classList.remove("selected"));row.classList.add("selected");selected=row;'
        'const tpl=document.getElementById(`user-management-inspector-${row.dataset.index}`);inspector.replaceChildren(tpl.content.cloneNode(true));}'
        'function reset(){rows.forEach(item=>item.classList.remove("selected"));selected=null;inspector.innerHTML="<p>Benutzer auswählen.</p>";}'
        'function apply(){const term=search.value.trim().toLocaleLowerCase("de");let visible=0;let first=null;rows.forEach(row=>{const show=(!term||row.dataset.search.includes(term))'
        '&&(!status.value||row.dataset.status===status.value)&&(!role.value||values(row,"roles").includes(role.value))'
        '&&(!permission.value||values(row,"permissions").includes(permission.value));row.hidden=!show;if(show){visible++;if(!first)first=row;}});'
        'count.textContent=`${visible} Benutzer sichtbar`;if(selected&&selected.hidden)reset();if(!selected&&first)selectRow(first);}'
        'rows.forEach(row=>{row.addEventListener("click",()=>selectRow(row));row.addEventListener("keydown",event=>{if(event.key==="Enter"||event.key===" "){event.preventDefault();selectRow(row);}});});'
        'search.addEventListener("input",apply);[status,role,permission].forEach(filter=>filter.addEventListener("change",apply));apply();'
        '})();</script>'
    )
