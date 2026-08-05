from tools.z_cockpit import (
    blocked_tasks,
    development_navigator_html,
    load_project_state,
    recommended_work,
)


def test_recommends_executable_in_progress_task():
    state = load_project_state()
    recommendation = recommended_work(state)
    assert recommendation is not None
    assert recommendation.task_id == "sicherheitsseite"
    assert recommendation.task_state == "in_progress"
    assert recommendation.milestone_title_de == "Z_Cockpit"


def test_blocked_ruleset_is_not_recommended():
    state = load_project_state()
    recommendation = recommended_work(state)
    assert recommendation is not None
    assert recommendation.task_id != "ruleset"
    assert "GitHub-Ruleset gemeinsam prüfen und aktivieren" in blocked_tasks(state)


def test_navigator_html_uses_german_labels_and_separates_blocked_work():
    html = development_navigator_html(load_project_state())
    assert "Entwicklungsnavigator" in html
    assert "Als Nächstes empfohlen" in html
    assert "Sicherheitsseite sichtbar anbinden" in html
    assert "In Arbeit" in html
    assert "Später nach Freigabe" in html
    assert "GitHub-Ruleset gemeinsam prüfen und aktivieren" in html
