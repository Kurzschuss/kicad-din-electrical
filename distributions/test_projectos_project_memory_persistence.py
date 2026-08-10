from uuid import uuid4

import pytest

from .projectos_project_memory import ProjectOSKnowledgeElement, ProjectOSProjectMemory
from .projectos_project_memory_persistence import (
    PROJECT_MEMORY_PERSISTENCE_VERSION,
    ProjectOSProjectMemoryState,
    load_project_memory_state,
    save_project_memory_state,
)


def _element(project_id: str, title: str, *, correlation_id: str | None = None, causation_id: str | None = None):
    return ProjectOSKnowledgeElement(
        knowledge_type="decision",
        title=title,
        content=f"Inhalt {title}",
        project_id=project_id,
        correlation_id=correlation_id,
        causation_id=causation_id,
    )


def test_project_memory_persistence_roundtrip_preserves_graph_and_diagnostic_context(tmp_path):
    project_id = str(uuid4())
    correlation_id = str(uuid4())
    message_id = str(uuid4())
    memory = ProjectOSProjectMemory(project_id)
    first = memory.add(_element(project_id, "A", correlation_id=correlation_id, causation_id=message_id))
    second = memory.add(_element(project_id, "B"))
    relation = memory.relate(first, second, "justifies", metadata={"source": "test"})
    path = tmp_path / "runtime-memory.json"

    save_project_memory_state(
        path,
        memory,
        known_message_ids=[message_id],
        known_correlation_ids=[correlation_id],
        saved_at="2026-08-10T18:00:00+00:00",
    )
    loaded = load_project_memory_state(path)

    assert loaded.project_id == project_id
    assert loaded.saved_at == "2026-08-10T18:00:00+00:00"
    assert loaded.known_message_ids == (message_id,)
    assert loaded.known_correlation_ids == (correlation_id,)
    assert [item.knowledge_id for item in loaded.memory.elements()] == [first.knowledge_id, second.knowledge_id]
    assert loaded.memory.relations()[0].relation_id == relation.relation_id
    assert loaded.memory.relations()[0].metadata == {"source": "test"}
    assert loaded.as_dict()["version"] == PROJECT_MEMORY_PERSISTENCE_VERSION
    assert "knowledge_diagnostics" in loaded.as_dict()["derived_not_persisted"]


def test_project_memory_persistence_rejects_unsupported_version():
    project_id = str(uuid4())
    with pytest.raises(ValueError, match="unsupported project memory persistence version"):
        ProjectOSProjectMemoryState.from_dict(
            {
                "version": 999,
                "project_id": project_id,
                "elements": [],
                "relations": [],
            }
        )


def test_project_memory_persistence_rejects_cross_project_element():
    project_id = str(uuid4())
    other_project_id = str(uuid4())
    element = _element(other_project_id, "Fremd")
    with pytest.raises(ValueError, match="another project"):
        ProjectOSProjectMemoryState.from_dict(
            {
                "version": PROJECT_MEMORY_PERSISTENCE_VERSION,
                "project_id": project_id,
                "saved_at": "2026-08-10T18:00:00+00:00",
                "known_message_ids": [],
                "known_correlation_ids": [],
                "elements": [element.as_dict()],
                "relations": [],
            }
        )
