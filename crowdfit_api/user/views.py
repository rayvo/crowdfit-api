"""
@author: Haseung Lee
@date: 2019.02.27
"""

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth import get_user_model

User = get_user_model()
from rest_framework import viewsets
# my app models
from crowdfit_api.user.models import Country, City, Address, Apartment, Household, ImageFile, UserAvatar, Status, DocumentFile, UserStatus, UserHousehold, Department, Role, \
   DepartmentRole, UserRole, Permission, AppFeature, RoleFeaturePermission, Login, UserBodyInfo, Club
    
# my app serializers
from crowdfit_api.user.serializers import UserSerializer, CountrySerializers, CitySerializers, AddressSerializers, \
    ApartmentSerializers, HouseholdSerializers, ImageFileSerializers, UserAvatarSerializers, StatusSerializers, DocumentFileSerializers, UserStatusSerializers, UserHouseholdSerializers, \
    DepartmentSerializers, RoleSerializers, DepartmentRoleSerializers, UserRoleSerializers, PermissionSerializers, AppFeatureSerializers, RoleFeaturePermissionSerializers, \
    LoginSerializers, UserBodyInfoSerializers, ClubSerializers
    


# Create your views here.

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-last_update')
    serializer_class = UserSerializer

    # authentication_classes = (TokenAuthentication,)
    # permission_classes = (IsAuthenticated,)


class CountryViewSet(viewsets.ModelViewSet):
    queryset = Country.objects.all().order_by('-country')
    serializer_class = CountrySerializers

    # def list(self, request, *args, **kwargs):
    #     family = Family.objects.all()
    #     serializer = FamilyMiniSerializer(family, many=True)
    #     return Response(serializer.data)


class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all().order_by('-city')
    serializer_class = CitySerializers


class AddressViewSet(viewsets.ModelViewSet):
    queryset = Address.objects.all().order_by('-id')
    serializer_class = AddressSerializers


class ApartmentViewSet(viewsets.ModelViewSet):
    queryset = Apartment.objects.all().order_by('-id')
    serializer_class = ApartmentSerializers


class HouseholdViewSet(viewsets.ModelViewSet):
    queryset = Household.objects.all().order_by('-id')
    serializer_class = HouseholdSerializers

class ImageFileViewSet(viewsets.ModelViewSet):
    queryset = ImageFile.objects.all().order_by('-id')
    serializer_class = ImageFileSerializers

class UserAvatarViewSet(viewsets.ModelViewSet):
    queryset = UserAvatar.objects.all().order_by('-id')
    serializer_class = UserAvatarSerializers
    
class StatusViewSet(viewsets.ModelViewSet):
    queryset = Status.objects.all().order_by('-id')
    serializer_class = StatusSerializers

class DocumentFileViewSet(viewsets.ModelViewSet):
    queryset = DocumentFile.objects.all().order_by('-id')
    serializer_class = DocumentFileSerializers

class UserStatusViewSet(viewsets.ModelViewSet):
    queryset = UserStatus.objects.all().order_by('-id')
    serializer_class = UserStatusSerializers


class UserHouseholdViewSet(viewsets.ModelViewSet):
    queryset = UserHousehold.objects.all().order_by('-id')
    serializer_class = UserHouseholdSerializers

class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all().order_by('-id')
    serializer_class = DepartmentSerializers


class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all().order_by('-id')
    serializer_class = RoleSerializers


class DepartmentRoleViewSet(viewsets.ModelViewSet):
    queryset = DepartmentRole.objects.all().order_by('-id')
    serializer_class = DepartmentRoleSerializers

class UserRoleViewSet(viewsets.ModelViewSet):
    queryset = UserRole.objects.all().order_by('-id')
    serializer_class = UserRoleSerializers


class PermissionViewSet(viewsets.ModelViewSet):
    queryset = Permission.objects.all().order_by('-id')
    serializer_class = PermissionSerializers


class AppFeatureViewSet(viewsets.ModelViewSet):
    queryset = AppFeature.objects.all().order_by('-id')
    serializer_class = AppFeatureSerializers


class RoleFeaturePermissionViewSet(viewsets.ModelViewSet):
    queryset = RoleFeaturePermission.objects.all().order_by('-id')
    serializer_class = RoleFeaturePermissionSerializers

class LoginViewSet(viewsets.ModelViewSet):
    queryset = Login.objects.all().order_by('-id')
    serializer_class = LoginSerializers


class UserBodyInfoViewSet(viewsets.ModelViewSet):
    queryset = UserBodyInfo.objects.all().order_by('-id')
    serializer_class = UserBodyInfoSerializers

class ClubViewSet(viewsets.ModelViewSet):
    queryset = Club.objects.all().order_by('-id')
    serializer_class = ClubSerializers






