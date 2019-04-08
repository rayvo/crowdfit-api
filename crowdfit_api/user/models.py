"""
@author: moon
@date: 2019.02.28
"""

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import validate_email


# My Models

# User( 
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     fullname VARCHAR(50) NOT NULL,
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
class CustomUser(AbstractUser):
    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']
    # USERNAME_FIELD = 'email'
    # ID is by default
    # id = models.AutoField(primary_key=True)
    email = models.EmailField(validators=[validate_email], verbose_name='email address', max_length=255, null=False,
                              unique=True, blank=False)
    fullname = models.CharField(max_length=150, null=True, blank=False)
    nickname = models.CharField(max_length=50, null=True, unique=True, blank=False)
    username = models.CharField(max_length=150, null=True, unique=True, blank=True)
    # password = models.CharField(max_length=256, null=False, blank=False) # auto generated field
    birthday = models.DateField(null=True, blank=False)

    # phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999 999 999'. Up to 15 digits allowed.")
    # phone_regex = RegexValidator(regex=r'^(\+82[- ]*10[- ]*[0-9]{4}[- ]*[0-9]{4}|010[- ]*[0-9]{4}[- ]*[0-9]{4})$',
    #                              message="Phone number must be entered in the format: '+82-10-xxxx-xxxx or 010-xxxx-xxxx")
    # # phone_number = models.CharField(validators=[phone_regex], max_length=17, default='+82', blank=True) # validators should be a list
    # phone = models.CharField(max_length=15, null=True, validators=[phone_regex])
    phone = models.CharField(max_length=15, null=True, validators=[settings.PHONE_REGEX])

    gender = models.PositiveSmallIntegerField(choices=settings.GENDER_CHOICES, null=True, blank=True)
    blood_type = models.CharField(max_length=3, null=True)
    #
    create_date = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    # class Meta:
    #     db_table = 'api_user' # name table

    def __str__(self):
        return self.email


# Country (
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     country VARCHAR(50) NOT NULL,
#     create_date DATETIME,
#     last_update DATETIME
# )
class Country(models.Model):
    # ID is by default
    # id = models.AutoField(primary_key=True)
    country = models.CharField(max_length=50, null=False, blank=False, unique=True)
    #
    create_date = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.country


# City (
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     city VARCHAR(50),
#     country_id INT, → COUNTRY ID
#     create_date DATETIME,
#     last_update DATETIME
# )
class City(models.Model):
    city = models.CharField(max_length=50, null=False, blank=False, unique=True)  # no 2 cities have the same name
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='cities')  # auto name: country_id
    #
    create_date = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.city


# Address (
# 	id INT AUTO_INCREMENT PRIMARY KEY,
#   city_id VARCHAR(50) NOT NULL,  CITY ID
# 	address_gu VARCHAR(50) NOT NULL,
# 	address_dong VARCHAR(50) NOT NULL,
# 	address_detail VARCHAR(100) NOT NULL,
#   postcode VARCHAR(10) NOT NULL,
#   phone VARCHAR(15), 
#   latitude DECIMAL(10,8),
#   longtitude DECIMAL(11,8),
#   create_date DATETIME, 
#   last_update DATETIME
# );

# class Address(models.Model):
#     # auto name: city_id
#     city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='cities')
#     address_gu = models.CharField(max_length=50, null=False)
#     address_dong = models.CharField(max_length=50, null=False)
#     address_detail = models.CharField(max_length=100, null=False)
#     postcode = models.CharField(max_length=10, null=False)
#     phone = models.CharField(max_length=15)
#     latitude = models.DecimalField(max_digits=11, decimal_places=8, default=0, null=True)
#     longtitude = models.DecimalField(max_digits=11, decimal_places=8, default=0, null=True)
#     #
#     create_date = models.DateTimeField(auto_now_add=True)
#     last_update = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return self.address_detail


# Apartment(
# 	id INT AUTO_INCREMENT PRIMARY KEY,
# 	name VARCHAR(125) NOT NULL UNIQUE, 
# 	address_id INT,  ADDRESS ID
# 	description VARCHAR(500),
# 	is_active BOOLEAN,
# 	create_date DATETIME,
# 	last_update DATETIME
# );

class Apartment(models.Model):
    # ID is by default
    # id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, null=False, unique=True)
    # foreign key, auto generate db column: address_id
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='cities')
    address_gu = models.CharField(max_length=50, null=False)
    address_dong = models.CharField(max_length=50, null=False)
    address_road = models.CharField(max_length=250, null=False)
    address_detail = models.CharField(max_length=100, null=False)
    postcode = models.CharField(max_length=10, null=False)
    phone = models.CharField(max_length=15)
    latitude = models.DecimalField(max_digits=11, decimal_places=8, default=0, null=True)
    longtitude = models.DecimalField(max_digits=11, decimal_places=8, default=0, null=True)
    description = models.CharField(max_length=500, null=True)
    is_active = models.BooleanField(default=True)
    #
    create_date = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


# Household(
# 	id,
# 	apartment_id,  APT ID
# 	address_dong VARCHAR(10),
# 	house_number VARCHAR(10),
# 	is_empty BOOLEAN
# 	create_date DATETIME,	
# 	last_update DATETIME
# );


class Household(models.Model):
    # ID is by default
    # id = models.AutoField(primary_key=True)
    # foreign key
    apartment = models.ForeignKey(Apartment, on_delete=models.CASCADE, related_name='apartments')
    #
    address_dong = models.CharField(max_length=10, null=True)
    house_number = models.CharField(max_length=10, null=True)
    is_empty = models.BooleanField(default=False)

    # STATUS_CHOICES = (
    #     (0, "occupied"),
    #     (1, "available")
    # )
    # status = models.IntegerField(choices=STATUS_CHOICES, null=False, blank=False)
    #
    create_date = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)


# ImageFile (
# 	id INT AUTO_INCREMENT PRIMARY KEY,
# 	file_name VARCHAR(250) NOTNULL,
#     file_url VARCHAR(1024) NOT NULL,
#     file_type VARCHAR(25),
#     file_size INT,
#     create_date DATETIME, 
# 	last_update DATETIME
# );

class ImageFile(models.Model):
    # ID is by default
    # id = models.AutoField(primary_key=True)
    # foreign key
    #
    file_name = models.CharField(max_length=250, null=False, unique=False)
    file_url = models.ImageField(max_length=None, null=False, upload_to='./pictures')
    file_type = models.CharField(max_length=25, null=True, blank=True)
    file_size = models.IntegerField()
    #
    create_date = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)


# UserAvatar (
# 	id INT AUTO_INCREMENT PRIMARY KEY,
# 	user_id INT,  USER ID
# 	image_file_id,  IMAGEFILE ID
#   is_active BOOLEAN,
# 	create_date DATETIME,
# 	last_update DATETIME
# )

class UserAvatar(models.Model):
    # ID is by default
    # id = models.AutoField(primary_key=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_ua_list')
    image_file = models.ForeignKey(ImageFile, on_delete=models.CASCADE, related_name='image_file_list')
    is_active = models.BooleanField(default=True)

    create_date = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)


# Status( //Applying, Waiting, approval, eviction
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     name VARCHAR(50) NOT NULL,
#     description VARCHAR(256),
#     create_date DATETIME,
#     last_update DATETIME
# )
class Status(models.Model):
    # ID is by default
    # id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, null=False, blank=False)
    description = models.CharField(max_length=256, null=True)
    #
    create_date = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


# DocumentFile (
# 	id INT AUTO_INCREMENT PRIMARY KEY,
# 	file_name VARCHAR(250),
#     file_url VARCHAR(1024) NOT NULL,
#     file_type VARCHAR(25),
#     file_size INT,
#     user_id INT,
#     is_active BOOLEAN
#     create_date DATETIME,
#     last_update DATETIME
# )
class DocumentFile(models.Model):
    # ID is by default
    # id = models.AutoField(primary_key=True)
    # foreign key
    #
    file_name = models.CharField(max_length=250, null=False, unique=False)
    file_url = models.ImageField(max_length=None, null=False, upload_to='./pictures')
    file_type = models.CharField(max_length=25, null=True, blank=True)
    file_size = models.IntegerField()
    is_active = models.BooleanField(default=True)
    user_id = models.IntegerField(null=False)
    #
    create_date = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.file_name


# UserStatus (
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     user_id INT, → USER ID
#     status_id INT, → STATUS ID
#     staff_id INT, → USER ID (can be admin)
#     document_file_id INT, --> DOCUMENTFILE, //등본
#     create_date DATETIME,
#     last_update DATETIME
# )
# class UserStatus(models.Model):
#     # ID is by default
#     # id = models.AutoField(primary_key=True)
#     user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='users')
#     staff = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='staffs', null=True)
#     status = models.ForeignKey(Status, db_column='status', on_delete=models.CASCADE, related_name='status_list')
#     #
#     document_file = models.ForeignKey(DocumentFile, on_delete=models.CASCADE, related_name='document_files')
#     #
#     create_date = models.DateTimeField(auto_now_add=True)
#     last_update = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return self.id


# UserHousehold (
# 	id INT AUTO_INCREMENT PRIMARY KEY,
# 	user_id INT,  USER ID
# 	household_id INT,  HOUSEHOLD ID
# 	is_owner BOOLEAN,
# 	is_active BOOLEAN,
#     create_date DATETIME,
#     last_update DATETIME
# )
class UserHousehold(models.Model):
    # ID is by default
    # id = models.AutoField(primary_key=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_list')
    household = models.ForeignKey(Household, on_delete=models.CASCADE, related_name='households')
    is_owner = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    #
    create_date = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)


# DepartmentIndex ( //Community,HR, Financial, Accouting, Admistration, IT, Sales, Training
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     name VARCHAR(125) NOT NULL,
#     description VARCHAR(500),
#     create_date DATETIME,
#     last_update DATETIME
# );
class DepartmentIndex(models.Model):
    # ID is by default
    # id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=125, null=False, unique=True)
    description = models.CharField(max_length=500)
    create_date = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


# Department ( //Community,HR, Financial, Accouting, Admistration, IT, Sales, Training
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     name VARCHAR(125) NOT NULL,
#     department_kind_id INT, →  DEP KIND ID
#     create_date DATETIME,
#     last_update DATETIME
# );
class Department(models.Model):
    # ID is by default
    # id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=125, null=True)
    apartment = models.ForeignKey(Apartment, on_delete=models.CASCADE, related_name='apartment_dep_list')
    department_index = models.ForeignKey(DepartmentIndex, on_delete=models.CASCADE, related_name='depidx_dep_list', null=True)
    description = models.CharField(max_length=500, null=True)
    #
    create_date = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)


# Role ( //비회원, 직원, 입주민, 관리자 Non-member, residents, lecturer, representative, IT dev, manager, ...
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     role VARCHAR(30) NOT NULL,
#     description TEXT,
#     is_active BOOLEAN,
#     create_date DATETIME,
#     last_update DATETIME
# );
class Role(models.Model):
    # ID is by default
    # id = models.AutoField(primary_key=True)
    role = models.CharField(max_length=30, null=False, blank=False)
    description = models.TextField(null=True)
    is_active = models.BooleanField(default=True)
    #
    create_date = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.role


# DepartmentRole ( //each department has different roles for members
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     department_id INT NOT NULL,	→ DEPARTMENT ID
#     role_id INT NOT NULL, → ROLE
#     is_active BOOLEAN,
#     create_date DATETIME,
#     last_update DATETIME
# );
class DepartmentRole(models.Model):
    # ID is by default
    # id = models.AutoField(primary_key=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='dep_deprole_list')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='role_deprole_list')
    is_active = models.BooleanField(null=False)
    #
    create_date = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.role.role)


# UserRole ( //assign role to each member in one department
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     user_id INT,	→ USER ID
#     department_role_id INT NOT NULL, → DEPARTMENT ROLE
#     is_active BOOLEAN,
#     create_date DATETIME,
#     last_update DATETIME
# )
class UserRoleStatus(models.Model):
    # ID is by default
    # id = models.AutoField(primary_key=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_userrole_list')
    department_role = models.ForeignKey(DepartmentRole, on_delete=models.CASCADE, related_name='deprole_userrole_list')
    staff = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='staffs', null=True)
    status = models.ForeignKey(Status, db_column='status', on_delete=models.CASCADE, related_name='status_list',
                               null=True)
    #
    document_file = models.ForeignKey(DocumentFile, on_delete=models.CASCADE, related_name='document_files')

    is_active = models.BooleanField(default=False)
    #
    create_date = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)


# Permission ( // View list, Read permission, Write permission, Write comment, Force delete, Hide post
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     name VARCHAR(100) NOT NULL UNIQUE,
#     description VARCHAR(255),
#     create_date DATETIME,
#     last_update DATETIME
# )
class Permission(models.Model):
    # ID is by default
    # id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, null=False, blank=False, unique=True)
    description = models.TextField(null=True)
    #
    create_date = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


# AppFeature (
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     name VARCHAR(100) NOT NULL UNIQUE,
#     description VARCHAR(255),
#     is_active BOOLEAN
#     create_date DATETIME,
#     last_update DATETIME
# )
class AppFeature(models.Model):
    # ID is by default
    # id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, null=False, blank=False, unique=True)
    description = models.TextField(null=True)
    is_active = models.BooleanField(default=True)
    #
    create_date = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


# RoleFeaturePermission (
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     department_role_id INT NOT NULL, → DepartmentRole ID
#     app_feature_id INT NOT NULL, → FEATURE ID
#     permission_id INT NOT NULL, → PERMISSION ID
#     is_active BOOLEAN,
#     create_date DATETIME,
#     last_update DATETIME
# )
class RoleFeaturePermission(models.Model):
    # ID is by default
    # id = models.AutoField(primary_key=True)
    department_role = models.ForeignKey(DepartmentRole, on_delete=models.CASCADE, related_name='deprole_rfp_list')
    app_feature = models.ForeignKey(AppFeature, on_delete=models.CASCADE, related_name='app_feature_rfp_list')
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE, related_name='permission_rfp_list')
    is_active = models.BooleanField(default=False)
    #
    create_date = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)


# Login (
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     user_id INT,
#     login_time DATETIME,
#     logout_time DATETIME,
#     last_app_feature_id INT, → FEATURE ID,
#     is_last BOOLEAN
# )
class Login(models.Model):
    # ID is by default
    # id = models.AutoField(primary_key=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_login_list')
    login_time = models.DateTimeField(null=False, blank=False)
    logout_time = models.DateTimeField(null=True, blank=False)
    last_app_feature = models.ForeignKey(AppFeature, on_delete=models.CASCADE, related_name='app_feature_login_list',
                                         null=True)
    is_last = models.BooleanField(default=False)

    #
    # create_date = models.DateTimeField(auto_now_add=True)
    # last_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)


# UserBodyInfo (
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     user_id —> User ID
#     height INT,
#     weight INT,
#     waist INT,
#     create_date DATETIME,
#     last_update DATETIME
# )
class UserBodyInfo(models.Model):
    # ID is by default
    # id = models.AutoField(primary_key=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_uei_list')
    height = models.IntegerField(default=0)
    weight = models.IntegerField(default=0)
    waist = models.IntegerField(default=0)
    #
    create_date = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)


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
class Club(models.Model):
    # ID is by default
    # id = models.AutoField(primary_key=True)
    apartment = models.ForeignKey(Apartment, on_delete=models.CASCADE, related_name='apartment_club_list')
    name = models.CharField(max_length=125, null=False, unique=True)
    phone = models.CharField(max_length=11)
    club_register_number = models.CharField(max_length=10)
    club_register_date = models.DateTimeField(null=False, blank=False)
    ot_number = models.IntegerField()
    ot_period = models.IntegerField()
    description = models.TextField()
    #
    create_date = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
