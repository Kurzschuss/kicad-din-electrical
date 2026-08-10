from __future__ import annotations

from html import escape
from pathlib import Path

from .user_management_page import UserManagementSnapshot


def project_page_html(snapshot: UserManagementSnapshot) -> str:
    """Rendert den lokalen ProjectOS-Projektdatei-Workflow."""
    if snapshot.source_available:
        source = snapshot.source_label
        project_file = Path(source).name or source
        project_name = project_file.removesuffix(".projectos.json").removesuffix(".json")
        current = (
            '<div class="project-current-grid">'
            f'<div><span class="project-label">Projekt</span><strong>{escape(project_name)}</strong></div>'
            f'<div><span class="project-label">Datei</span><code>{escape(project_file)}</code></div>'
            f'<div><span class="project-label">Projekt-ID</span><code>{escape(snapshot.project_id or "–")}</code></div>'
            '<div><span class="project-label">Format</span><strong>ProjectOS v4</strong></div>'
            '</div>'
            f'<p class="project-path"><strong>Speicherort:</strong> <code>{escape(source)}</code></p>'
        )
    else:
        current = (
            '<div class="project-empty"><strong>Kein ProjectOS-Projekt aktiv.</strong> '
            'Erstelle unten ein neues Projekt. Beim nächsten Z_Cockpit-Start wird das zuletzt aktive, '
            'noch gültige Projekt automatisch wieder geladen.</div>'
        )

    return (
        '<style>'
        '#page-projekt.active{display:block;min-height:100%}'
        '.project-layout{display:grid;grid-template-columns:minmax(0,1.2fr) minmax(320px,.8fr);gap:1rem;align-items:start}'
        '.project-panel{border:1px solid #8886;border-radius:.5rem;padding:1rem}'
        '.project-panel h3{margin-top:0}'
        '.project-current-grid{display:grid;grid-template-columns:repeat(2,minmax(180px,1fr));gap:.7rem}'
        '.project-current-grid>div{padding:.65rem;border:1px solid #8885;border-radius:.4rem;min-width:0}'
        '.project-current-grid strong,.project-current-grid code,.project-label{display:block;overflow-wrap:anywhere}'
        '.project-label{font-size:.78rem;opacity:.7;margin-bottom:.2rem}'
        '.project-path{margin:.85rem 0 0;overflow-wrap:anywhere}'
        '.project-empty{padding:.85rem;border:1px dashed #8888;border-radius:.4rem}'
        '.project-new-form{display:grid;gap:.65rem}'
        '.project-new-form input{padding:.55rem .6rem;width:100%}'
        '.project-new-form button{padding:.6rem .85rem;justify-self:start;cursor:pointer;font-weight:700}'
        '.project-note{padding:.7rem;border:1px solid #2878c866;border-left:5px solid #2878c8;border-radius:.4rem;font-size:.9rem}'
        '.project-status{min-height:1.35rem;margin:.1rem 0 0;font-size:.9rem;font-weight:650}'
        '.project-security{margin:.8rem 0 0;font-size:.86rem;opacity:.8}'
        '@media(max-width:950px){.project-layout{grid-template-columns:1fr}.project-current-grid{grid-template-columns:1fr}}'
        '</style>'
        '<section class="page" id="page-projekt">'
        '<h2 class="cockpit-page-title">Projekt '
        '<small class="cockpit-page-description">(ProjectOS-Projektdatei erstellen und aktives Projekt verwalten.)</small></h2>'
        '<div class="project-layout">'
        '<section class="project-panel"><h3>Aktives Projekt</h3>'
        f'{current}</section>'
        '<section class="project-panel"><h3>Neues Projekt</h3>'
        '<div class="project-note"><strong>Speicherort:</strong> Nach Klick auf „Neues Projekt erstellen“ öffnet Windows '
        'den normalen „Speichern unter“-Dialog. Der Browser übergibt keinen Dateipfad.</div>'
        '<div class="project-new-form">'
        '<label>Projektname<input id="project-new-name" type="text" maxlength="80" autocomplete="off" '
        'placeholder="z. B. Verteilung Werkstatt"></label>'
        '<button type="button" id="project-new-create">Neues Projekt erstellen</button>'
        '<p class="project-status" id="project-new-status" role="status" aria-live="polite"></p>'
        '</div>'
        '<p class="project-security">Die Datei wird über <code>DinEditorProjectManager</code> als gültiges ProjectOS-v4-Bundle erzeugt. '
        'Das lokale Protokoll akzeptiert nur den Projektnamen; den Zielpfad bestimmt ausschließlich der Windows-Dateidialog. '
        'Im Simulationsmodus ist die Dateierzeugung gesperrt.</p>'
        '</section></div></section>'
        '<script type="text/javascript">(()=>{'
        'const input=document.getElementById("project-new-name");const button=document.getElementById("project-new-create");'
        'const status=document.getElementById("project-new-status");if(!input||!button||!status)return;'
        'function validName(value){const name=value.trim();if(!name||name.length>80)return false;'
        'return !/[\\\\/:*?"<>|\\x00-\\x1f]/.test(name);}'
        'button.addEventListener("click",()=>{const name=input.value.trim();'
        'if(document.body.classList.contains("cockpit-simulation")){status.textContent="Im Simulationsmodus werden keine Projektdateien erzeugt.";return;}'
        'if(!validName(name)){status.textContent="Bitte einen gültigen Projektnamen ohne Dateipfadzeichen eingeben.";input.focus();return;}'
        'status.textContent="Windows-Speicherdialog wird geöffnet …";'
        'window.location.href=`projectos-z://new?name=${encodeURIComponent(name)}`;'
        '});'
        '})();</script>'
    )
