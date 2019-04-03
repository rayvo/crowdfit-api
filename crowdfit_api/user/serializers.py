""""
@author: moon
@date: 2019.02.27
"""

from django.contrib.auth import get_user_model

# for custom user
User = get_user_model()

from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from crowdfit_api.user.models import Country, City, Apartment, Household, ImageFile, UserAvatar, Status, DocumentFile, UserHousehold, Department, Role, \
   DepartmentRole, UserRoleStatus, Permission, AppFeature, RoleFeaturePermission, Login, UserBodyInfo, Club
  

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
#     blood_type CHAR(3),
#     create_date DATETIME,
#     last_update DATETIME
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
            'id', 'username', 'email', 'password', 'nickname', 'fullname', 'birthday', 'gender', 'phone', "blood_type")
        extra_kwargs = {'password': {'write_only': True, 'required': True}}


# City (
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     city VARCHAR(50),
#     country_id INT, → COUNTRY ID
#     create_date DATETIME,
#     last_update DATETIME
# )
class CitySerializers(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ('id', 'city', 'country', 'create_date', 'last_update')
        extra_kwargs = {'last_update': {'read_only': True}}


# Country (
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     country VARCHAR(50) NOT NULL,
#     create_date DATETIME,
#     last_update DATETIME
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
        fields = ('id', 'country', 'create_date', 'last_update', 'cities')


# Apartment(
# 	id INT AUTO_INCREMENT PRIMARY KEY,
# 	name VARCHAR(125) NOT NULL UNIQUE, 
# 	address_id INT,  ADDRESS ID
# 	description VARCHAR(500),
# 	is_active BOOLEAN,
# 	create_date DATETIME,
# 	last_update DATETIME
# );
class ApartmentSerializers(serializers.ModelSerializer):
    cities = CitySerializers(many=True, read_only=True)

    class Meta:
        model = Apartment
        fields = ('id', 'name', 'address_gu', 'address_dong', 'address_road', 'address_detail', 'postcode', 'phone', 'latitude', 'longtitude',  'city', 'cities', 'description','is_active', 'create_date', 'last_update')
        extra_kwargs = {'last_update': {'read_only': True},
                        'create_date': {'read_only': True}}


# Household(
# 	id,
# 	apartment_id,  APT ID
# 	address_dong VARCHAR(10),
# 	house_number VARCHAR(10),
# 	is_empty BOOLEAN
# 	create_date DATETIME,	
# 	last_update DATETIME
# );
class HouseholdSerializers(serializers.ModelSerializer):
    apartments = ApartmentSerializers(many=True, read_only=True)

    class Meta:
        model = Household
        fields = ('id', 'address_dong', 'house_number', 'is_empty', 'apartment', 'apartments', 'create_date', 'last_update')
        extra_kwargs = {'last_update': {'read_only': True},
                        'create_date': {'read_only': True}}



# ImageFile (
# 	id INT AUTO_INCREMENT PRIMARY KEY,
# 	file_name VARCHAR(250) NOTNULL,
#     file_url VARCHAR(1024) NOT NULL,
#     file_type VARCHAR(25),
#     file_size INT,
#     create_date DATETIME, 
# 	last_update DATETIME
# );
class ImageFileSerializers(serializers.ModelSerializer):
    class Meta:
        model = ImageFile
        fields = ('id', 'file_name', 'file_url', 'file_type', 'file_size', 'create_date', 'last_update')
        extra_kwargs = {'last_update': {'read_only': True},
                        'create_date': {'read_only': True}}


# UserAvatar (
# 	id INT AUTO_INCREMENT PRIMARY KEY,
# 	user_id INT,  USER ID
# 	image_file_id,  IMAGEFILE ID
#   is_active BOOLEAN,
# 	create_date DATETIME,
# 	last_update DATETIME
# )
class UserAvatarSerializers(serializers.ModelSerializer):
    user_ua_list = UserSerializer(many=True, read_only=True)
    image_file_list = ImageFileSerializers(many=True, read_only=True)
    class Meta:
        model = UserAvatar
        fields = (
            'id', 'user', 'url',
            'user_ua_list', 'image_file_list', 'is_active',
            'create_date', 'last_update')
        extra_kwargs = {'last_update': {'read_only': True},
                        'create_date': {'read_only': True}}

# Status( //Applying, Waiting, approval, eviction
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     name VARCHAR(50) NOT NULL,
#     description VARCHAR(256),
#     create_date DATETIME,
#     last_update DATETIME
# )


class StatusSerializers(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = ('id', 'name', 'description', 'create_date', 'last_update')
        extra_kwargs = {'last_update': {'read_only': True},
                        'create_date': {'read_only': True}}

# DocumentFile (
# 	id INT AUTO_INCREMENT PRIMARY KEY,
# 	file_name VARCHAR(250),
#     file_url VARCHAR(1024) NOT NULL,
#     file_type VARCHAR(25),
#     file_size INT,
#     is_active BOOLEAN
#     create_date DATETIME,
#     last_update DATETIME
# )
class DocumentFileSerializers(serializers.ModelSerializer):
    class Meta:
        model = DocumentFile
        fields = ('id', 'file_name', 'file_url', 'file_type', 'file_size', 'is_active','create_date', 'last_update')
        extra_kwargs = {'last_update': {'read_only': True},
                        'create_date': {'read_only': True}}

# UserStatus (
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     user_id INT, → USER ID
#     status_id INT, → STATUS ID
#     staff_id INT, → USER ID (can be admin)
#     document_file_id INT, --> DOCUMENTFILE, //등본
#     create_date DATETIME,
#     last_update DATETIME
# )
# class UserStatusSerializers(serializers.ModelSerializer):
#     users = UserSerializer(many=True, read_only=True)
#     staffs = UserSerializer(many=True, read_only=True)
#     status_list = StatusSerializers(many=True, read_only=True)
#     document_files = DocumentFileSerializers(many=True, read_only=True)
#     class Meta:
#         model = UserStatus
#         fields = (
#             'id', 'status', 'document_file', 'user', 'staff', 'users', 'staffs', 'status_list', 'document_files', 'create_date', 'last_update')
#         extra_kwargs = {'last_update': {'read_only': True},
#                         'create_date': {'read_only': True}}


# UserHousehold (
# 	id INT AUTO_INCREMENT PRIMARY KEY,
# 	user_id INT,  USER ID
# 	household_id INT,  HOUSEHOLD ID
# 	is_owner BOOLEAN,
# 	is_active BOOLEAN,
#   create_date DATETIME,
#   last_update DATETIME
# )
class UserHouseholdSerializers(serializers.ModelSerializer):
    user_list = UserSerializer(many=True, read_only=True)
    households = HouseholdSerializers(many=True, read_only=True)

    class Meta:
        model = UserHousehold
        fields = ('id', 'user', 'household', 'is_owner', 'user_list', 'households', 'is_active', 'create_date', 'last_update')
        extra_kwargs = {'last_update': {'read_only': True},
                        'create_date': {'read_only': True}}

# Department ( //Community,HR, Financial, Accouting, Admistration, IT, Sales, Training
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     name VARCHAR(125) NOT NULL,
#     apartment_id INT, →  APT ID
#     description VARCHAR(500),
#     create_date DATETIME,
#     last_update DATETIME
# );
class DepartmentSerializers(serializers.ModelSerializer):
    apartment_dep_list = ApartmentSerializers(many=True, read_only=True)

    class Meta:
        model = Department
        fields = (
            'id', 'name',
            'apartment', 'apartment_dep_list', 'description', 
                   'create_date', 'last_update')
        extra_kwargs = {'last_update': {'read_only': True},
                        'create_date': {'read_only': True}}


# Role ( //비회원, 직원, 입주민, 관리자 Non-member, residents, lecturer, representative, IT dev, manager, ...
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     role VARCHAR(30) NOT NULL,
#     description TEXT,
#     is_active BOOLEAN,
#     create_date DATETIME,
#     last_update DATETIME
# );
class RoleSerializers(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ('id', 'role', 'description', 'is_active',
                  'create_date', 'last_update')
        extra_kwargs = {'last_update': {'read_only': True},
                        'create_date': {'read_only': True}}


# DepartmentRole ( //each department has different roles for members
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     department_id INT NOT NULL,	→ DEPARTMENT ID
#     role_id INT NOT NULL, → ROLE
#     is_active BOOLEAN,
#     create_date DATETIME,
#     last_update DATETIME
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
            'is_active',
            'create_date', 'last_update')
        extra_kwargs = {'last_update': {'read_only': True},
                        'create_date': {'read_only': True}}

# UserRole ( //assign role to each member in one department
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     user_id INT,	→ USER ID
#     department_role_id INT NOT NULL, → DEPARTMENT ROLE
#     is_active BOOLEAN,
#     create_date DATETIME,
#     last_update DATETIME
# )
class UserRoleStatusSerializers(serializers.ModelSerializer):
    user_userrole_list = UserSerializer(many=True, read_only=True)
    deprole_userrole_list = DepartmentRoleSerializers(many=True, read_only=True)
    staffs = UserSerializer(many=True, read_only=True)
    status_list = StatusSerializers(many=True, read_only=True)
    document_files = DocumentFileSerializers(many=True, read_only=True)
    class Meta:
        model = UserRoleStatus
        fields = (
            'id', 'user', 'user_userrole_list',
            'department_role', 'deprole_userrole_list', 'status', 'document_file', 'staff', 'staffs',  'status_list', 'document_files',
            'is_active',
            'create_date', 'last_update')
        extra_kwargs = {'last_update': {'read_only': True},
                        'create_date': {'read_only': True}}

# Permission ( // View list, Read permission, Write permission, Write comment, Force delete, Hide post
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     name VARCHAR(100) NOT NULL UNIQUE,
#     description VARCHAR(255),
#     create_date DATETIME,
#     last_update DATETIME
# )
class PermissionSerializers(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ('id', 'name', 'description', 'create_date', 'last_update')
        extra_kwargs = {'last_update': {'read_only': True},
                        'create_date': {'read_only': True}}


# AppFeature (
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     name VARCHAR(100) NOT NULL UNIQUE,
#     description VARCHAR(255),
#     is_active BOOLEAN
#     create_date DATETIME,
#     last_update DATETIME
# )
class AppFeatureSerializers(serializers.ModelSerializer):
    class Meta:
        model = AppFeature
        fields = ('id', 'name', 'description', 'is_active', 'create_date', 'last_update')
        extra_kwargs = {'last_update': {'read_only': True},
                        'create_date': {'read_only': True}}

# RoleFeaturePermission (
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     department_role_id INT NOT NULL, → DepartmentRole ID
#     app_feature_id INT NOT NULL, → FEATURE ID
#     permission_id INT NOT NULL, → PERMISSION ID
#     is_active BOOLEAN,
#     create_date DATETIME,
#     last_update DATETIME
# )
class RoleFeaturePermissionSerializers(serializers.ModelSerializer):
    deprole_rfp_list = DepartmentRoleSerializers(many=True, read_only=True)
    app_feature_rfp_list = RoleSerializers(many=True, read_only=True)
    permission_rfp_list = RoleSerializers(many=True, read_only=True)

    class Meta:
        model = RoleFeaturePermission
        fields = (
            'id', 'department_role', 'deprole_rfp_list',
            'app_feature', 'app_feature_rfp_list',
            'permission', 'permission_rfp_list',
            'is_active',
            'create_date', 'last_update')
        extra_kwargs = {'last_update': {'read_only': True},
                        'create_date': {'read_only': True}}
                        
# Login (
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     user_id INT,
#     login_time DATETIME,
#     logout_time DATETIME,
#     last_app_feature_id INT, → FEATURE ID,
#     is_last BOOLEAN
# )
class LoginSerializers(serializers.ModelSerializer):
    user_login_list = UserSerializer(many=True, read_only=True)
    app_feature_login_list = AppFeatureSerializers(many=True, read_only=True)

    class Meta:
        model = Login
        fields = (
            'id', 'user', 'login_time', 'logout_time', 'last_app_feature', 'is_last',
            'user_login_list', 'app_feature_login_list')
        extra_kwargs = {'login_time': {'read_only': True}}


# UserBodyInfo (
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     user_id —> User ID
#     height INT,
#     weight INT,
#     waist INT,
#     create_date DATETIME,
#     last_update DATETIME
# )
class UserBodyInfoSerializers(serializers.ModelSerializer):
    user_uei_list = UserSerializer(many=True, read_only=True)

    class Meta:
        model = UserBodyInfo
        fields = (
            'id', 'user', 'height', 'weight', 'waist',
            'user_uei_list',
            'create_date', 'last_update')
        extra_kwargs = {'last_update': {'read_only': True},
                        'create_date': {'read_only': True}}


# Club (
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     apartment_id INT —> APT id
#     name VARCHAR(125) NOT NULL UNIQUE,
#     address_id, → ADDRESS ID
#     phone VARCHAR(11),
#     club_register_number VARCHAR(10),
#     club_register_date DATETIME,
#     ot_number INT,
#     ot_period INT,
#     description TEXT,
#     create_date DATETIME,
#     last_update DATETIME
# );
class ClubSerializers(serializers.ModelSerializer):
    apartment_club_list = ApartmentSerializers(many=True, read_only=True)

    class Meta:
        model = Club
        fields = (
            'id', 'apartment', 'name', 'phone', 'club_register_number', 'club_register_date', 'ot_number', 'ot_period', 'description',
            'apartment_club_list', 'address_club_list',
            'create_date', 'last_update')
        extra_kwargs = {'last_update': {'read_only': True},
                        'create_date': {'read_only': True}}

















