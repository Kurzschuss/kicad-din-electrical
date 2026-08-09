import json
from uuid import uuid4

from .din_editor_project_bundle import export_project_bundle
from .din_editor_project_manager import DinEditorProjectManager
from .din_editor_session import DinEditorSession
from .din_editor_sync_log import DinSyncLog
from .z_cockpit_attention import ZCockpitAttentionView
from .z_cockpit_navigation import ZCockpitNavigationTarget
from .z_cockpit_navigation_resolver import ZCockpitNavigationResolver
from .z_cockpit_project_lead_overview import ZCockpitProjectLeadOverview


def _load_v3_manager(tmp_path) -> DinEditorProjectManager:
    project_id = str(uuid4())
    payload = export_project_bundle(DinEditorSession(), DinSyncLog(), project_id=project_id)
    path = tmp_path / "legacy-v3.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    manager = DinEditorProjectManager()
    manager.load(path)
    return manager


def _load_v4_user_management_v1_manager(tmp_path) -> DinEditorProjectManager:
    path = tmp_path / "legacy-user-management-v1.json"
    manager = DinEditorProjectManager()
    manager.save(path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["user_management"]["version"] = 1
    payload["user_management"].pop("permission_revocations")
    path.write_text(json.dumps(payload), encoding="utf-8")
    loaded = DinEditorProjectManager()
    loaded.load(path)
    return loaded


def test_project_lead_overview_exposes_bundle_migration_status(tmp_path):
    manager = _load_v3_manager(tmp_path)
    state = ZCockpitProjectLeadOverview(manager).state()

    assert state["persistence"]["persisted_bundle_version"] == 3
    assert state["persistence"]["migration_pending"] is True
    assert state["summary"]["bundle_migration_pending"] is True
    assert state["traffic_light"] == "yellow"
    assert any("Migration" in reason for reason in state["attention_reasons"])


def test_attention_creates_navigable_migration_item(tmp_path):
    manager = _load_v3_manager(tmp_path)
    overview = ZCockpitProjectLeadOverview(manager)
    state = ZCockpitAttentionView(overview).state()

    item = next(
        item for item in state["items"]
        if item["code"] == "USER_MANAGEMENT_BUNDLE_MIGRATION_PENDING"
    )
    assert item["traffic_light"] == "yellow"
    assert item["source"] == "persistence"
    assert item["affected"]["persisted_bundle_version"] == 3
    assert item["affected"]["migration_target_version"] == 4
    assert item["detail_target"]["view"] == "user_management_persistence"

    target = ZCockpitNavigationTarget(**{
        "view": item["detail_target"]["view"],
        "project_id": item["detail_target"]["project_id"],
        "correlation_id": item["detail_target"]["correlation_id"],
        "knowledge_ids": tuple(item["detail_target"]["knowledge_ids"]),
        "relation_ids": tuple(item["detail_target"]["relation_ids"]),
        "message_ids": tuple(item["detail_target"]["message_ids"]),
        "audit_filter": item["detail_target"]["audit_filter"],
        "recovery_path": item["detail_target"]["recovery_path"],
        "metadata": item["detail_target"]["metadata"],
    })
    resolved = ZCockpitNavigationResolver(manager).resolve(target)
    assert resolved["resolved_view"] == "user_management_persistence"
    assert resolved["payload"]["migration_pending"] is True
    assert resolved["payload"]["persisted_bundle_version"] == 3


def test_user_management_v1_gets_distinct_navigable_migration_attention(tmp_path):
    manager = _load_v4_user_management_v1_manager(tmp_path)
    overview = ZCockpitProjectLeadOverview(manager).state()
    attention = ZCockpitAttentionView(ZCockpitProjectLeadOverview(manager)).state()

    assert overview["persistence"]["persisted_bundle_version"] == 4
    assert overview["summary"]["bundle_migration_pending"] is False
    assert overview["summary"]["user_management_migration_pending"] is True
    assert any("Benutzerverwaltungsdaten" in reason for reason in overview["attention_reasons"])
    assert not any(
        item["code"] == "USER_MANAGEMENT_BUNDLE_MIGRATION_PENDING"
        for item in attention["items"]
    )

    item = next(
        item for item in attention["items"]
        if item["code"] == "USER_MANAGEMENT_PERSISTENCE_MIGRATION_PENDING"
    )
    assert item["traffic_light"] == "yellow"
    assert item["affected"]["persisted_user_management_version"] == 1
    assert item["affected"]["user_management_migration_target_version"] == 2
    assert item["detail_target"]["view"] == "user_management_persistence"

    target = ZCockpitNavigationTarget(**{
        "view": item["detail_target"]["view"],
        "project_id": item["detail_target"]["project_id"],
        "correlation_id": item["detail_target"]["correlation_id"],
        "knowledge_ids": tuple(item["detail_target"]["knowledge_ids"]),
        "relation_ids": tuple(item["detail_target"]["relation_ids"]),
        "message_ids": tuple(item["detail_target"]["message_ids"]),
        "audit_filter": item["detail_target"]["audit_filter"],
        "recovery_path": item["detail_target"]["recovery_path"],
        "metadata": item["detail_target"]["metadata"],
    })
    resolved = ZCockpitNavigationResolver(manager).resolve(target)
    assert resolved["resolved_view"] == "user_management_persistence"
    assert resolved["payload"]["persisted_user_management_version"] == 1
    assert resolved["payload"]["user_management_migration_target_version"] == 2


def test_saved_v4_has_no_migration_attention(tmp_path):
    manager = DinEditorProjectManager()
    manager.save(tmp_path / "project-v4.json")

    overview = ZCockpitProjectLeadOverview(manager).state()
    attention = ZCockpitAttentionView(ZCockpitProjectLeadOverview(manager)).state()

    assert overview["persistence"]["bundle_v4_persisted"] is True
    assert overview["persistence"]["migration_pending"] is False
    assert not any(
        item["code"] in {
            "USER_MANAGEMENT_BUNDLE_MIGRATION_PENDING",
            "USER_MANAGEMENT_PERSISTENCE_MIGRATION_PENDING",
        }
        for item in attention["items"]
    )
