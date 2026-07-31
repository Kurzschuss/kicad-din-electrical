"""Tests for serialized DIN editor session validation."""
import pytest

from .din_editor_serialization import import_session


def test_import_session_rejects_non_object_data():
    with pytest.raises(ValueError, match="invalid DIN editor session"):
        import_session([])


@pytest.mark.parametrize("components", ["broken", {}, [None], [{"reference": "X5"}, "broken"]])
def test_import_session_rejects_malformed_components(components):
    with pytest.raises(ValueError, match="components must be a list of objects"):
        import_session({"version": 1, "components": components})


def test_import_session_copies_components():
    component = {"reference": "X5", "label": "24V"}
    session = import_session({"version": 1, "components": [component]})
    component["label"] = "mutated"

    assert session.components == [{"reference": "X5", "label": "24V"}]
