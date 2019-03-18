"""
@author: Haseung Lee
@date: 2019.02.27
"""

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth import get_user_model

User = get_user_model()
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
# from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from .serializers import UserSerializer
# my app models
from crowdfit_api.user.models import Country, City, Address, Apt, Household, Status, UserStatus, UserHousehold, Role, \
    UserRole, Permission, Feature, RoleFeaturePermission, Club, Login, UserExerInfo
# my app serializers
from crowdfit_api.user.serializers import CountrySerializers, CitySerializers, AddressSerializers, AptSerializers, \
    HouseholdSerializers, StatusSerializers, UserStatusSerializers, UserHouseholdSerializers, RoleSerializers, \
    UserRoleSerializers, PermissionSerializers, FeatureSerializers, RoleFeaturePermissionSerializers, ClubSerializers, \
    LoginSerializers, UserExerInfoSerializers


# Create your views here.

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-lastUpdate')
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


class AptViewSet(viewsets.ModelViewSet):
    queryset = Apt.objects.all().order_by('-id')
    serializer_class = AptSerializers


class HouseholdViewSet(viewsets.ModelViewSet):
    queryset = Household.objects.all().order_by('-id')
    serializer_class = HouseholdSerializers


class StatusViewSet(viewsets.ModelViewSet):
    queryset = Status.objects.all().order_by('-id')
    serializer_class = StatusSerializers


class UserStatusViewSet(viewsets.ModelViewSet):
    queryset = UserStatus.objects.all().order_by('-id')
    serializer_class = UserStatusSerializers


class UserHouseholdViewSet(viewsets.ModelViewSet):
    queryset = UserHousehold.objects.all().order_by('-id')
    serializer_class = UserHouseholdSerializers


class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all().order_by('-id')
    serializer_class = RoleSerializers


class UserRoleViewSet(viewsets.ModelViewSet):
    queryset = UserRole.objects.all().order_by('-id')
    serializer_class = UserRoleSerializers


class PermissionViewSet(viewsets.ModelViewSet):
    queryset = Permission.objects.all().order_by('-id')
    serializer_class = PermissionSerializers


class FeatureViewSet(viewsets.ModelViewSet):
    queryset = Feature.objects.all().order_by('-id')
    serializer_class = FeatureSerializers


class RoleFeaturePermissionViewSet(viewsets.ModelViewSet):
    queryset = RoleFeaturePermission.objects.all().order_by('-id')
    serializer_class = RoleFeaturePermissionSerializers


class ClubViewSet(viewsets.ModelViewSet):
    queryset = Club.objects.all().order_by('-id')
    serializer_class = ClubSerializers


class LoginViewSet(viewsets.ModelViewSet):
    queryset = Login.objects.all().order_by('-id')
    serializer_class = LoginSerializers


class UserExerInfoViewSet(viewsets.ModelViewSet):
    queryset = UserExerInfo.objects.all().order_by('-id')
    serializer_class = UserExerInfoSerializers
