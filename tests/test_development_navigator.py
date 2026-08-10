from tools.z_cockpit import (
    blocked_tasks,
    development_navigator_html,
    load_project_state,
    recommended_work,
)


def test_no_executable_task_remains_after_issue_workflow():
    state = load_project_state()
    assert recommended_work(state) is None


def test_projectvalidator_user_permissions_and_issue_workflow_are_marked_done():
    state = load_project_state()
    tasks = {
        task.task_id: task
        for milestone in state.milestones
        for task in milestone.tasks
    }
    assert tasks["projektvalidator"].state == "done"
    assert tasks["benutzerverwaltung"].state == "done"
    assert tasks["whitelist_verwaltung"].state == "done"
    assert tasks["issue_fehlermeldung"].state == "done"


def test_blocked_ruleset_is_not_recommended():
    state = load_project_state()
    assert recommended_work(state) is None
    assert "GitHub-Ruleset gemeinsam prüfen und aktivieren" in blocked_tasks(state)


def test_navigator_html_shows_complete_state_and_blocked_work_separately():
    html = development_navigator_html(load_project_state())
    assert "Entwicklungsnavigator" in html
    assert "Keine ausführbare Aufgabe offen." in html
    assert "Später nach Freigabe" in html
    assert "GitHub-Ruleset gemeinsam prüfen und aktivieren" in html
