from tools.z_cockpit.library_page import library_page_html


def test_library_page_keeps_heading_and_filters_fixed_while_table_scrolls():
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
    assert '.library-main{display:flex;flex-direction:column;overflow:hidden}' in html
    assert '.library-overview-wrap{flex:1 1 auto;min-height:0;overflow:auto;' in html
    assert '.library-overview-table thead th{position:sticky;top:0;background:Canvas;z-index:1}' in html
