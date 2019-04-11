from rest_framework.permissions import BasePermission
from django.conf import settings

from api import utils

"""
permission priority: resident < staff < ceo < superuser
"""


# https://www.django-rest-framework.org/api-guide/permissions/#custom-permissions
class IsCrowdfitAuthenticated(BasePermission):
    """
    Allows access only to authenticated users.
    """
    message = {'res_msg': 'User is not authenticated', 'res_code': 0}

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)


class IsCrowdfitCEOUser(BasePermission):
    """
    Allows access only to ceo users, or superuser
    """
    message = {'res_msg': 'Request User is not ceo', 'res_code': 0}

    def has_permission(self, request, view):
        # superuser also mean ceo user
        if utils.is_superuser(request.user):
            return True
        if request.user:
            all_roles = utils.get_all_user_role_id(request.user)
            return settings.CROWDFIT_API_ROLE_NAME_CEO_ID in all_roles
        return False


class IsCrowdfitSuperUser(BasePermission):
    """
    Allows access only to super users.
    """
    message = {'res_msg': 'Request User is not superuser', 'res_code': 0}

    def has_permission(self, request, view):
        res = utils.is_superuser(request.user)
        if not res:
            self.message['user_id'] = request.user.id
        return res
