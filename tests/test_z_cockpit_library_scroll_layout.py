from tools.z_cockpit.library_page import library_page_html


def test_library_page_keeps_summary_visible_and_scrolls_only_library_list():
    html = library_page_html(())

    summary = '<div class="library-page-summary">'
    scroll = '<div class="library-list-scroll">'

    assert summary in html
    assert scroll in html
    assert html.index(summary) < html.index(scroll)
    assert '#page-bibliotheken.active{position:absolute;inset:0;display:flex;flex-direction:column;' in html
    assert 'min-height:0;overflow:hidden;padding:0}' in html
    assert '.library-page-summary{flex:0 0 auto;' in html
    assert '.library-list-scroll{flex:1 1 auto;min-height:0;overflow-y:auto;' in html
    assert 'scrollbar-gutter:stable' in html
