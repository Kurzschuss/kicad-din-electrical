from __future__ import annotations

from dataclasses import dataclass
from html import escape
from pathlib import Path
import re

from tools.validate_device_catalog import REPO_ROOT


_CATEGORY_LABELS = {
    "00_Project": "Projektgrundlagen",
    "01_Roadmap": "Planung",
    "02_User": "Benutzer",
    "03_Developer": "Entwicklung",
    "04_Reference": "Referenz",
    "projectos": "ProjectOS",
    "handover": "Übergaben",
}

_ROOT_MARKDOWN = (
    "README.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "CHANGELOG.md",
)


@dataclass(frozen=True)
class DocumentationEntry:
    title: str
    category: str
    path: str
    relative_url: str
    summary: str
    line_count: int
    byte_count: int


def _title_from_markdown(path: Path, text: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            title = stripped[2:].strip()
            if title:
                return title
    return path.stem.replace("_", " ").replace("-", " ")


def _plain_markdown(value: str) -> str:
    value = re.sub(r"!\[([^\]]*)\]\([^)]*\)", r"\1", value)
    value = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", value)
    value = value.replace("`", "").replace("**", "").replace("__", "")
    value = value.replace("*", "").replace("_", " ")
    return " ".join(value.split())


def _summary_from_markdown(text: str) -> str:
    paragraph: list[str] = []
    in_code = False
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        if not line:
            if paragraph:
                break
            continue
        if line.startswith("#") or line.startswith(("- ", "* ", "+ ", "> ", "|")):
            if paragraph:
                break
            continue
        if re.match(r"^\d+[.)]\s", line):
            if paragraph:
                break
            continue
        paragraph.append(line)
    summary = _plain_markdown(" ".join(paragraph))
    if not summary:
        return "Keine Kurzbeschreibung im Dokument vorhanden."
    if len(summary) > 280:
        return summary[:277].rstrip() + "…"
    return summary


def _category_for(path: Path) -> str:
    relative = path.relative_to(REPO_ROOT)
    if relative.parts and relative.parts[0] != "docs":
        return "Projekt"
    if len(relative.parts) >= 2:
        return _CATEGORY_LABELS.get(relative.parts[1], "Dokumentation")
    return "Dokumentation"


def _relative_url(path: Path) -> str:
    relative = path.relative_to(REPO_ROOT)
    if relative.parts and relative.parts[0] == "docs":
        return "../" + Path(*relative.parts[1:]).as_posix()
    return "../../" + relative.as_posix()


def _candidate_paths() -> tuple[Path, ...]:
    paths = {path for path in (REPO_ROOT / "docs").rglob("*.md") if path.is_file()}
    for name in _ROOT_MARKDOWN:
        path = REPO_ROOT / name
        if path.is_file():
            paths.add(path)
    return tuple(sorted(paths, key=lambda item: item.relative_to(REPO_ROOT).as_posix().casefold()))


def collect_documentation(paths: tuple[Path, ...] | None = None) -> tuple[DocumentationEntry, ...]:
    """Liest vorhandene Markdown-Dokumente read-only aus dem Repository."""
    source = _candidate_paths() if paths is None else paths
    entries: list[DocumentationEntry] = []
    for path in source:
        text = path.read_text(encoding="utf-8")
        encoded = text.encode("utf-8")
        entries.append(
            DocumentationEntry(
                title=_title_from_markdown(path, text),
                category=_category_for(path),
                path=path.relative_to(REPO_ROOT).as_posix(),
                relative_url=_relative_url(path),
                summary=_summary_from_markdown(text),
                line_count=len(text.splitlines()),
                byte_count=len(encoded),
            )
        )
    return tuple(sorted(entries, key=lambda item: (item.category.casefold(), item.title.casefold(), item.path.casefold())))


def _options(values: tuple[str, ...]) -> str:
    return "".join(f'<option value="{escape(value, quote=True)}">{escape(value)}</option>' for value in values)


def _inspector_template(item: DocumentationEntry, index: int) -> str:
    return (
        f'<template id="documentation-inspector-{index}">'
        '<div class="documentation-inspector-fixed">'
        f'<h3>{escape(item.title)}</h3>'
        '<dl class="documentation-properties">'
        f'<dt>Bereich</dt><dd>{escape(item.category)}</dd>'
        f'<dt>Pfad</dt><dd><code>{escape(item.path)}</code></dd>'
        f'<dt>Zeilen</dt><dd>{item.line_count}</dd>'
        f'<dt>Größe</dt><dd>{item.byte_count} Byte</dd>'
        '</dl>'
        '<h3>Kurzbeschreibung</h3>'
        f'<p>{escape(item.summary)}</p>'
        '<div class="documentation-open">'
        f'<a href="{escape(item.relative_url, quote=True)}" target="_blank" rel="noopener">Dokument öffnen</a>'
        '</div>'
        '</div>'
        '</template>'
    )


def documentation_page_html(entries: tuple[DocumentationEntry, ...] | None = None) -> str:
    """Rendert den read-only Dokumentationsbrowser für Z_Cockpit."""
    items = collect_documentation() if entries is None else entries
    categories = tuple(sorted({item.category for item in items}, key=str.casefold))

    rows: list[str] = []
    templates: list[str] = []
    for index, item in enumerate(items):
        search_value = " ".join((item.title, item.category, item.path, item.summary)).casefold()
        rows.append(
            f'<tr class="documentation-row" tabindex="0" data-index="{index}" '
            f'data-category="{escape(item.category, quote=True)}" '
            f'data-search="{escape(search_value, quote=True)}">'
            f'<th scope="row"><strong>{escape(item.title)}</strong></th>'
            f'<td>{escape(item.category)}</td>'
            f'<td><code>{escape(item.path)}</code></td>'
            f'<td>{item.line_count}</td></tr>'
        )
        templates.append(_inspector_template(item, index))

    table_rows = "".join(rows) if rows else '<tr><td colspan="4">Keine Markdown-Dokumente gefunden.</td></tr>'

    return (
        '<style>'
        '#page-dokumentation.active{position:absolute;inset:0;display:flex;flex-direction:column;min-height:0;overflow:hidden;padding:0}'
        '.documentation-workspace{display:grid;grid-template-columns:minmax(0,1fr) 380px;height:100%;min-height:0;overflow:hidden}'
        '.documentation-main{min-width:0;min-height:0;padding:1rem;display:flex;flex-direction:column;overflow:hidden}'
        '.documentation-title{margin:0 0 .25rem;flex:0 0 auto}'
        '.documentation-subtitle{margin:.1rem 0 .8rem;opacity:.78;flex:0 0 auto}'
        '.documentation-filters{display:grid;grid-template-columns:minmax(220px,2fr) minmax(150px,1fr);gap:.6rem;margin-bottom:.8rem;flex:0 0 auto}'
        '.documentation-filters input,.documentation-filters select{padding:.45rem;width:100%}'
        '.documentation-table-wrap{flex:1 1 auto;min-height:0;overflow:auto;border:1px solid #8886}'
        '.documentation-table{border-collapse:collapse;width:100%;min-width:820px}'
        '.documentation-table th,.documentation-table td{padding:.55rem .65rem;border-bottom:1px solid #8884;text-align:left;white-space:nowrap}'
        '.documentation-table td:nth-child(3){white-space:normal;min-width:320px}'
        '.documentation-table thead th{position:sticky;top:0;background:Canvas;z-index:1}'
        '.documentation-table th[scope="row"]{position:static;background:transparent}'
        '.documentation-row{cursor:pointer}'
        '.documentation-row:hover{background:#2878c812}'
        '.documentation-row.selected{background:#2878c81f;font-weight:600}'
        '.documentation-result-count{margin:.65rem 0 0;font-size:.9rem;opacity:.8;flex:0 0 auto}'
        '.documentation-inspector{min-width:0;min-height:0;height:100%;padding:1rem;display:flex;flex-direction:column;overflow:hidden;border-left:1px solid #8886}'
        '.documentation-inspector>h2{margin-top:0;flex:0 0 auto}'
        '#documentation-inspector-content{min-height:0;flex:1 1 auto;overflow:auto;scrollbar-gutter:stable}'
        '.documentation-inspector-fixed>h3{margin:.25rem 0 .7rem}'
        '.documentation-properties{display:grid;grid-template-columns:1fr 1.55fr;gap:.45rem .7rem;margin:0 0 1rem}'
        '.documentation-properties dt{font-weight:700}.documentation-properties dd{margin:0;min-width:0;overflow-wrap:anywhere}'
        '.documentation-properties code{white-space:normal;overflow-wrap:anywhere}'
        '.documentation-open{margin-top:1rem;padding-top:.8rem;border-top:1px solid #8885}'
        '.documentation-open a{display:inline-block;padding:.5rem .7rem;border:1px solid #2878c888;border-radius:.35rem;text-decoration:none;font-weight:700}'
        '.documentation-note{padding:.7rem;border:1px solid #2878c866;border-left:5px solid #2878c8;border-radius:.4rem;margin:0 0 .8rem;flex:0 0 auto}'
        '@media(max-width:1050px){.documentation-workspace{grid-template-columns:1fr}.documentation-inspector{height:auto;max-height:40vh;border-left:0;border-top:1px solid #8886}.documentation-filters{grid-template-columns:1fr}}'
        '</style>'
        '<section class="page" id="page-dokumentation"><div class="documentation-workspace">'
        '<div class="documentation-main">'
        '<h2 class="documentation-title">Dokumentation</h2>'
        '<p class="documentation-subtitle">Durchsuchbarer Index der vorhandenen Markdown-Dokumentation im Repository.</p>'
        '<div class="documentation-note"><strong>Read-only:</strong> Titel, Kurzbeschreibung und Metadaten werden beim Erzeugen des Z_Cockpits direkt aus den vorhandenen Dokumentdateien gelesen. Es gibt keine zweite Dokumentationsdatenbank.</div>'
        '<div class="documentation-filters">'
        '<label>Suche<input id="documentation-filter-search" type="search" placeholder="Titel, Pfad oder Inhalt durchsuchen"></label>'
        f'<label>Bereich ({len(categories)})<select id="documentation-filter-category"><option value="">Alle</option>{_options(categories)}</select></label>'
        '</div>'
        '<div class="documentation-table-wrap"><table class="documentation-table" id="documentation-overview">'
        '<thead><tr><th>Titel</th><th>Bereich</th><th>Pfad</th><th>Zeilen</th></tr></thead>'
        f'<tbody>{table_rows}</tbody></table></div>'
        f'<p class="documentation-result-count" id="documentation-result-count">{len(items)} Dokument(e)</p>'
        '</div>'
        '<section class="documentation-inspector"><h2>Dokument</h2>'
        '<div id="documentation-inspector-content"><p>Dokument auswählen.</p></div></section>'
        f'{"".join(templates)}'
        '</div></section>'
        '<script type="text/javascript">(()=>{'
        'const table=document.getElementById("documentation-overview");if(!table)return;'
        'const rows=[...table.querySelectorAll(".documentation-row")];'
        'const search=document.getElementById("documentation-filter-search");'
        'const category=document.getElementById("documentation-filter-category");'
        'const count=document.getElementById("documentation-result-count");'
        'const inspector=document.getElementById("documentation-inspector-content");let selected=null;'
        'function selectRow(row){rows.forEach(item=>item.classList.remove("selected"));row.classList.add("selected");selected=row;'
        'const tpl=document.getElementById(`documentation-inspector-${row.dataset.index}`);inspector.innerHTML="";inspector.appendChild(tpl.content.cloneNode(true));}'
        'function apply(){const term=search.value.trim().toLocaleLowerCase("de");const wanted=category.value;let visible=0;let first=null;'
        'rows.forEach(row=>{const show=(!wanted||row.dataset.category===wanted)&&(!term||row.dataset.search.includes(term));row.hidden=!show;if(show){visible+=1;if(!first)first=row;}});'
        'count.textContent=`${visible} Dokument(e)`;if(selected&&selected.hidden)selected=null;if(!selected&&first)selectRow(first);if(!first){inspector.innerHTML="<p>Keine Dokumente für diesen Filter.</p>";}}'
        'rows.forEach(row=>{row.addEventListener("click",()=>selectRow(row));row.addEventListener("keydown",event=>{if(event.key==="Enter"||event.key===" "){event.preventDefault();selectRow(row);}});});'
        'search.addEventListener("input",apply);category.addEventListener("change",apply);apply();'
        '})();</script>'
    )
