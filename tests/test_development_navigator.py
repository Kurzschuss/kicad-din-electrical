from tools.z_cockpit import (
    blocked_tasks,
    development_navigator_html,
    load_project_state,
    recommended_work,
)


def test_recommends_next_executable_task():
    state = load_project_state()
    recommendation = recommended_work(state)
    assert recommendation is not None
    assert recommendation.task_id == "projektvalidator"
    assert recommendation.task_state == "planned"
    assert recommendation.milestone_title_de == "Qualitätssicherung"


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
    assert "Projektanalyse und Konsistenzprüfung umsetzen" in html
    assert "Geplant" in html
    assert "Später nach Freigabe" in html
    assert "GitHub-Ruleset gemeinsam prüfen und aktivieren" in html
