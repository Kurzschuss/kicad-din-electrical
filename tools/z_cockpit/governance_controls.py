from __future__ import annotations

from datetime import datetime, timezone
from html import escape
import json
from pathlib import Path

from distributions.projectos_authorization import ProjectOSAuthorizationEvaluator
from distributions.projectos_project_bundle_v4 import load_projectos_bundle_details
from tools.projectos_governance import PERMISSION_CATALOG, SCOPE_CATALOG
from tools.projectos_issue_reporting import DEFAULT_RESULT_PATH
from tools.validate_device_catalog import REPO_ROOT

from .permissions_page import PermissionsSnapshot
from .user_management_page import UserManagementSnapshot

_VERSION_RESULT_PATH = REPO_ROOT / "build" / "VERSIONSPRUEFUNG.json"


def _load_state(snapshot: UserManagementSnapshot):
    if not snapshot.source_available:
        return None
    source = Path(snapshot.source_label)
    if not source.is_file():
        return None
    try:
        _, _, project_id, _, state = load_projectos_bundle_details(source)
    except (OSError, ValueError):
        return None
    if state is None or (project_id and state.project_id != project_id):
        return None
    return state


def _load_json(path: Path) -> dict:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return raw if isinstance(raw, dict) else {}


def _decision_matrix(state) -> list[dict[str, object]]:
    if state is None:
        return []
    evaluator = ProjectOSAuthorizationEvaluator(
        state.permission_assignments,
        state.permission_revocations,
        state.user_deactivations,
        state.user_reactivations,
    )
    now = datetime.now(timezone.utc)
    rows: list[dict[str, object]] = []
    project_permissions = tuple(PERMISSION_CATALOG)
    page_scopes = tuple(scope for scope in SCOPE_CATALOG if scope.startswith("page:"))
    for user in state.users:
        project_rights = []
        for permission in project_permissions:
            result = evaluator.evaluate(user, permission, scope="project", at=now)
            project_rights.append({
                "permission": permission,
                "label": PERMISSION_CATALOG[permission],
                "decision": result["decision"],
                "allowed": result["allowed"],
            })
        page_rights = []
        for scope in page_scopes:
            view = evaluator.evaluate(user, "cockpit.view", scope=scope, at=now)
            edit = evaluator.evaluate(user, "cockpit.edit", scope=scope, at=now)
            page_rights.append({
                "scope": scope,
                "label": SCOPE_CATALOG[scope],
                "view": view["decision"],
                "view_allowed": view["allowed"],
                "edit": edit["decision"],
                "edit_allowed": edit["allowed"],
            })
        rows.append({
            "user_id": user.user_id,
            "display_name": user.display_name,
            "weight": user.weight,
            "github_login": user.github_login or "",
            "roles": list(user.roles),
            "project_rights": project_rights,
            "page_rights": page_rights,
        })
    return rows


def _auto_gate(state) -> dict[str, object]:
    repo = _load_json(_VERSION_RESULT_PATH)
    login = str(repo.get("authenticated_user", "")).strip()
    reasons: list[str] = []
    if not repo:
        reasons.append("Repositoryprüfung fehlt.")
    if not bool(repo.get("official_remote", False)):
        reasons.append("Kein offizielles Repository / möglicher Fork.")
    if int(repo.get("behind", 0) or 0) > 0:
        reasons.append(f"Version ist {int(repo.get('behind', 0) or 0)} Commit(s) veraltet.")
    if not bool(repo.get("current", False)):
        reasons.append(str(repo.get("message", "Repositorystand nicht freigegeben.")))
    if not login:
        reasons.append("Kein mit gh authentifizierter GitHub-Benutzer erkannt.")

    matched = None
    decision = "not_checked"
    if state is not None and login:
        matches = [
            user for user in state.users
            if user.github_login and user.github_login.casefold() == login.casefold()
        ]
        if len(matches) != 1:
            reasons.append("GitHub-Benutzer ist keinem eindeutigen ProjectOS-Benutzer zugeordnet.")
        else:
            user = matches[0]
            matched = {"user_id": user.user_id, "display_name": user.display_name, "weight": user.weight}
            evaluator = ProjectOSAuthorizationEvaluator(
                state.permission_assignments,
                state.permission_revocations,
                state.user_deactivations,
                state.user_reactivations,
            )
            result = evaluator.evaluate(user, "github.issue.auto_submit", scope="project")
            decision = str(result["decision"])
            if not result["allowed"]:
                reasons.append(f"Recht github.issue.auto_submit ist nicht erlaubt ({decision}).")
    elif state is None:
        reasons.append("Keine ProjectOS-Benutzerdaten geladen.")

    return {
        "allowed": not reasons,
        "reasons": list(dict.fromkeys(reasons)),
        "repository_status": str(repo.get("status", "nicht_geprueft")),
        "repository_message": str(repo.get("message", "")),
        "authenticated_user": login,
        "project_user": matched,
        "permission_decision": decision,
    }


def _model(users: UserManagementSnapshot, permissions: PermissionsSnapshot) -> dict[str, object]:
    state = _load_state(users)
    user_rows = _decision_matrix(state)
    assignments = [
        {
            "assignment_id": item.assignment_id,
            "user_id": item.user_id,
            "user_name": item.user_name,
            "permission": item.permission,
            "scope": item.scope,
            "source_type": item.source_type,
            "source_label": item.source_label,
            "effect": item.effect,
            "status": item.status,
            "status_label": item.status_label,
            "effective_decision": item.effective_decision,
            "effective_decision_label": item.effective_decision_label,
        }
        for item in permissions.assignments
    ]
    return {
        "source_available": bool(state is not None),
        "project_id": users.project_id,
        "users": user_rows,
        "assignments": assignments,
        "permissions": PERMISSION_CATALOG,
        "scopes": SCOPE_CATALOG,
        "auto_report_gate": _auto_gate(state),
        "last_report": _load_json(REPO_ROOT / DEFAULT_RESULT_PATH),
    }


def governance_controls_html(users: UserManagementSnapshot, permissions: PermissionsSnapshot) -> str:
    payload = json.dumps(_model(users, permissions), ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    return f'''\
<style>
.gov-panel{{border:1px solid #8886;border-radius:.45rem;padding:.8rem;margin:0 0 .8rem;flex:0 0 auto}}
.gov-panel h3{{margin:.05rem 0 .6rem}}
.gov-grid{{display:grid;grid-template-columns:repeat(4,minmax(145px,1fr));gap:.6rem;align-items:end}}
.gov-grid label{{min-width:0}}
.gov-grid input,.gov-grid select{{width:100%;padding:.48rem .55rem}}
.gov-grid button,.gov-actions button{{padding:.55rem .75rem;cursor:pointer;font-weight:650}}
.gov-note{{font-size:.84rem;opacity:.8;margin:.6rem 0 0}}
.gov-status{{font-size:.86rem;font-weight:650;min-height:1.2em;margin:.5rem 0 0}}
.gov-user-matrix{{margin-top:.75rem;overflow:auto;max-height:21rem;border:1px solid #8885;border-radius:.35rem}}
.gov-user-matrix table{{width:100%;border-collapse:collapse;min-width:760px}}
.gov-user-matrix th,.gov-user-matrix td{{padding:.42rem .55rem;border-bottom:1px solid #8884;text-align:left;white-space:nowrap}}
.gov-pill{{display:inline-block;padding:.1rem .38rem;border-radius:999px;border:1px solid #8886;font-size:.75rem}}
.gov-pill.allow{{border-color:#2e8b57;color:#2e8b57}}.gov-pill.deny{{border-color:#b33a3a;color:#b33a3a}}
.gov-report-gate{{padding:.7rem;border:1px solid #8886;border-left:5px solid #b33a3a;border-radius:.4rem;margin:.8rem 0}}
.gov-report-gate.ready{{border-left-color:#2e8b57}}
.gov-report-last{{margin-top:.55rem;font-size:.86rem}}
@media(max-width:1100px){{.gov-grid{{grid-template-columns:repeat(2,minmax(150px,1fr))}}}}
@media(max-width:680px){{.gov-grid{{grid-template-columns:1fr}}}}
</style>
<script type="application/json" id="governance-model">{payload}</script>
<script type="text/javascript">
(()=>{{
const M=JSON.parse(document.getElementById('governance-model').textContent);
const enc=value=>encodeURIComponent(String(value??''));
const simulation=()=>document.body.classList.contains('cockpit-simulation');
function go(params){{if(simulation()){{alert('Im Simulationsmodus werden keine ProjectOS-Daten verändert.');return}}const q=Object.entries(params).map(([k,v])=>`${{enc(k)}}=${{enc(v)}}`).join('&');window.location.href=`projectos-z://governance?${{q}}`;}}
function option(select,value,label){{const o=document.createElement('option');o.value=value;o.textContent=label;select.appendChild(o)}}
function selectedUser(id){{return M.users.find(u=>u.user_id===id)}}
function pill(decision){{const allow=decision==='allow';return `<span class="gov-pill ${{allow?'allow':'deny'}}">${{allow?'Erlaubt':decision==='deny'?'Verweigert':'Nicht erteilt'}}</span>`}}

function buildUserAdmin(){{
 const main=document.querySelector('#page-benutzer .user-management-main');if(!main||document.getElementById('gov-user-admin'))return;
 const panel=document.createElement('section');panel.className='gov-panel';panel.id='gov-user-admin';
 panel.innerHTML='<h3>Benutzerverwaltung &amp; Zugriffsstatus</h3><div class="gov-grid">'+
 '<label>Benutzer<select id="gov-user-select"><option value="">Neuen Benutzer anlegen</option></select></label>'+
 '<label>Bezeichnung<input id="gov-user-name" maxlength="80"></label>'+
 '<label>Gewichtung (0–1000)<input id="gov-user-weight" type="number" min="0" max="1000" value="100"></label>'+
 '<label>GitHub-Benutzer<input id="gov-user-github" maxlength="39" placeholder="z. B. Kurzschuss"></label>'+
 '</div><div class="gov-actions" style="margin-top:.6rem"><button id="gov-user-save" type="button">Benutzer speichern</button> <button id="gov-bootstrap" type="button">Erstadministrator einrichten</button></div>'+
 '<p class="gov-note">Bezeichnung und Gewichtung sind ProjectOS-Profilwerte; die Gewichtung entscheidet nicht über Rechte. Die GitHub-Zuordnung ist für vertrauenswürdige Schreib- und automatische Meldeaktionen erforderlich. Sichtbarkeit einer Projektdatei wird zusätzlich durch den tatsächlichen Repository-/Dateizugriff erzwungen.</p>'+
 '<p id="gov-user-status" class="gov-status"></p><div id="gov-user-matrix" class="gov-user-matrix"></div>';
 const sim=document.getElementById('user-simulation-panel');if(sim)sim.insertAdjacentElement('afterend',panel);else main.prepend(panel);
 const select=document.getElementById('gov-user-select');M.users.forEach(u=>option(select,u.user_id,`${{u.display_name}} · ${{u.github_login||'kein GitHub'}}`));
 const name=document.getElementById('gov-user-name'),weight=document.getElementById('gov-user-weight'),github=document.getElementById('gov-user-github');
 function fill(){{const u=selectedUser(select.value);name.value=u?u.display_name:'';weight.value=u?u.weight:100;github.value=u?u.github_login:'';renderMatrix(u)}}
 function renderMatrix(u){{const box=document.getElementById('gov-user-matrix');if(!u){{box.innerHTML='<p style="padding:.6rem">Benutzer auswählen, um Rechte und Zugriffsbereiche zu sehen.</p>';return}}let html='<table><thead><tr><th>Projekt-Recht</th><th>Status</th></tr></thead><tbody>';u.project_rights.forEach(r=>{{html+=`<tr><td><code>${{r.permission}}</code><br><small>${{r.label}}</small></td><td>${{pill(r.decision)}}</td></tr>`}});html+='</tbody></table><table><thead><tr><th>Bereich</th><th>Sehen</th><th>Bearbeiten</th></tr></thead><tbody>';u.page_rights.forEach(r=>{{html+=`<tr><td>${{r.label}}</td><td>${{pill(r.view)}}</td><td>${{pill(r.edit)}}</td></tr>`}});html+='</tbody></table>';box.innerHTML=html}}
 select.addEventListener('change',fill);fill();
 document.getElementById('gov-user-save').addEventListener('click',()=>{{const n=name.value.trim(),w=Number(weight.value),g=github.value.trim();if(!n||!Number.isInteger(w)||w<0||w>1000){{document.getElementById('gov-user-status').textContent='Bezeichnung und Gewichtung prüfen.';return}}if(select.value)go({{op:'user-update',user_id:select.value,name:n,weight:w,github:g}});else go({{op:'user-create',name:n,weight:w,github:g}})}});
 document.getElementById('gov-bootstrap').addEventListener('click',()=>{{const n=name.value.trim()||'Projektadministrator';const w=Number(weight.value)||1000;if(M.users.length){{document.getElementById('gov-user-status').textContent='Bootstrap ist nur bei leerer Benutzerverwaltung zulässig.';return}}go({{op:'bootstrap',name:n,weight:w}})}});
}}

function buildPermissionAdmin(){{
 const main=document.querySelector('#page-berechtigungen .permissions-main');if(!main||document.getElementById('gov-permission-admin'))return;
 const panel=document.createElement('section');panel.className='gov-panel';panel.id='gov-permission-admin';
 panel.innerHTML='<h3>White-/Blacklist &amp; Zugriffsregeln verwalten</h3><div class="gov-grid">'+
 '<label>Benutzer<select id="gov-rule-user"></select></label><label>Recht<select id="gov-rule-permission"></select></label><label>Zugriffsbereich<select id="gov-rule-scope"></select></label><label>Liste<select id="gov-rule-list"><option value="whitelist">Whitelist · erlauben</option><option value="blacklist">Blacklist · sperren</option></select></label>'+
 '</div><div class="gov-grid" style="margin-top:.6rem"><label>Risikoklasse<select id="gov-rule-risk"><option>low</option><option selected>medium</option><option>high</option><option>critical</option></select></label><label>Aktive Regel widerrufen<select id="gov-rule-revoke"><option value="">– auswählen –</option></select></label><label>Widerrufsgrund<input id="gov-rule-reason" value="Berechtigung geändert"></label><div class="gov-actions"><button id="gov-rule-add" type="button">Regel hinzufügen</button> <button id="gov-rule-revoke-btn" type="button">Widerrufen</button></div></div>'+
 '<p class="gov-note">Whitelist = ALLOW, Blacklist = DENY. Ein wirksames DENY hat weiterhin Vorrang. Schreibende Änderungen werden nicht im Browser gespeichert, sondern über den autorisierten ProjectOS-Change-Service in die aktive Projektdatei geschrieben.</p><p id="gov-rule-status" class="gov-status"></p>';
 const source=main.querySelector('.permissions-source');if(source)source.insertAdjacentElement('afterend',panel);else main.prepend(panel);
 const user=document.getElementById('gov-rule-user'),perm=document.getElementById('gov-rule-permission'),scope=document.getElementById('gov-rule-scope'),revoke=document.getElementById('gov-rule-revoke');
 M.users.forEach(u=>option(user,u.user_id,u.display_name));Object.entries(M.permissions).forEach(([id,label])=>option(perm,id,`${{label}} · ${{id}}`));Object.entries(M.scopes).forEach(([id,label])=>option(scope,id,`${{label}} · ${{id}}`));M.assignments.filter(a=>a.status==='active'&&(a.source_type==='whitelist'||a.source_type==='blacklist')).forEach(a=>option(revoke,a.assignment_id,`${{a.user_name}} · ${{a.source_label}} · ${{a.permission}} · ${{a.scope}}`));
 document.getElementById('gov-rule-add').addEventListener('click',()=>{{if(!user.value){{document.getElementById('gov-rule-status').textContent='Benutzer auswählen.';return}}go({{op:'rule-add',user_id:user.value,permission:perm.value,scope:scope.value,list_type:document.getElementById('gov-rule-list').value,risk:document.getElementById('gov-rule-risk').value}})}});
 document.getElementById('gov-rule-revoke-btn').addEventListener('click',()=>{{if(!revoke.value){{document.getElementById('gov-rule-status').textContent='Aktive Regel auswählen.';return}}go({{op:'rule-revoke',assignment_id:revoke.value,reason:document.getElementById('gov-rule-reason').value.trim()||'Berechtigung geändert'}})}});
}}

function buildAutoReporting(){{
 const root=document.getElementById('page-fehlerbericht');if(!root||document.getElementById('gov-auto-report'))return;const gate=M.auto_report_gate;
 const target=root.querySelector('.issue-report-repository');if(!target)return;const box=document.createElement('section');box.className=`gov-report-gate ${{gate.allowed?'ready':''}}`;box.id='gov-auto-report';
 const user=gate.project_user?`${{gate.project_user.display_name}} · ${{gate.authenticated_user}}`:(gate.authenticated_user||'nicht zugeordnet');
 const reasons=gate.allowed?'Alle Voraussetzungen erfüllt.':gate.reasons.map(x=>`• ${{x}}`).join('<br>');
 let last='';if(M.last_report&&M.last_report.status){{const reporters=(M.last_report.reporters||[]).join(', ')||'–';last=`<div class="gov-report-last"><strong>Letzte Automatikprüfung:</strong> ${{M.last_report.message||M.last_report.status}}<br>Issue: ${{M.last_report.issue_number?'#'+M.last_report.issue_number:'–'}} · Meldungen: ${{M.last_report.report_count||0}} · Reporter: ${{reporters}}</div>`}}
 box.innerHTML=`<strong>Automatische GitHub-Meldung: ${{gate.allowed?'freigegeben':'gesperrt'}}</strong><br>GitHub/ProjectOS: ${{user}}<br>Repository: ${{gate.repository_status}}<br><span>${{reasons}}</span>${{last}}<div class="gov-actions" style="margin-top:.6rem"><button type="button" id="gov-auto-send" ${{gate.allowed?'':'disabled'}}>Nach Dublettenprüfung automatisch senden</button></div><p class="gov-note">Vor jedem Schreibzugriff werden Version, offizielles Repository/Fork, GitHub-Authentifizierung, ProjectOS-Zuordnung, Benutzerstatus und <code>github.issue.auto_submit</code> serverseitig erneut geprüft. Bereits bekannte Fehler erzeugen kein zweites Issue; ProjectOS ergänzt eine Wiederholungsmeldung und zählt Reporter/Meldungen.</p>`;
 target.insertAdjacentElement('afterend',box);
 document.getElementById('gov-auto-send').addEventListener('click',async()=>{{const confirm=document.getElementById('issue-confirm-review'),preview=document.getElementById('issue-report-preview'),status=document.getElementById('issue-report-status');if(!confirm?.checked){{if(status)status.textContent='Bericht zuerst prüfen und bestätigen.';return}}if(!preview?.value.trim()){{if(status)status.textContent='Berichtsvorschau ist leer.';return}}if(simulation()){{if(status)status.textContent='Automatisches Senden ist im Simulationsmodus gesperrt.';return}}try{{await navigator.clipboard.writeText(preview.value);if(status)status.textContent='Bericht wird lokal erneut geprüft und an GitHub übergeben …';window.location.href='projectos-z://report?mode=auto'}}catch(_){{if(status)status.textContent='Zwischenablage konnte nicht für die sichere lokale Übergabe verwendet werden.'}}}});
}}

buildUserAdmin();buildPermissionAdmin();buildAutoReporting();
}})();
</script>'''
