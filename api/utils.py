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


def get_all_user_role_id(user):
    if not user:
        return []
    list_user_role_id = []
    # 1. from table user-role-status, get all active role
    list_active_user_role = UserRoleStatus.objects.filter(user_id=user.id, is_active=True)
    for active_user_role in list_active_user_role:
        active_role = active_user_role.department_role.role
        list_user_role_id.append(active_role.id)
    return list_user_role_id


def get_all_user_role_name(user):
    if not user:
        return []
    list_user_role_name = []
    # 1. from table user-role-status, get all active role
    list_active_user_role = UserRoleStatus.objects.filter(user_id=user.id, is_active=True)
    for active_user_role in list_active_user_role:
        active_role = active_user_role.department_role.role
        list_user_role_name.append(active_role.role)
    return list_user_role_name


def get_apartment(user):
    if not user:
        return None
    list_active_user_role = UserRoleStatus.objects.filter(user_id=user.id)
    for active_user_role in list_active_user_role:
        return active_user_role.department_role.department.apartment
    return None


def get_department_name(department):
    if not department:
        return ''
    if department.name:
        return department.name
    return department.department_index.name


def is_superuser(user):
    return bool(user and user.is_superuser)


def is_valid_user_role_status(user_role_status, department_index_id, role_id):
    """
    department = department_index_id
    role = role_id
    """
    return user_role_status.department_role.department_id == department_index_id \
           and user_role_status.department_role.role_id == role_id
