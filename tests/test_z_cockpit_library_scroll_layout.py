from tools.z_cockpit.library_page import library_page_html


def test_library_page_keeps_heading_filters_and_inspector_fixed_while_content_scrolls():
    html = library_page_html(())

    heading = '<h2 class="library-page-title">'
    filters = '<div class="library-filters">'
    table_scroll = '<div class="library-overview-wrap">'

    assert '<div class="library-list-scroll">' in html
    assert heading in html
    assert filters in html
    assert table_scroll in html
    assert html.index(heading) < html.index(filters) < html.index(table_scroll)
    assert '#page-bibliotheken.active{position:absolute;inset:0;display:flex;flex-direction:column;' in html
    assert 'min-height:0;overflow:hidden;padding:0}' in html
    assert '.library-list-scroll{flex:1 1 auto;min-height:0;overflow:hidden;' in html
    assert '.library-workspace{display:grid;grid-template-columns:minmax(0,1fr) 360px;' in html
    assert '.library-main{min-width:0;min-height:0;padding:1rem;display:flex;flex-direction:column;overflow:hidden}' in html
    assert '.library-inspector{min-width:0;min-height:0;height:100%;padding:1rem;display:flex;' in html
    assert 'flex-direction:column;overflow:hidden;border-left:1px solid #8886}' in html
    assert '#library-symbol-inspector{min-height:0;flex:1 1 auto;display:flex;flex-direction:column;overflow:hidden}' in html
    assert '.library-device-id-scroll{min-height:0;flex:1 1 auto;overflow-y:auto;overflow-x:hidden;' in html
    assert '.library-overview-wrap{flex:1 1 auto;min-height:0;overflow:auto;' in html
    assert '.library-overview-table thead th{position:sticky;top:0;background:Canvas;z-index:1}' in html
