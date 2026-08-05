from __future__ import annotations

from html import escape

from .security_status import SecurityItem, collect_security_status


_STATE_LABELS = {
    "vorhanden": "Vorhanden",
    "fehlt": "Fehlt",
    "vorbereitet": "Vorbereitet",
    "laufzeitpruefung": "Laufzeitprüfung",
}


def security_state_label(state: str) -> str:
    try:
        return _STATE_LABELS[state]
    except KeyError as exc:
        raise ValueError(f"Unbekannter Sicherheitszustand: {state}") from exc


def security_table_html(items: tuple[SecurityItem, ...] | None = None) -> str:
    status_items = collect_security_status() if items is None else items
    rows = []
    for item in status_items:
        label = security_state_label(item.state)
        rows.append(
            f'<tr data-security="{escape(item.security_id)}" data-state="{escape(item.state)}">'
            f'<th scope="row">{escape(item.label_de)}</th>'
            f'<td><strong>{escape(label)}</strong></td>'
            f'<td>{escape(item.detail_de)}</td>'
            '</tr>'
        )
    return (
        '<div class="security-table-wrap"><table class="security-table">'
        '<thead><tr><th>Bereich</th><th>Zustand</th><th>Erläuterung</th></tr></thead>'
        f'<tbody>{"".join(rows)}</tbody></table></div>'
    )


def security_page_html(items: tuple[SecurityItem, ...] | None = None) -> str:
    table = security_table_html(items)
    return (
        '<section class="page" id="page-sicherheit">'
        '<h2>Sicherheit</h2>'
        '<p>Übersicht der lokal prüfbaren Schutzmechanismen. '
        'Laufzeit- und GitHub-Zustände werden nicht als bestätigt dargestellt.</p>'
        f'{table}'
        '<aside class="security-notice">'
        '<strong>Wichtig:</strong> Eine vorhandene Ruleset-Vorlage bedeutet nicht, '
        'dass der Repository-Schutz auf GitHub bereits aktiviert ist.'
        '</aside></section>'
    )
