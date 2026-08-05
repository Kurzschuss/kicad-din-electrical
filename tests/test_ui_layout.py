from tools.z_cockpit.ui_layout import cockpit_layout_css


def test_layout_keeps_navigation_top_aligned_and_sticky():
    css = cockpit_layout_css()
    assert "aside {" in css
    assert "align-self: start" in css
    assert "position: sticky" in css


def test_device_list_scrolls_without_moving_details():
    css = cockpit_layout_css()
    assert ".device-main .table-wrap" in css
    assert "overflow: auto" in css
    assert ".details" in css
    assert "overflow: hidden" in css


def test_previews_are_compact_and_visible_together():
    css = cockpit_layout_css()
    assert ".preview-grid" in css
    assert "grid-template-columns: 1fr" in css
    assert "height: clamp(120px, 24vh, 190px)" in css
    assert "object-fit: contain" in css


def test_progress_percent_is_visually_separated():
    css = cockpit_layout_css()
    assert ".progress-label" in css
    assert "justify-content: space-between" in css
    assert "gap: 1.5rem" in css
    assert ".progress-percent" in css
    assert "margin-left: auto" in css


def test_small_screens_return_to_normal_document_flow():
    css = cockpit_layout_css()
    assert "@media (max-width: 1050px)" in css
    assert "position: static" in css
    assert "overflow: visible" in css
