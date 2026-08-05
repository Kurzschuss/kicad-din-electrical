from tools.z_cockpit.project_dashboard import (
    next_dashboard_tasks,
    next_tasks_html,
    progress_bar_html,
    project_progress_html,
)
from tools.z_cockpit.project_model import MilestoneState, ProjectState, TaskState


def sample_project() -> ProjectState:
    return ProjectState(
        name="kicad-din-electrical",
        display_name="KiCad DIN Electrical",
        language="de",
        phase="development",
        target_release="1.0",
        milestones=(
            MilestoneState(
                "cockpit",
                "Z_Cockpit",
                (
                    TaskState("navigation", "Navigation", "done"),
                    TaskState("security-page", "Sicherheitsseite", "in_progress"),
                ),
            ),
            MilestoneState(
                "library",
                "Bibliotheken",
                (
                    TaskState("viewer", "Bibliotheksviewer", "planned"),
                    TaskState("preview", "Symbolvorschau", "blocked"),
                ),
            ),
        ),
    )


def test_next_tasks_are_prioritized_and_limited():
    tasks = next_dashboard_tasks(sample_project(), limit=2)
    assert [task.title_de for task in tasks] == ["Sicherheitsseite", "Bibliotheksviewer"]
    assert [task.state_label_de for task in tasks] == ["In Arbeit", "Geplant"]


def test_negative_limit_is_rejected():
    try:
        next_dashboard_tasks(sample_project(), limit=-1)
    except ValueError as exc:
        assert "nicht negativ" in str(exc)
    else:
        raise AssertionError("Negatives Limit muss abgelehnt werden")


def test_progress_bar_contains_accessible_values():
    html = progress_bar_html(50, "Z_Cockpit")
    assert 'aria-label="Z_Cockpit"' in html
    assert 'aria-valuenow="50"' in html
    assert 'style="width:50%"' in html
    assert "50 %" in html


def test_invalid_progress_is_rejected():
    for value in (-1, 101):
        try:
            progress_bar_html(value, "Ungültig")
        except ValueError as exc:
            assert "zwischen 0 und 100" in str(exc)
        else:
            raise AssertionError("Ungültiger Fortschritt muss abgelehnt werden")


def test_project_progress_uses_calculated_values():
    html = project_progress_html(sample_project())
    assert "Gesamtfortschritt bis Version 1.0" in html
    assert "Z_Cockpit" in html
    assert "Bibliotheken" in html
    assert html.count('aria-valuenow="25"') == 1
    assert html.count('aria-valuenow="50"') == 1
    assert html.count('aria-valuenow="0"') == 1


def test_next_tasks_html_is_german_and_shows_states():
    html = next_tasks_html(sample_project())
    assert "Nächste Aufgaben" in html
    assert "Sicherheitsseite" in html
    assert "In Arbeit" in html
    assert "Bibliotheksviewer" in html
    assert "Geplant" in html
    assert "Symbolvorschau" in html
    assert "Blockiert" in html
