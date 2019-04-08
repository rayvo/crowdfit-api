from crowdfit_api.user.models import UserRoleStatus


def is_staff_user(user):
    if not user:
        return False
    return True


def get_all_user_role(user):
    if not user:
        return []
    list_user_role = []
    # 1. from table user-role-status, get all active role
    list_active_user_role = UserRoleStatus.objects.filter(user_id=user.id, is_active=True)
    for active_user_role in list_active_user_role:
        active_role = active_user_role.department_role.role
        list_user_role.append(active_role)
    return list_user_role
