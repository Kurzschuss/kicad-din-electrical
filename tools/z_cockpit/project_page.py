from __future__ import annotations

from html import escape
from pathlib import Path

from .project_access import (
    PROJECT_FILE_RIGHTS,
    collect_project_access,
    path_is_within,
)
from .user_management_page import UserManagementSnapshot

ROOT = Path(__file__).resolve().parents[2]


def _decision_badge(decision: str, label: str) -> str:
    css = "allow" if decision == "allow" else "deny" if decision in {"deny", "user_deactivated"} else "neutral"
    return f'<span class="project-access-badge {css}">{escape(label)}</span>'


def _access_matrix(snapshot: UserManagementSnapshot) -> str:
    users = collect_project_access(snapshot)
    if not users:
        return (
            '<div class="project-empty"><strong>Noch keine ProjectOS-Benutzerrechte vorhanden.</strong> '
            'Die vier Dateirechte sind bereits fest definiert und können später über die vorhandene '
            'ProjectOS-Berechtigungsverwaltung zugewiesen werden.</div>'
        )
    headings = "".join(f'<th title="{escape(permission)}">{escape(label)}</th>' for permission, label in PROJECT_FILE_RIGHTS)
    rows: list[str] = []
    for user in users:
        rights = "".join(
            f'<td>{_decision_badge(item.decision, item.decision_label)}</td>'
            for item in user.rights
        )
        rows.append(
            '<tr>'
            f'<td><strong>{escape(user.display_name)}</strong><br><code>{escape(user.user_id)}</code></td>'
            f'<td>{escape(user.status_label)}</td>{rights}</tr>'
        )
    return (
        '<div class="project-access-scroll"><table class="project-access-table">'
        f'<thead><tr><th>Benutzer</th><th>Status</th>{headings}</tr></thead>'
        f'<tbody>{"".join(rows)}</tbody></table></div>'
    )


def project_page_html(snapshot: UserManagementSnapshot) -> str:
    """Rendert Projektdatei-Workflow, Speicherklassifizierung und ProjectOS-Dateirechte."""
    if snapshot.source_available:
        source = snapshot.source_label
        project_file = Path(source).name or source
        project_name = project_file.removesuffix(".projectos.json").removesuffix(".json")
        repository_visible = path_is_within(source, ROOT)
        storage_label = (
            "Im allgemeinen Quell-Repository · für alle Repository-Leser sichtbar"
            if repository_visible
            else "Außerhalb des allgemeinen Quell-Repositories"
        )
        storage_class = "warning" if repository_visible else "ok"
        current = (
            '<div class="project-current-grid">'
            f'<div><span class="project-label">Projekt</span><strong>{escape(project_name)}</strong></div>'
            f'<div><span class="project-label">Datei</span><code>{escape(project_file)}</code></div>'
            f'<div><span class="project-label">Projekt-ID</span><code>{escape(snapshot.project_id or "–")}</code></div>'
            '<div><span class="project-label">Format</span><strong>ProjectOS v4</strong></div>'
            '</div>'
            f'<p class="project-path"><strong>Speicherort:</strong> <code>{escape(source)}</code></p>'
            f'<div class="project-storage-state {storage_class}"><strong>Dateisichtbarkeit:</strong> {escape(storage_label)}</div>'
        )
    else:
        current = (
            '<div class="project-empty"><strong>Kein ProjectOS-Projekt aktiv.</strong> '
            'Erstelle unten ein neues Projekt. Beim nächsten Z_Cockpit-Start wird das zuletzt aktive, '
            'noch gültige Projekt automatisch wieder geladen.</div>'
        )

    access_matrix = _access_matrix(snapshot)
    permission_legend = " · ".join(
        f'<code>{escape(permission)}</code> = {escape(label)}' for permission, label in PROJECT_FILE_RIGHTS
    )

    return (
        '<style>'
        '#page-projekt.active{display:block;min-height:100%}'
        '.project-layout{display:grid;grid-template-columns:minmax(0,1.2fr) minmax(340px,.8fr);gap:1rem;align-items:start}'
        '.project-panel{border:1px solid #8886;border-radius:.5rem;padding:1rem}'
        '.project-panel h3{margin-top:0}'
        '.project-current-grid{display:grid;grid-template-columns:repeat(2,minmax(180px,1fr));gap:.7rem}'
        '.project-current-grid>div{padding:.65rem;border:1px solid #8885;border-radius:.4rem;min-width:0}'
        '.project-current-grid strong,.project-current-grid code,.project-label{display:block;overflow-wrap:anywhere}'
        '.project-label{font-size:.78rem;opacity:.7;margin-bottom:.2rem}'
        '.project-path{margin:.85rem 0 0;overflow-wrap:anywhere}'
        '.project-empty{padding:.85rem;border:1px dashed #8888;border-radius:.4rem}'
        '.project-new-form{display:grid;gap:.65rem}'
        '.project-new-form input,.project-new-form select{padding:.55rem .6rem;width:100%}'
        '.project-new-form button{padding:.6rem .85rem;justify-self:start;cursor:pointer;font-weight:700}'
        '.project-note{padding:.7rem;border:1px solid #2878c866;border-left:5px solid #2878c8;border-radius:.4rem;font-size:.9rem}'
        '.project-note.security{border-color:#c58a0066;border-left-color:#c58a00}'
        '.project-status{min-height:1.35rem;margin:.1rem 0 0;font-size:.9rem;font-weight:650}'
        '.project-security{margin:.8rem 0 0;font-size:.86rem;opacity:.86}'
        '.project-storage-state{margin:.75rem 0 0;padding:.6rem;border-radius:.35rem;border:1px solid #8885;font-size:.88rem}'
        '.project-storage-state.warning{border-left:5px solid #c58a00}.project-storage-state.ok{border-left:5px solid #26865b}'
        '.project-access-panel{margin-top:1rem}'
        '.project-access-scroll{overflow:auto;max-height:24rem;border:1px solid #8885;border-radius:.4rem}'
        '.project-access-table{width:100%;border-collapse:collapse;font-size:.85rem}'
        '.project-access-table th,.project-access-table td{padding:.48rem .55rem;border-bottom:1px solid #8884;text-align:left;vertical-align:top}'
        '.project-access-table th{position:sticky;top:0;background:var(--surface,#fff);z-index:1}'
        '.project-access-table code{font-size:.75rem}'
        '.project-access-badge{display:inline-block;padding:.12rem .35rem;border:1px solid #8886;border-radius:999px;white-space:nowrap}'
        '.project-access-badge.allow{border-color:#26865b;background:#26865b18}.project-access-badge.deny{border-color:#b84242;background:#b8424218}.project-access-badge.neutral{opacity:.72}'
        '.project-access-legend{font-size:.8rem;opacity:.78;overflow-wrap:anywhere}'
        '@media(max-width:950px){.project-layout{grid-template-columns:1fr}.project-current-grid{grid-template-columns:1fr}}'
        '</style>'
        '<section class="page" id="page-projekt">'
        '<h2 class="cockpit-page-title">Projekt '
        '<small class="cockpit-page-description">(ProjectOS-Projektdatei, Schutzklasse und Zugriffsrechte.)</small></h2>'
        '<div class="project-layout">'
        '<section class="project-panel"><h3>Aktives Projekt</h3>'
        f'{current}</section>'
        '<section class="project-panel"><h3>Neues Projekt</h3>'
        '<div class="project-note security"><strong>Vertrauliche Teamprojekte:</strong> Standardmäßig wird die Schutzklasse '
        '„Vertraulich · Team“ verwendet. Solche Dateien dürfen nicht im allgemeinen Quell-Repository liegen. Für Zusammenarbeit '
        'muss ein separates privates Projekt-Repository mit den passenden GitHub-Lese-/Schreibrechten verwendet werden.</div>'
        '<div class="project-new-form">'
        '<label>Projektname<input id="project-new-name" type="text" maxlength="80" autocomplete="off" '
        'placeholder="z. B. Verteilung Werkstatt"></label>'
        '<label>Schutzklasse<select id="project-new-protection">'
        '<option value="private_team" selected>Vertraulich · Team — separates privates Projekt-Repository</option>'
        '<option value="restricted_local">Vertraulich · lokal — nicht über GitHub teilen</option>'
        '<option value="repository_visible">Repository-sichtbar — alle Repository-Leser können die Datei sehen</option>'
        '</select></label>'
        '<button type="button" id="project-new-create">Neues Projekt erstellen</button>'
        '<p class="project-status" id="project-new-status" role="status" aria-live="polite"></p>'
        '</div>'
        '<p class="project-security">Der Browser übergibt weiterhin keinen Dateipfad. Windows bestimmt den Speicherort. '
        'Für vertrauliche Schutzklassen blockieren sowohl der lokale Handler als auch die ProjectOS-CLI einen Speicherort '
        'innerhalb dieses allgemeinen Quell-Repositories.</p>'
        '</section></div>'
        '<section class="project-panel project-access-panel"><h3>ProjectOS-Dateirechte</h3>'
        '<div class="project-note"><strong>Zwei Schutzebenen:</strong> Die folgenden ProjectOS-Rechte steuern Aktionen innerhalb '
        'einer vertrauenswürdigen ProjectOS-Laufzeit. Sie können eine bereits über Git zugängliche Datei nicht unsichtbar machen. '
        'Die tatsächliche Dateisichtbarkeit muss deshalb zusätzlich durch einen privaten Speicherort bzw. ein separates privates '
        'GitHub-Repository erzwungen werden.</div>'
        f'<p class="project-access-legend">{permission_legend}</p>{access_matrix}'
        '<p class="project-security">Die Rechte werden aus dem vorhandenen <code>ProjectOSUserManagementState</code> gelesen. '
        'Es werden keine Freigaben automatisch erfunden. Eine lokale Cockpit-Identitätsauswahl oder Simulation ist keine '
        'Authentifizierung und darf daher keine echten Dateirechte erteilen.</p>'
        '</section></section>'
        '<script type="text/javascript">(()=>{'
        'const input=document.getElementById("project-new-name");const protection=document.getElementById("project-new-protection");'
        'const button=document.getElementById("project-new-create");const status=document.getElementById("project-new-status");'
        'if(!input||!protection||!button||!status)return;'
        'function validName(value){const name=value.trim();if(!name||name.length>80)return false;'
        'return !/[\\\\/:*?"<>|\\x00-\\x1f]/.test(name);}'
        'button.addEventListener("click",()=>{const name=input.value.trim();const mode=protection.value;'
        'if(document.body.classList.contains("cockpit-simulation")){status.textContent="Im Simulationsmodus werden keine Projektdateien erzeugt.";return;}'
        'if(!validName(name)){status.textContent="Bitte einen gültigen Projektnamen ohne Dateipfadzeichen eingeben.";input.focus();return;}'
        'if(!["private_team","restricted_local","repository_visible"].includes(mode)){status.textContent="Ungültige Schutzklasse.";return;}'
        'status.textContent="Windows-Speicherdialog wird geöffnet …";'
        'window.location.href=`projectos-z://new?name=${encodeURIComponent(name)}&protection=${encodeURIComponent(mode)}`;'
        '});'
        '})();</script>'
    )
