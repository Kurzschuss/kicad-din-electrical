"""Tests for project bundle session and synchronization log boundaries."""
import pytest

from .din_editor_project_bundle import DinProjectBundleError, import_project_bundle


def test_bundle_requires_session_object():
    with pytest.raises(DinProjectBundleError, match="invalid DIN editor project session"):
        import_project_bundle({"version": 2, "session": [], "sync_log": []})


def test_bundle_requires_sync_log_list():
    with pytest.raises(DinProjectBundleError, match="invalid DIN synchronization log"):
        import_project_bundle({"version": 2, "session": {"components": []}, "sync_log": {}})


def test_bundle_does_not_partially_construct_on_invalid_log():
    data = {
        "version": 2,
        "session": {"version": 1, "components": [{"reference": "X5"}]},
        "sync_log": [{"timestamp": "bad", "reference": "X5", "source": "KiCad", "value": "24V", "action": "imported"}],
    }
    with pytest.raises(DinProjectBundleError, match="invalid DIN editor project data"):
        import_project_bundle(data)
