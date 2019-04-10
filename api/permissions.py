from rest_framework.permissions import BasePermission
from django.conf import settings

from api import utils


class IsCrowdfitAuthenticated(BasePermission):
    """
    Allows access only to authenticated users.
    """
    message = {'res_msg': 'User is not authenticated', 'res_code': 0}

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)


class IsCrowdfitCEOUser(BasePermission):
    """
    Allows access only to ceo users.
    """
    message = {'res_msg': 'User is not superuser', 'res_code': 0}

    def has_permission(self, request, view):
        if request.user:
            all_roles = utils.get_all_user_role_id(request.user)
            return settings.CROWDFIT_API_ROLE_NAME_CEO_ID in all_roles
        return False
