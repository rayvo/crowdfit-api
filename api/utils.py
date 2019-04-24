from django.utils import timezone

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


def get_all_user_role_id_in_dep_idx(user, dep_idx_id):
    if not user:
        return []
    list_user_role_id = []
    # 1. from table user-role-status, get all active role
    list_active_user_role = UserRoleStatus.objects.filter(user_id=user.id, is_active=True,
                                                          department_role__department__department_index=dep_idx_id)
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
    return user_role_status.department_role.department.department_index_id == department_index_id \
           and user_role_status.department_role.role_id == role_id


def is_gateway(ble_post_data):
    return ble_post_data.type.casefold() == 'gateway'.casefold()


# https://stackoverflow.com/questions/6407362/how-can-i-check-if-a-date-is-the-same-day-as-datetime-today
def is_same_day(datetime1, datetime2):
    return datetime1.date() == datetime2.date()


def diff_in_second(source_datetime, dest_datetime):
    return (source_datetime - dest_datetime).total_seconds()


def diff_in_day(source_datetime, dest_datetime):
    return (source_datetime - dest_datetime).days


def is_today(src_datetime):
    return diff_in_day(timezone.now(), src_datetime) == 0
