from __future__ import annotations


def editor_links_html() -> str:
    """Ergänzt Geräte- und Bibliotheksinspektor um lokale KiCad-Editoraufrufe.

    Die statische HTML-Datei führt selbst keine Prozesse aus. Sie verwendet ausschließlich
    das lokale ``kicad-z:``-Protokoll, dessen Windows-Handler Repository-IDs validiert.
    """
    return r'''
<style>
.kicad-editor-actions{display:flex;gap:.55rem;flex-wrap:wrap;align-items:center;margin:.7rem 0 1rem;padding:.65rem;border:1px solid #8886;border-radius:.4rem}
.kicad-editor-actions a{display:inline-block;padding:.48rem .65rem;border:1px solid #2878c888;border-radius:.35rem;text-decoration:none;font-weight:650}
.kicad-editor-actions a:hover{background:#2878c812}
.kicad-editor-actions .kicad-editor-disabled{opacity:.5;cursor:not-allowed;border-color:#8886}
.kicad-editor-actions small{flex-basis:100%;opacity:.72;line-height:1.35}
</style>
<script type="text/javascript">
(()=>{
const SYMBOL_RE=/^[A-Za-z0-9_.+-]+:[A-Za-z0-9_.+-]+$/;
const FOOTPRINT_RE=/^[A-Za-z0-9_.+-]+$/;
const NON_FOOTPRINTS=new Set(["", "Nicht zugeordnet", "optional", "required", "forbidden", "none", "–"]);
function editorUri(kind,key,value){return `kicad-z://${kind}?${key}=${encodeURIComponent(value)}`;}
function action(label,href,title){const a=document.createElement("a");a.textContent=label;a.href=href;a.title=title;return a;}
function disabled(label,title){const span=document.createElement("span");span.className="kicad-editor-disabled";span.textContent=label;span.title=title;return span;}
function buildActions(symbol,footprint){
 const box=document.createElement("div");box.className="kicad-editor-actions";box.dataset.kicadEditorActions="1";
 if(SYMBOL_RE.test(symbol)) box.appendChild(action("Symbol-Editor öffnen",editorUri("symbol","reference",symbol),"KiCad Symbol Editor öffnen; die technische Symbolreferenz wird in die Zwischenablage gelegt."));
 else box.appendChild(disabled("Symbol-Editor öffnen","Keine gültige Repository-Symbolreferenz verfügbar."));
 if(FOOTPRINT_RE.test(footprint)&&!NON_FOOTPRINTS.has(footprint)) box.appendChild(action("Footprint direkt öffnen",editorUri("footprint","name",footprint),"Den zugeordneten Repository-Footprint direkt im KiCad Footprint Editor öffnen."));
 else box.appendChild(disabled("Footprint direkt öffnen","Kein zugeordneter Repository-Footprint verfügbar."));
 const note=document.createElement("small");note.textContent="Lokale Windows-Integration über tools\\windows\\open_z_cockpit.bat. Es werden nur validierte Repository-IDs an den KiCad-Handler übergeben.";box.appendChild(note);
 return box;
}
function injectDevice(row){
 const details=document.querySelector("#page-geraete .details");const properties=document.getElementById("properties");if(!details||!properties||!row)return;
 details.querySelectorAll('[data-kicad-editor-actions="1"]').forEach(item=>item.remove());
 const symbol=(row.cells[7]?.textContent||"").trim();const footprint=(row.cells[8]?.textContent||"").trim();
 properties.insertAdjacentElement("afterend",buildActions(symbol,footprint));
}
function injectLibrary(row){
 const fixed=document.querySelector("#library-symbol-inspector .library-inspector-fixed");if(!fixed||!row)return;
 fixed.querySelectorAll('[data-kicad-editor-actions="1"]').forEach(item=>item.remove());
 const symbol=(row.dataset.symbol||"").trim();const footprint=(row.dataset.footprint||"").trim();const box=buildActions(symbol,footprint);
 const firstPreviewTitle=fixed.querySelector(".library-inspector-preview-title");if(firstPreviewTitle)fixed.insertBefore(box,firstPreviewTitle);else fixed.appendChild(box);
}
document.addEventListener("click",event=>{
 const deviceRow=event.target.closest("#devices tbody tr");if(deviceRow)requestAnimationFrame(()=>injectDevice(deviceRow));
 const libraryRow=event.target.closest(".library-symbol-row");if(libraryRow)requestAnimationFrame(()=>injectLibrary(libraryRow));
});
document.addEventListener("keydown",event=>{
 if(event.key!=="Enter"&&event.key!==" ")return;
 const deviceRow=event.target.closest("#devices tbody tr");if(deviceRow)requestAnimationFrame(()=>injectDevice(deviceRow));
 const libraryRow=event.target.closest(".library-symbol-row");if(libraryRow)requestAnimationFrame(()=>injectLibrary(libraryRow));
});
window.addEventListener("load",()=>{
 const selectedDevice=document.querySelector("#devices tbody tr.selected");if(selectedDevice)injectDevice(selectedDevice);
 const selectedLibrary=document.querySelector(".library-symbol-row.selected");if(selectedLibrary)injectLibrary(selectedLibrary);
});
})();
</script>
'''
