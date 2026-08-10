from tools.z_cockpit.documentation_page import (
    DocumentationEntry,
    collect_documentation,
    documentation_page_html,
)


def test_repository_documentation_is_collected_from_existing_markdown_files():
    entries = collect_documentation()
    paths = {item.path for item in entries}

    assert "README.md" in paths
    assert "docs/README.md" in paths
    assert "docs/03_Developer/Z_COCKPIT.md" in paths
    assert any(item.category == "Benutzer" for item in entries)
    assert any(item.category == "Entwicklung" for item in entries)
    assert any(item.category == "Referenz" for item in entries)
    assert any(item.category == "ProjectOS" for item in entries)
    assert all(item.title for item in entries)
    assert all(item.relative_url for item in entries)
    assert all(item.line_count >= 1 for item in entries)


def test_documentation_page_contains_search_category_filter_table_and_inspector():
    entries = (
        DocumentationEntry(
            title="Schnellstart",
            category="Benutzer",
            path="docs/02_User/QUICKSTART.md",
            relative_url="../02_User/QUICKSTART.md",
            summary="Kurzer Einstieg in die Bibliothek.",
            line_count=42,
            byte_count=2048,
        ),
        DocumentationEntry(
            title="Entwicklerleitfaden",
            category="Entwicklung",
            path="docs/03_Developer/DEVELOPER.md",
            relative_url="../03_Developer/DEVELOPER.md",
            summary="Hinweise für die Entwicklung.",
            line_count=80,
            byte_count=4096,
        ),
    )

    html = documentation_page_html(entries)

    assert 'id="page-dokumentation"' in html
    assert 'id="documentation-overview"' in html
    assert 'id="documentation-filter-search"' in html
    assert 'id="documentation-filter-category"' in html
    assert 'class="documentation-inspector"' in html
    assert 'id="documentation-inspector-content"' in html
    assert "Schnellstart" in html
    assert "Entwicklerleitfaden" in html
    assert "Dokument öffnen" in html
    assert "2 Dokument(e)" in html


def test_documentation_page_escapes_repository_values():
    html = documentation_page_html((
        DocumentationEntry(
            title="<script>alert(1)</script>",
            category="<Bereich>",
            path="docs/<Datei>.md",
            relative_url="../%3CDatei%3E.md",
            summary="Text <kritisch> & wichtig.",
            line_count=1,
            byte_count=10,
        ),
    ))

    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in html
    assert "&lt;Bereich&gt;" in html
    assert "Text &lt;kritisch&gt; &amp; wichtig." in html


def test_repository_documentation_page_is_renderable_and_read_only():
    html = documentation_page_html()

    assert "Durchsuchbarer Index der vorhandenen Markdown-Dokumentation" in html
    assert "Read-only" in html
    assert "keine zweite Dokumentationsdatenbank" in html
    assert "docs/README.md" in html
