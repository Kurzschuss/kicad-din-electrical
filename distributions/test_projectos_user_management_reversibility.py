import pytest

from .projectos_user_management_reversibility import ProjectOSUserManagementReversibilityPolicy


def test_reversibility_matrix_is_fail_closed_and_only_weight_change_is_reversible():
    policy = ProjectOSUserManagementReversibilityPolicy()
    state = policy.state()

    assert state["reversible_operations"] == ["user_weight_changed"]
    assert state["fail_closed"] is True
    assert state["persisted"] is False
    assert policy.require(
        "user_weight_changed",
        compensation="restore_previous_weight",
    ).reversible is True

    for operation in (
        "user_created",
        "permission_assigned",
        "permission_revoked",
        "project_role_assigned",
        "project_role_activated",
        "project_role_deactivated",
        "approval_requested",
        "approval_recorded",
        "post_review_completed",
    ):
        assert policy.is_reversible(operation) is False
        with pytest.raises(ValueError, match="operation is not reversible"):
            policy.require(operation)

    with pytest.raises(ValueError, match="reversibility policy not configured"):
        policy.is_reversible("unknown_operation")
