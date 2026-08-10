from tools.z_cockpit import (
    blocked_tasks,
    development_navigator_html,
    load_project_state,
    recommended_work,
)


def test_whitelist_management_is_recommended_as_next_executable_task():
    state = load_project_state()
    task = recommended_work(state)
    assert task is not None
    assert task.task_id == "whitelist_verwaltung"
    assert task.task_title_de == "Whitelist- und Berechtigungsverwaltung integrieren"


def test_projectvalidator_and_user_management_are_marked_done():
    state = load_project_state()
    tasks = {
        task.task_id: task
        for milestone in state.milestones
        for task in milestone.tasks
    }
    assert tasks["projektvalidator"].state == "done"
    assert tasks["benutzerverwaltung"].state == "done"
    assert tasks["whitelist_verwaltung"].state == "planned"
    assert tasks["issue_fehlermeldung"].state == "planned"


def test_blocked_ruleset_is_not_recommended():
    state = load_project_state()
    task = recommended_work(state)
    assert task is not None
    assert task.task_id == "whitelist_verwaltung"
    assert "GitHub-Ruleset gemeinsam prüfen und aktivieren" in blocked_tasks(state)


def test_navigator_html_shows_next_expansion_and_blocked_work_separately():
    html = development_navigator_html(load_project_state())
    assert "Entwicklungsnavigator" in html
    assert "Whitelist- und Berechtigungsverwaltung integrieren" in html
    assert "Später nach Freigabe" in html
    assert "GitHub-Ruleset gemeinsam prüfen und aktivieren" in html
