from __future__ import annotations

from dataclasses import dataclass
from html import escape

from .project_model import ProjectState, load_project_state


@dataclass(frozen=True)
class CockpitSettingsSnapshot:
    project_name: str
    display_name: str
    language: str
    phase: str
    target_release: str
    project_state_path: str = "project_state.yaml"
    device_catalog_path: str = "data/devices/"
    symbol_library_path: str = "symbols/"
    footprint_library_path: str = "footprints/"
    documentation_path: str = "docs/"
    cockpit_output_path: str = "docs/site/z-cockpit.html"
    python_requirement: str = ">=3.11"
    generator_command: str = "python -m tools.generate_z_cockpit"


def collect_settings(project: ProjectState | None = None) -> CockpitSettingsSnapshot:
    """Liest die projektweiten Einstellungen aus bestehenden Quellen read-only aus."""
    state = load_project_state() if project is None else project
    return CockpitSettingsSnapshot(
        project_name=state.name,
        display_name=state.display_name,
        language=state.language,
        phase=state.phase,
        target_release=state.target_release,
    )


def _row(label: str, value: str, *, code: bool = False) -> str:
    content = f"<code>{escape(value)}</code>" if code else escape(value)
    return f"<tr><th scope=\"row\">{escape(label)}</th><td>{content}</td></tr>"


def settings_page_html(snapshot: CockpitSettingsSnapshot | None = None) -> str:
    """Rendert Repository-Einstellungen read-only und lokale Browserpräferenzen editierbar."""
    item = collect_settings() if snapshot is None else snapshot
    project_rows = "".join(
        (
            _row("Projekt", item.display_name),
            _row("Technischer Name", item.project_name, code=True),
            _row("Projektsprache", item.language, code=True),
            _row("Phase", item.phase),
            _row("Zielrelease", item.target_release),
        )
    )
    path_rows = "".join(
        (
            _row("Projektmodell", item.project_state_path, code=True),
            _row("Gerätekatalog", item.device_catalog_path, code=True),
            _row("Symbolbibliotheken", item.symbol_library_path, code=True),
            _row("Footprintbibliotheken", item.footprint_library_path, code=True),
            _row("Dokumentation", item.documentation_path, code=True),
            _row("Z_Cockpit-Ausgabe", item.cockpit_output_path, code=True),
        )
    )
    developer_rows = "".join(
        (
            _row("Python", item.python_requirement, code=True),
            _row("Cockpit erzeugen", item.generator_command, code=True),
            _row("Persistenz lokaler Optionen", "Browser localStorage"),
        )
    )

    return (
        '<style>'
        ':root[data-cockpit-theme="light"]{color-scheme:light}'
        ':root[data-cockpit-theme="dark"]{color-scheme:dark}'
        'body.cockpit-compact th,body.cockpit-compact td{padding:.32rem .45rem}'
        'body.cockpit-compact .page-link{padding:.42rem .55rem}'
        '#page-einstellungen.active{display:block;min-height:100%}'
        '.settings-layout{display:grid;grid-template-columns:minmax(0,1.35fr) minmax(320px,.85fr);gap:1rem;align-items:start}'
        '.settings-panel{border:1px solid #8886;border-radius:.5rem;padding:1rem}'
        '.settings-panel h3{margin-top:0}'
        '.settings-table{width:100%;min-width:0;border-collapse:collapse}'
        '.settings-table th,.settings-table td{padding:.5rem .6rem;border-bottom:1px solid #8884;text-align:left;white-space:normal;vertical-align:top}'
        '.settings-table th{width:38%;position:static;background:transparent}'
        '.settings-stack{display:grid;gap:1rem}'
        '.settings-control{display:grid;gap:.35rem;margin:.8rem 0}'
        '.settings-control select{max-width:260px}'
        '.settings-check{display:flex;align-items:flex-start;gap:.55rem;margin:.8rem 0;font-size:.95rem}'
        '.settings-check input{margin-top:.22rem}'
        '.settings-note{padding:.75rem;border:1px solid #2878c866;border-left:5px solid #2878c8;border-radius:.4rem;margin:.8rem 0}'
        '.settings-actions{display:flex;gap:.7rem;flex-wrap:wrap;margin-top:1rem}'
        '.settings-actions button{padding:.55rem .8rem;cursor:pointer}'
        '.settings-status{min-height:1.4rem;margin:.7rem 0 0;font-size:.9rem;font-weight:600}'
        '.settings-developer[hidden]{display:none}'
        '@media(max-width:1000px){.settings-layout{grid-template-columns:1fr}}'
        '</style>'
        '<section class="page" id="page-einstellungen"><h2>Einstellungen</h2>'
        '<p>Projektwerte werden aus den vorhandenen Repository-Quellen gelesen. Änderbare Oberflächenoptionen gelten nur lokal in diesem Browser.</p>'
        '<div class="settings-layout"><div class="settings-stack">'
        '<section class="settings-panel"><h3>Projekt</h3><table class="settings-table"><tbody>'
        f'{project_rows}</tbody></table></section>'
        '<section class="settings-panel"><h3>Pfade</h3><table class="settings-table"><tbody>'
        f'{path_rows}</tbody></table></section>'
        '<section class="settings-panel settings-developer" id="settings-developer-details" hidden><h3>Entwicklerdetails</h3>'
        f'<table class="settings-table"><tbody>{developer_rows}</tbody></table></section>'
        '</div><section class="settings-panel"><h3>Lokale Oberfläche</h3>'
        '<div class="settings-note"><strong>Lokal:</strong> Diese Optionen ändern keine Repositorydateien und werden ausschließlich im Browser gespeichert.</div>'
        '<label class="settings-control">Erscheinungsbild<select id="setting-theme">'
        '<option value="system">Systemeinstellung</option><option value="light">Hell</option><option value="dark">Dunkel</option>'
        '</select></label>'
        '<label class="settings-control">Tabellendichte<select id="setting-density">'
        '<option value="normal">Standard</option><option value="compact">Kompakt</option>'
        '</select></label>'
        '<label class="settings-check"><input type="checkbox" id="setting-remember-page">'
        '<span>Zuletzt geöffneten Cockpit-Bereich beim nächsten Start wiederherstellen.</span></label>'
        '<label class="settings-check"><input type="checkbox" id="setting-developer-details">'
        '<span>Entwicklerdetails mit technischen Pfaden und Generatorhinweisen anzeigen.</span></label>'
        '<div class="settings-actions"><button type="button" id="settings-reset">Lokale Einstellungen zurücksetzen</button></div>'
        '<p class="settings-status" id="settings-status" role="status" aria-live="polite"></p>'
        '</section></div></section>'
        '<script type="text/javascript">(()=>{'
        'const KEY="z-cockpit.settings.v1";'
        'const defaults={theme:"system",density:"normal",rememberPage:false,developerDetails:false,lastPage:"start"};'
        'function read(){try{const raw=localStorage.getItem(KEY);if(!raw)return {...defaults};const value=JSON.parse(raw);return {...defaults,...value}}catch(_){return {...defaults}}}'
        'function write(value){try{localStorage.setItem(KEY,JSON.stringify(value));return true}catch(_){return false}}'
        'let state=read();'
        'const theme=document.getElementById("setting-theme");const density=document.getElementById("setting-density");'
        'const remember=document.getElementById("setting-remember-page");const developer=document.getElementById("setting-developer-details");'
        'const details=document.getElementById("settings-developer-details");const status=document.getElementById("settings-status");'
        'function apply(){document.documentElement.dataset.cockpitTheme=state.theme;document.documentElement.style.colorScheme=state.theme==="system"?"light dark":state.theme;'
        'document.body.classList.toggle("cockpit-compact",state.density==="compact");details.hidden=!state.developerDetails;'
        'theme.value=state.theme;density.value=state.density;remember.checked=!!state.rememberPage;developer.checked=!!state.developerDetails}'
        'function save(message){const ok=write(state);apply();status.textContent=ok?message:"Einstellung angewendet, konnte aber nicht dauerhaft im Browser gespeichert werden."}'
        'theme.addEventListener("change",()=>{state.theme=theme.value;save("Erscheinungsbild gespeichert.")});'
        'density.addEventListener("change",()=>{state.density=density.value;save("Tabellendichte gespeichert.")});'
        'remember.addEventListener("change",()=>{state.rememberPage=remember.checked;save("Startverhalten gespeichert.")});'
        'developer.addEventListener("change",()=>{state.developerDetails=developer.checked;save("Entwickleransicht gespeichert.")});'
        'document.querySelectorAll(".page-link").forEach(button=>button.addEventListener("click",()=>{if(!state.rememberPage)return;state.lastPage=button.dataset.page||"start";write(state)}));'
        'window.addEventListener("load",()=>{if(!state.rememberPage||!state.lastPage)return;const button=[...document.querySelectorAll(".page-link")].find(item=>item.dataset.page===state.lastPage);if(button)button.click()});'
        'document.getElementById("settings-reset").addEventListener("click",()=>{state={...defaults};try{localStorage.removeItem(KEY)}catch(_){}apply();status.textContent="Lokale Einstellungen wurden zurückgesetzt."});'
        'apply();'
        '})();</script>'
    )
