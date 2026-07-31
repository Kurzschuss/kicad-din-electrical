"""Tests for KiCad field validation in the sync view model."""
import pytest

from .din_editor_change_service import DinEditorChangeService
from .din_editor_session import DinEditorSession
from .din_editor_sync_service import DinEditorSyncService
from .din_editor_sync_view_model import DinEditorSyncViewModel


def _view_model():
    session = DinEditorSession(components=[])
    return DinEditorSyncViewModel(DinEditorSyncService(DinEditorChangeService(session)))


@pytest.mark.parametrize("fields", [None, "broken", {}, ["broken"], [None]])
def test_refresh_rejects_non_object_kicad_fields(fields):
    view_model = _view_model()
    if fields is None:
        assert view_model.refresh() ["conflicts"] == []
    else:
        with pytest.raises(ValueError):
            view_model.refresh(fields)


def test_refresh_copies_field_objects():
    view_model = _view_model()
    field = {"reference": "X5", "label": "24V"}
    view_model.refresh([field])
    field["label"] = "mutated"

    assert view_model._kicad_fields == [{"reference": "X5", "label": "24V"}]
