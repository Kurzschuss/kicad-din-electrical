from pathlib import Path
from uuid import uuid4

import pytest

from .din_editor_project_manager import DinEditorProjectManager
from .projectos_user_management_change_service import ProjectOSUserManagementChangeService
from .projectos_user_management_command_context import ProjectOSUserManagementCommandContext
from .projectos_user_management_command_policy import (
    DEFAULT_COMMAND_PERMISSION_MAP,
    ProjectOSUserManagementCommandPolicy,
)
from .projectos_user_management_runtime import build_projectos_user_management_runtime


def _context(actor_user_id: str) -> ProjectOSUserManagementCommandContext:
    return ProjectOSUserManagementCommandContext(
        actor_user_id=actor_user_id,
        correlation_id=str(uuid4()),
    )


def test_default_policy_is_central_read_only_and_does_not_grant_implicit_role_rights():
    policy = ProjectOSUserManagementCommandPolicy.default()

    assert policy.command_permission_map["user_weight_changed"] == "project.user_management.weight.change"
    assert policy.command_permission_map["undo:user_weight_changed"] == "project.user_management.weight.undo"
    assert policy.command_permission_map["redo:user_weight_changed"] == "project.user_management.weight.redo"
    assert set(DEFAULT_COMMAND_PERMISSION_MAP) == set(policy.command_permission_map)
    assert dict(policy.role_permission_map) == {}
    assert dict(policy.role_risk_class_map) == {}
    assert policy.as_dict()["persisted"] is False

    with pytest.raises(TypeError):
        policy.command_permission_map["user_weight_changed"] = "override"


def test_productive_runtime_uses_authorized_change_service_and_default_policy():
    manager = DinEditorProjectManager()
    bootstrap = ProjectOSUserManagementChangeService(manager)
    administrator = bootstrap.create_user("Administrator")
    target = bootstrap.create_user("Ziel", weight=100)
    bootstrap.command_assign_permission(
        user_id=administrator.user_id,
        permission="project.user_management.weight.change",
        source_type="direct",
        effect="allow",
    )

    runtime = build_projectos_user_management_runtime(manager)
    runtime.changes.change_user_weight(
        target.user_id,
        350,
        command_context=_context(administrator.user_id),
    )

    current = next(user for user in manager.user_management.users if user.user_id == target.user_id)
    assert current.weight == 350
    assert runtime.state()["last_authorization"]["decision"] == "allow"
    assert runtime.state()["command_history"]["count"] == 1
    assert runtime.state()["trace_count"] == 1
    assert runtime.state()["persisted"] is False


def test_productive_modules_do_not_instantiate_raw_user_management_change_service():
    base = Path(__file__).resolve().parent
    violations = []
    for path in base.glob("*.py"):
        if path.name.startswith("test_") or path.name == "projectos_user_management_change_service.py":
            continue
        text = path.read_text(encoding="utf-8")
        if "ProjectOSUserManagementChangeService(" in text:
            violations.append(path.name)

    assert violations == [], (
        "Produktive Benutzerverwaltungs-Commands müssen über "
        "build_projectos_user_management_runtime()/ProjectOSAuthorizedUserManagementChangeService laufen: "
        + ", ".join(sorted(violations))
    )
