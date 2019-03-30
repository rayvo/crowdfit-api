""""
@author: moon
@date: 2019.02.27
"""

from django.contrib.auth import get_user_model

# for custom user
User = get_user_model()

from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from crowdfit_api.user.models import Country, City, Address, Apt, Household, Status, UserStatus, UserHousehold, Role, \
    UserRole, Permission, Feature, RoleFeaturePermission, Club, Login, UserExerInfo, Department, DepartmentRole


# TODO: make sure the full info serializer actually has all of the information


# User(
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     name VARCHAR(50) NOT NULL,
#     email VARCHAR(50) NOT NULL UNIQUE,
#     nickname VARCHAR(50) NOT NULL UNIQUE,
#     password VARCHAR(256) NOT NULL,
#     birthday DATE NOT NULL,
#     phone VARCHAR(15),
#     gender CHAR(1) NOT NULL,
#     bloodType CHAR(3),
#     createDate DATETIME,
#     lastUpdate DATETIME
# );
# class UserSerializer(serializers.HyperlinkedModelSerializer):
class UserSerializer(serializers.ModelSerializer):
    # validate_password = make_password  # for hashing password
    # Your validate_<field_name> methods should return the validated value or raise a serializers.ValidationError
    def validate_password(self, value):
        """
        return the validated password
        """
        value = make_password(value)
        return value

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'password', 'nickname', 'fullname', 'birthday', 'gender', 'phone', "bloodType")
        extra_kwargs = {'password': {'write_only': True, 'required': True}}


# City (
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     city VARCHAR(50),
#     countryID INT, → COUNTRY ID
#     lastUpdate DATETIME
# )
class CitySerializers(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ('id', 'city', 'country', 'lastUpdate')
        extra_kwargs = {'lastUpdate': {'read_only': True}}


# Country (
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     country VARCHAR(50),
#     lastUpdate DATETIME
# )
class CountrySerializers(serializers.ModelSerializer):
    # cities = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    # cities = serializers.SlugRelatedField(
    #     many=True,
    #     read_only=True,
    #     slug_field='city'
    # )
    cities = CitySerializers(many=True, read_only=True)

    class Meta:
        model = Country
        fields = ('id', 'country', 'cities')


# Address (
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     cityID VARCHAR(50) NOT NULL, → CITY ID
#     addGu VARCHAR(50) NOT NULL,
#     addDong VARCHAR(50) NOT NULL,
#     addDetail VARCHAR(100) NOT NULL,
#     postcode VARCHAR(10) NOT NULL,
#     phone VARCHAR(15),
#     lat DECIMAL(10,8) NOT NULL,
#     lng DECIMAL(11,8) NOT NULL,
#     lastUpdate DATETIME
# )
class AddressSerializers(serializers.ModelSerializer):
    cities = CitySerializers(many=True, read_only=True)

    class Meta:
        model = Address
        fields = ('id', 'addGu', 'addDong', 'addDetail', 'postcode', 'phone', 'lat', 'lng', 'city', 'cities')
        extra_kwargs = {'lastUpdate': {'read_only': True}}


# APT(
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     name VARCHAR(125) NOT NULL UNIQUE,
#     addressID INT, → ADDRESS ID
#     desc VARCHAR(500),
#     createDate DATETIME,
#     lastUpdate DATETIME
# );
class AptSerializers(serializers.ModelSerializer):
    addresses = AddressSerializers(many=True, read_only=True)

    class Meta:
        model = Apt
        fields = ('id', 'name', 'desc', 'address', 'addresses', 'createDate', 'lastUpdate')
        extra_kwargs = {'lastUpdate': {'read_only': True},
                        'createDate': {'read_only': True}}


# Household(
#     id,
#     aptID, → APT ID
#     addDong VARCHAR(10),
#     houseNum VARCHAR(10),
#     status INT, //0: occupied, 1: available
#     createDate DATETIME,
#     lastUpdate DATETIME
# );
class HouseholdSerializers(serializers.ModelSerializer):
    apts = AptSerializers(many=True, read_only=True)

    class Meta:
        model = Household
        fields = ('id', 'addDong', 'houseNum', 'status', 'apt', 'apts', 'createDate', 'lastUpdate')
        extra_kwargs = {'lastUpdate': {'read_only': True},
                        'createDate': {'read_only': True}}


# Status( //Waiting, approval, eviction
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     name VARCHAR(50) NOT NULL,
#     desc VARCHAR(256),

#     createDate DATETIME,
#     lastUpdate DATETIME
# )
class StatusSerializers(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = ('id', 'name', 'desc', 'createDate', 'lastUpdate')
        extra_kwargs = {'lastUpdate': {'read_only': True},
                        'createDate': {'read_only': True}}


# UserStatus (
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     userID INT, → USER ID
#     status INT, → STATUS ID
#     staffID INT, → USER ID (can be admin)
#     fileUrl VARCHAR(256), //등본
#     createDate DATETIME,
#     lastUpdate DATETIME
# )
class UserStatusSerializers(serializers.ModelSerializer):
    users = UserSerializer(many=True, read_only=True)
    staffs = UserSerializer(many=True, read_only=True)
    status_list = StatusSerializers(many=True, read_only=True)

    class Meta:
        model = UserStatus
        fields = (
            'id', 'status', 'fileUrl', 'user', 'staff', 'users', 'staffs', 'status_list', 'createDate', 'lastUpdate')
        extra_kwargs = {'lastUpdate': {'read_only': True},
                        'createDate': {'read_only': True}}


# UserHouseHold (
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     userID INT, → USER ID
#     householdID INT, → HOUSEHOLD ID
#     isOwner BOOLEAN,
#     createDate DATETIME,
#     lastUpdate DATETIME
# )
class UserHouseholdSerializers(serializers.ModelSerializer):
    user_list = UserSerializer(many=True, read_only=True)
    households = HouseholdSerializers(many=True, read_only=True)

    class Meta:
        model = UserHousehold
        fields = ('id', 'user', 'household', 'isOwner', 'user_list', 'households', 'createDate', 'lastUpdate')
        extra_kwargs = {'lastUpdate': {'read_only': True},
                        'createDate': {'read_only': True}}


# Role ( // Non-member, Employee, Residents, Manager
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     role VARCHAR(30) NOT NULL,
#     desc TEXT,
#     createDate DATETIME,
#     lastUpdate DATETIME
# );
class RoleSerializers(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ('id', 'role', 'desc',
                  'createDate', 'lastUpdate')
        extra_kwargs = {'lastUpdate': {'read_only': True},
                        'createDate': {'read_only': True}}


# Permission ( // View list, Read permission, Write permission, Write comment, Force delete, Hide post
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     name VARCHAR(100) NOT NULL UNIQUE,
#     desc VARCHAR(255),
#     createDate DATETIME
# )
class PermissionSerializers(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ('id', 'name', 'desc', 'createDate', 'lastUpdate')
        extra_kwargs = {'lastUpdate': {'read_only': True},
                        'createDate': {'read_only': True}}


# Feature (
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     name VARCHAR(100) NOT NULL UNIQUE,
#     desc VARCHAR(255),
#     createDate DATETIME,
#     lastUpdate DATETIME
# )
class FeatureSerializers(serializers.ModelSerializer):
    class Meta:
        model = Feature
        fields = ('id', 'name', 'desc', 'createDate', 'lastUpdate')
        extra_kwargs = {'lastUpdate': {'read_only': True},
                        'createDate': {'read_only': True}}


# Club (
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     aptID INT —> APT id
#     name VARCHAR(125) NOT NULL UNIQUE,
#     addressID, → ADDRESS ID
#     phone VARCHAR(11),
#     clubRegNum VARCHAR(10),
#     clubRegDate DATETIME,
#     otNum INT,
#     otPeriod INT,
#     desc TEXT,
#     createDate DATETIME,
#     lastUpdate DATETIME
# );
class ClubSerializers(serializers.ModelSerializer):
    apt_club_list = AptSerializers(many=True, read_only=True)
    address_club_list = AddressSerializers(many=True, read_only=True)

    class Meta:
        model = Club
        fields = (
            'id', 'apt', 'name', 'address', 'phone', 'clubRegNum', 'clubRegDate', 'otNum', 'otPeriod', 'desc',
            'apt_club_list', 'address_club_list',
            'createDate', 'lastUpdate')
        extra_kwargs = {'lastUpdate': {'read_only': True},
                        'createDate': {'read_only': True}}


# Login (
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     userID INT,
#     loginTime DATETIME,
#     logoutTime DATETIME,
#     lastFeatureID INT, → FEATURE ID,
#     isLast BOOLEAN
# )
class LoginSerializers(serializers.ModelSerializer):
    user_login_list = UserSerializer(many=True, read_only=True)
    feature_login_list = FeatureSerializers(many=True, read_only=True)

    class Meta:
        model = Login
        fields = (
            'id', 'user', 'loginTime', 'logoutTime', 'lastFeature', 'isLast',
            'user_login_list', 'feature_login_list',
            'createDate', 'lastUpdate')
        extra_kwargs = {'lastUpdate': {'read_only': True},
                        'createDate': {'read_only': True}}


# UserExerInfo (
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     userID —> User ID
#     height INT,
#     weight INT,
#     createDate DATETIME,
#     lastUpdate DATETIME
# )
class UserExerInfoSerializers(serializers.ModelSerializer):
    user_uei_list = UserSerializer(many=True, read_only=True)

    class Meta:
        model = UserExerInfo
        fields = (
            'id', 'user', 'height', 'weight',
            'user_uei_list',
            'createDate', 'lastUpdate')
        extra_kwargs = {'lastUpdate': {'read_only': True},
                        'createDate': {'read_only': True}}


# UserAvatar (
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     userID INT, → USER ID
#     url VARCHAR(1024) NOT NULL,
# )
class UserAvatarSerializers(serializers.ModelSerializer):
    user_ua_list = UserSerializer(many=True, read_only=True)

    class Meta:
        model = UserExerInfo
        fields = (
            'id', 'user', 'url',
            'user_ua_list',
            'createDate', 'lastUpdate')
        extra_kwargs = {'lastUpdate': {'read_only': True},
                        'createDate': {'read_only': True}}


# Department ( //Community,HR, Financial, Accouting, Admistration, IT, Sales, Training
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     name VARCHAR(125) NOT NULL,
#     aptID INT, →  APT ID
#     desc VARCHAR(500),
#     createDate DATETIME,
#     lastUpdate DATETIME
# );
class DepartmentSerializers(serializers.ModelSerializer):
    apt_dep_list = AptSerializers(many=True, read_only=True)

    class Meta:
        model = Department
        fields = (
            'id', 'name',
            'apt', 'apt_dep_list'
                   'createDate', 'lastUpdate')
        extra_kwargs = {'lastUpdate': {'read_only': True},
                        'createDate': {'read_only': True}}


# DepartmentRole ( //each department has different roles for members
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     departmentID INT NOT NULL,	→ DEPARTMENT ID
#     roleID INT NOT NULL, → ROLE
#     isActive BOOLEAN,
#     createDate DATETIME,
#     lastUpdate DATETIME
# );
class DepartmentRoleSerializers(serializers.ModelSerializer):
    dep_deprole_list = DepartmentSerializers(many=True, read_only=True)
    role_deprole_list = RoleSerializers(many=True, read_only=True)

    class Meta:
        model = DepartmentRole
        fields = (
            'id',
            'department', 'dep_deprole_list',
            'role', 'role_deprole_list',
            'isActive',
            'createDate', 'lastUpdate')
        extra_kwargs = {'lastUpdate': {'read_only': True},
                        'createDate': {'read_only': True}}


# UserRole ( //assign role to each member in one department
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     userID INT,	→ USER ID
#     departmentRoleID INT NOT NULL, → DEPARTMENT ROLE
#     isActive BOOLEAN,
#     createDate DATETIME,
#     lastUpdate DATETIME
# )
class UserRoleSerializers(serializers.ModelSerializer):
    user_userrole_list = UserSerializer(many=True, read_only=True)
    deprole_userrole_list = DepartmentRoleSerializers(many=True, read_only=True)

    class Meta:
        model = UserRole
        fields = (
            'id', 'user', 'user_userrole_list',
            'departmentRole', 'deprole_userrole_list',
            'isActive',
            'createDate', 'lastUpdate')
        extra_kwargs = {'lastUpdate': {'read_only': True},
                        'createDate': {'read_only': True}}


# RoleFeaturePermission (
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     departmentRole INT NOT NULL, → DepartmentRole ID
#     featureID INT NOT NULL, → FEATURE ID
#     permissionID INT NOT NULL, → PERMISSION ID
#     isActive BOOLEAN,
#     createDate DATETIME,
#     lastUpdate DATETIME
# )
class RoleFeaturePermissionSerializers(serializers.ModelSerializer):
    deprole_rfp_list = DepartmentRoleSerializers(many=True, read_only=True)
    feature_rfp_list = RoleSerializers(many=True, read_only=True)
    permission_rfp_list = RoleSerializers(many=True, read_only=True)

    class Meta:
        model = RoleFeaturePermission
        fields = (
            'id', 'departmentRole', 'deprole_rfp_list',
            'feature', 'feature_rfp_list',
            'permission', 'permission_rfp_list',
            'isActive',
            'createDate', 'lastUpdate')
        extra_kwargs = {'lastUpdate': {'read_only': True},
                        'createDate': {'read_only': True}}
