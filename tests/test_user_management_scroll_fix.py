from datetime import datetime, timezone

from tools.z_cockpit import user_management_page_html
from tools.z_cockpit.user_management_page import collect_user_management
from tools.z_cockpit.user_management_scroll_fix import user_management_scroll_fix_html


AT = datetime(2026, 8, 11, 0, 0, tzinfo=timezone.utc)


def test_user_management_scroll_fix_makes_main_and_inspector_scrollable():
    html = user_management_scroll_fix_html()

    assert 'id="user-management-scroll-fix"' in html
    assert '#page-benutzer .user-management-main {' in html
    assert 'overflow-y: auto;' in html
    assert 'scrollbar-gutter: stable;' in html
    assert '#page-benutzer .user-management-table-wrap {' in html
    assert 'min-height: 16rem;' in html
    assert '#page-benutzer .user-management-inspector {' in html
    assert '#page-benutzer #user-management-inspector-content {' in html
    assert 'overflow: visible;' in html


def test_user_management_scroll_fix_switches_to_page_scroll_on_narrow_windows():
    html = user_management_scroll_fix_html()

    assert '@media (max-width: 1050px)' in html
    assert '#page-benutzer.active {' in html
    assert 'min-height: 100%;' in html
    assert 'max-height: none;' in html
    assert 'min-height: 18rem;' in html


def test_combined_user_management_includes_scroll_fix_after_governance_controls():
    snapshot = collect_user_management(at=AT)
    html = user_management_page_html(snapshot)

    governance_index = html.rfind('id="governance-model"')
    fix_index = html.rfind('id="user-management-scroll-fix"')
    assert governance_index >= 0
    assert fix_index > governance_index
