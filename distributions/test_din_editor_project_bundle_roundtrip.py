"""Round-trip tests for DIN project bundles including synchronization history and project identity."""
from datetime import datetime, timezone
from uuid import uuid4

from .din_editor_project_bundle import export_project_bundle, import_project_bundle, import_project_bundle_details
from .din_editor_session import DinEditorSession
from .din_editor_sync_log import DinSyncLog


def test_project_bundle_roundtrip_preserves_components_and_audit_history():
    session = DinEditorSession(components=[
        {"reference": "X5", "component_type": "DIN_RAIL_TERMINAL_BLOCK", "label": "Versorgung 24V", "can_edit_label": True},
    ])
    log = DinSyncLog()
    log.entries = [{
        "timestamp": datetime(2026, 7, 31, 12, 0, tzinfo=timezone.utc).isoformat(),
        "reference": "X5",
        "source": "KiCad",
        "value": "Versorgung 24V",
        "action": "imported",
    }]
    project_id = str(uuid4())
    bundle = export_project_bundle(session, log, project_id=project_id)

    restored_session, restored_log = import_project_bundle(bundle)
    _, _, restored_project_id, migration_required = import_project_bundle_details(bundle)

    assert restored_session.components == session.components
    assert restored_log.entries == log.entries
    assert restored_project_id == project_id
    assert migration_required is False