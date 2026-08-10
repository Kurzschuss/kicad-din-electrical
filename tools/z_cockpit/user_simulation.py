from __future__ import annotations

from dataclasses import dataclass
from html import escape
import json

from .user_management_page import UserManagementSnapshot, UserView

TEST_USER_ID = "00000000-0000-0000-0000-000000000001"


@dataclass(frozen=True)
class CockpitIdentityView:
    user_id: str
    display_name: str
    status_label: str
    weight: int
    roles: tuple[str, ...]
    permissions: tuple[tuple[str, str], ...]
    allowed_count: int
    denied_count: int
    simulation_only: bool = False

    def as_dict(self) -> dict[str, object]:
        return {
            "user_id": self.user_id,
            "display_name": self.display_name,
            "status_label": self.status_label,
            "weight": self.weight,
            "roles": list(self.roles),
            "permissions": [
                {"permission": permission, "decision_label": decision_label}
                for permission, decision_label in self.permissions
            ],
            "allowed_count": self.allowed_count,
            "denied_count": self.denied_count,
            "simulation_only": self.simulation_only,
        }


def _identity_from_user(user: UserView) -> CockpitIdentityView:
    return CockpitIdentityView(
        user_id=user.user_id,
        display_name=user.display_name,
        status_label=user.status_label,
        weight=user.weight,
        roles=user.roles,
        permissions=tuple((item.permission, item.decision_label) for item in user.permissions),
        allowed_count=user.allowed_count,
        denied_count=user.denied_count,
    )


def simulation_test_user(*, weight: int = 100) -> CockpitIdentityView:
    """Liefert den rein lokalen Testbenutzer ohne persistierte Rechte."""
    normalized_weight = int(weight)
    if not 0 <= normalized_weight <= 1000:
        raise ValueError("test user weight must be between 0 and 1000")
    return CockpitIdentityView(
        user_id=TEST_USER_ID,
        display_name="Testuser",
        status_label="Aktiv",
        weight=normalized_weight,
        roles=("Testbenutzer",),
        permissions=(),
        allowed_count=0,
        denied_count=0,
        simulation_only=True,
    )


def collect_identity_users(snapshot: UserManagementSnapshot) -> tuple[CockpitIdentityView, ...]:
    """Bereitet vorhandene Benutzer plus den lokalen Testuser für die UI auf."""
    users = tuple(_identity_from_user(user) for user in snapshot.users)
    return (*users, simulation_test_user())


def _payload(snapshot: UserManagementSnapshot) -> str:
    data = {
        "project_id": snapshot.project_id,
        "source_available": snapshot.source_available,
        "users": [item.as_dict() for item in collect_identity_users(snapshot)],
        "test_user_id": TEST_USER_ID,
        "note": (
            "Die aktive Cockpit-Identität ist eine lokale Oberflächenwahl und keine Authentifizierung. "
            "Der Simulationsmodus verändert keine ProjectOS-Daten."
        ),
    }
    return json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


def user_simulation_html(snapshot: UserManagementSnapshot) -> str:
    """Ergänzt Benutzerverwaltung und Kopfbereich um lokalen Identitäts-/Simulationskontext."""
    payload = _payload(snapshot)
    return f'''\
<style>
.cockpit-identity-bar{{display:grid;grid-template-columns:minmax(190px,1.35fr) repeat(4,minmax(120px,1fr)) minmax(160px,1.1fr);gap:.55rem;align-items:stretch;margin-top:.65rem}}
.cockpit-identity-item{{min-width:0;padding:.48rem .6rem;border:1px solid #8885;border-radius:.4rem;font-size:.82rem}}
.cockpit-identity-item>span,.cockpit-identity-item>strong{{display:block;overflow-wrap:anywhere}}
.cockpit-identity-label{{font-size:.72rem;opacity:.68;margin-bottom:.12rem}}
.cockpit-identity-mode{{display:inline-block;padding:.12rem .4rem;border-radius:999px;border:1px solid #8886;font-weight:700}}
.cockpit-identity-mode.simulation{{border-color:#c58a00;background:#c58a0018}}
.cockpit-identity-rights{{position:relative}}
.cockpit-identity-rights summary{{cursor:pointer;font-weight:700}}
.cockpit-identity-rights ul{{margin:.45rem 0 0;padding-left:1.2rem;max-height:12rem;overflow:auto}}
.user-simulation-panel{{padding:.8rem;border:1px solid #8886;border-left:5px solid #2878c8;border-radius:.45rem;margin:0 0 .8rem;flex:0 0 auto}}
.user-simulation-panel.simulation-active{{border-left-color:#c58a00}}
.user-simulation-panel h3{{margin:0 0 .55rem}}
.user-simulation-controls{{display:grid;grid-template-columns:minmax(180px,1.2fr) minmax(170px,.8fr) minmax(180px,1.2fr) minmax(140px,.7fr);gap:.65rem;align-items:end}}
.user-simulation-controls label{{min-width:0}}
.user-simulation-toggle{{display:flex;align-items:center;gap:.45rem;padding:.45rem .55rem;border:1px solid #8885;border-radius:.35rem;min-height:2.45rem;font-size:.9rem}}
.user-simulation-toggle input{{margin:0}}
.user-simulation-note{{margin:.65rem 0 0;font-size:.85rem;opacity:.8}}
.user-simulation-test-card{{margin:.65rem 0 0;padding:.55rem .65rem;border:1px dashed #8887;border-radius:.35rem;font-size:.86rem}}
.user-simulation-status{{font-weight:700;margin-left:.35rem}}
body.cockpit-simulation .kicad-editor-actions a{{opacity:.42;filter:grayscale(.4);cursor:not-allowed}}
@media(max-width:1200px){{.cockpit-identity-bar{{grid-template-columns:repeat(3,minmax(150px,1fr))}}.user-simulation-controls{{grid-template-columns:repeat(2,minmax(150px,1fr))}}}}
@media(max-width:720px){{.cockpit-identity-bar,.user-simulation-controls{{grid-template-columns:1fr}}}}
</style>
<script type="text/javascript">
(()=>{{
const MODEL={payload};
const KEY="z-cockpit.identity.v1";
const testUserId=MODEL.test_user_id;
const realUsers=MODEL.users.filter(item=>!item.simulation_only);
const allUsers=MODEL.users;
const defaultState={{ownUserId:"",simulation:false,simulationUserId:testUserId,testWeight:100}};
function read(){{try{{const raw=localStorage.getItem(KEY);if(!raw)return {{...defaultState}};return {{...defaultState,...JSON.parse(raw)}}}}catch(_){{return {{...defaultState}}}}}}
function write(){{try{{localStorage.setItem(KEY,JSON.stringify(state))}}catch(_){{}}}}
let state=read();
if(!realUsers.some(item=>item.user_id===state.ownUserId))state.ownUserId="";
if(!allUsers.some(item=>item.user_id===state.simulationUserId))state.simulationUserId=testUserId;
state.testWeight=Math.max(0,Math.min(1000,Number(state.testWeight)||100));

function option(select,value,label){{const item=document.createElement("option");item.value=value;item.textContent=label;select.appendChild(item)}}
function currentUser(){{
 const id=state.simulation?state.simulationUserId:state.ownUserId;
 const found=allUsers.find(item=>item.user_id===id);
 if(!found)return null;
 if(found.user_id===testUserId)return {{...found,weight:state.testWeight}};
 return found;
}}
function permissionSummary(user){{if(!user)return "Keine Identität gewählt";return `${{user.allowed_count}} erlaubt / ${{user.denied_count}} verweigert`}}
function rolesText(user){{return user&&user.roles.length?user.roles.join(", "):"–"}}

function buildIdentityBar(){{
 const header=document.querySelector("body>header");if(!header||document.getElementById("cockpit-identity-bar"))return;
 const bar=document.createElement("div");bar.className="cockpit-identity-bar";bar.id="cockpit-identity-bar";
 bar.innerHTML='<div class="cockpit-identity-item"><span class="cockpit-identity-label">Aktive ProjectOS-Identität</span><strong id="cockpit-identity-name">Nicht gewählt</strong></div>'+
 '<div class="cockpit-identity-item"><span class="cockpit-identity-label">Modus</span><span id="cockpit-identity-mode" class="cockpit-identity-mode">Lokal</span></div>'+
 '<div class="cockpit-identity-item"><span class="cockpit-identity-label">Bearbeitungsstatus</span><strong id="cockpit-identity-status">–</strong></div>'+
 '<div class="cockpit-identity-item"><span class="cockpit-identity-label">Gewichtung</span><strong id="cockpit-identity-weight">–</strong></div>'+
 '<div class="cockpit-identity-item"><span class="cockpit-identity-label">Rollen</span><strong id="cockpit-identity-roles">–</strong></div>'+
 '<details class="cockpit-identity-item cockpit-identity-rights"><summary id="cockpit-identity-rights-summary">Rechte: –</summary><ul id="cockpit-identity-rights-list"></ul></details>';
 header.appendChild(bar);
}}

function buildSimulationPanel(){{
 const main=document.querySelector("#page-benutzer .user-management-main");if(!main||document.getElementById("user-simulation-panel"))return;
 const panel=document.createElement("section");panel.className="user-simulation-panel";panel.id="user-simulation-panel";
 panel.innerHTML='<h3>Eigene Identität &amp; Simulation <span class="user-simulation-status" id="user-simulation-status"></span></h3>'+
 '<div class="user-simulation-controls">'+
 '<label>Eigene Cockpit-Identität<select id="user-own-identity"><option value="">Nicht gewählt</option></select></label>'+
 '<label class="user-simulation-toggle"><input type="checkbox" id="user-simulation-toggle"><span>Simulationsmodus</span></label>'+
 '<label>Simulierter Benutzer<select id="user-simulation-user"></select></label>'+
 '<label>Testuser-Gewichtung<input id="user-test-weight" type="number" min="0" max="1000" step="1"></label>'+
 '</div>'+
 '<p class="user-simulation-note">Die Auswahl ist lokal im Browser und keine Anmeldung. Im Simulationsmodus werden keine ProjectOS-Daten verändert; lokale <code>kicad-z:</code>-Editoraufrufe sind gesperrt.</p>'+
 '<div class="user-simulation-test-card"><strong>Testuser:</strong> nur für Simulation, Status Aktiv, Standardgewichtung 100, Rolle Testbenutzer und bewusst ohne persistierte Rechte. Für vorhandene Rechteprofile kann im Simulationsmodus ein realer ProjectOS-Benutzer ausgewählt werden.</div>';
 const source=main.querySelector(".user-management-source");if(source)source.insertAdjacentElement("afterend",panel);else main.prepend(panel);
 const own=document.getElementById("user-own-identity");const simulated=document.getElementById("user-simulation-user");
 realUsers.forEach(user=>option(own,user.user_id,`${{user.display_name}} · ${{user.status_label}}`));
 option(simulated,testUserId,"Testuser · Simulation");realUsers.forEach(user=>option(simulated,user.user_id,`${{user.display_name}} · ${{user.status_label}}`));
}}

function renderRights(user){{
 const summary=document.getElementById("cockpit-identity-rights-summary");const list=document.getElementById("cockpit-identity-rights-list");if(!summary||!list)return;
 summary.textContent=`Rechte: ${{permissionSummary(user)}}`;list.replaceChildren();
 if(!user||!user.permissions.length){{const li=document.createElement("li");li.textContent=user?"Keine Rechtezuweisungen vorhanden.":"Keine Identität gewählt.";list.appendChild(li);return}}
 user.permissions.forEach(item=>{{const li=document.createElement("li");li.textContent=`${{item.permission}} · ${{item.decision_label}}`;list.appendChild(li)}});
}}
function renderHeader(){{
 const user=currentUser();const name=document.getElementById("cockpit-identity-name");const mode=document.getElementById("cockpit-identity-mode");
 if(!name||!mode)return;name.textContent=user?user.display_name:"Nicht gewählt";mode.textContent=state.simulation?"SIMULATION":(user?"Lokale Identität":"Nicht gewählt");mode.classList.toggle("simulation",state.simulation);
 document.getElementById("cockpit-identity-status").textContent=user?user.status_label:"–";
 document.getElementById("cockpit-identity-weight").textContent=user?String(user.weight):"–";
 document.getElementById("cockpit-identity-roles").textContent=rolesText(user);renderRights(user);
}}

function renderTestInspector(user){{
 const inspector=document.getElementById("user-management-inspector-content");if(!inspector)return;
 document.querySelectorAll("#user-management-overview .user-management-row").forEach(row=>row.classList.remove("selected"));
 inspector.replaceChildren();
 const fixed=document.createElement("div");fixed.className="user-management-inspector-fixed";
 const title=document.createElement("h3");title.textContent="Testuser · Simulation";fixed.appendChild(title);
 const dl=document.createElement("dl");dl.className="user-management-properties";
 [["Benutzer",user.display_name],["Technische ID",user.user_id],["Bearbeitungsstatus",user.status_label],["Rollen",rolesText(user)],["Gewichtung",String(user.weight)],["Rechte",permissionSummary(user)]].forEach(([label,value])=>{{const dt=document.createElement("dt");dt.textContent=label;const dd=document.createElement("dd");dd.textContent=value;dl.append(dt,dd)}});fixed.appendChild(dl);
 const note=document.createElement("div");note.className="user-management-note";note.innerHTML="<strong>Simulation:</strong> Dieser Testuser existiert nur in der lokalen Cockpit-Simulation und wird nicht in ProjectOS gespeichert. Die Gewichtung beeinflusst die Rechteentscheidung nicht.";fixed.appendChild(note);
 const rights=document.createElement("h3");rights.textContent="Effektive Rechte";fixed.appendChild(rights);const text=document.createElement("p");text.textContent="Keine persistierten Rechte. Für die Sicht eines vorhandenen Rechteprofils im Simulationsmodus einen realen Benutzer auswählen.";fixed.appendChild(text);inspector.appendChild(fixed);
}}
function syncInspector(){{
 if(!state.simulation)return;const user=currentUser();if(!user)return;
 if(user.user_id===testUserId){{renderTestInspector(user);return}}
 const row=[...document.querySelectorAll("#user-management-overview .user-management-row")].find(item=>item.textContent.includes(user.user_id));if(row&&!row.hidden)row.click();
}}

function syncEditorActions(){{
 document.body.classList.toggle("cockpit-simulation",state.simulation);
 document.querySelectorAll('a[href^="kicad-z:"]').forEach(link=>{{if(state.simulation){{link.setAttribute("aria-disabled","true");link.dataset.simulationBlocked="1"}}else if(link.dataset.simulationBlocked){{link.removeAttribute("aria-disabled");delete link.dataset.simulationBlocked}}}});
}}
function apply(){{
 const own=document.getElementById("user-own-identity");const toggle=document.getElementById("user-simulation-toggle");const simulated=document.getElementById("user-simulation-user");const weight=document.getElementById("user-test-weight");
 if(!own||!toggle||!simulated||!weight)return;own.value=state.ownUserId;toggle.checked=!!state.simulation;simulated.value=state.simulationUserId;simulated.disabled=!state.simulation;weight.value=String(state.testWeight);weight.disabled=!state.simulation||state.simulationUserId!==testUserId;
 document.getElementById("user-simulation-panel").classList.toggle("simulation-active",state.simulation);document.getElementById("user-simulation-status").textContent=state.simulation?"SIMULATION":"LOKAL";
 renderHeader();syncEditorActions();requestAnimationFrame(syncInspector);write();
}}

buildIdentityBar();buildSimulationPanel();
const own=document.getElementById("user-own-identity");const toggle=document.getElementById("user-simulation-toggle");const simulated=document.getElementById("user-simulation-user");const weight=document.getElementById("user-test-weight");
own?.addEventListener("change",()=>{{state.ownUserId=own.value;apply()}});toggle?.addEventListener("change",()=>{{state.simulation=toggle.checked;apply()}});simulated?.addEventListener("change",()=>{{state.simulationUserId=simulated.value;apply()}});weight?.addEventListener("change",()=>{{state.testWeight=Math.max(0,Math.min(1000,Number(weight.value)||100));apply()}});
["user-management-filter-search","user-management-filter-status","user-management-filter-role","user-management-filter-permission"].forEach(id=>{{const control=document.getElementById(id);control?.addEventListener(id.includes("search")?"input":"change",()=>requestAnimationFrame(syncInspector))}});
document.addEventListener("click",event=>{{const link=event.target.closest?.('a[href^="kicad-z:"]');if(state.simulation&&link){{event.preventDefault();event.stopImmediatePropagation();document.getElementById("user-simulation-status").textContent="SIMULATION · Editoraufruf blockiert"}}}},true);
new MutationObserver(syncEditorActions).observe(document.body,{{childList:true,subtree:true}});
apply();
}})();
</script>
'''


__all__ = [
    "CockpitIdentityView",
    "TEST_USER_ID",
    "collect_identity_users",
    "simulation_test_user",
    "user_simulation_html",
]
