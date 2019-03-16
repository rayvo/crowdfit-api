"""
@author: moon
@date: 2019.02.28
"""

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import date
from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from phonenumber_field.modelfields import PhoneNumberField
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
#     bloodType CHAR(3),
#     lastUpdate DATETIME
# );
class CustomUser(AbstractUser):
    # ID is by default
    # id = models.AutoField(primary_key=True)
    email = models.EmailField(validators=[validate_email], verbose_name='email address', max_length=255, null=False,
                              unique=True, blank=False)
    fullname = models.CharField(max_length=150, null=False, blank=False)
    nickname = models.CharField(max_length=50, null=False, unique=True, blank=False)
    # password = models.CharField(max_length=256, null=False, blank=False)
    birthday = models.DateField(null=False, blank=False)

    # phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    # phone_number = models.CharField(validators=[phone_regex], max_length=17, default='+82', blank=True) # validators should be a list
    phone = models.CharField(max_length=15, null=True)

    GENDER_CHOICES = (
        (1, "Male"),
        (2, "Female")
    )
    gender = models.PositiveSmallIntegerField(choices=GENDER_CHOICES, null=True, blank=True)
    bloodType = models.CharField(max_length=3, null=True)
    lastUpdate = models.DateTimeField(auto_now_add=True, null=True)

    # profile_photo = models.ImageField(upload_to='./media', blank=True, verbose_name="Profile Picture")

    # class Meta:
    #     db_table = 'api_user' # name table

    def __str__(self):
        return self.username


# Country (
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     country VARCHAR(50),
#     lastUpdate DATETIME
# )
class Country(models.Model):
    # ID is by default
    # id = models.AutoField(primary_key=True)
    country = models.CharField(max_length=50, null=False, blank=False, unique=True)
    lastUpdate = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.country


# City (
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     city VARCHAR(50),
#     countryID INT, → COUNTRY ID
#     lastUpdate DATETIME
# )
class City(models.Model):
    city = models.CharField(max_length=50, null=False, blank=False, unique=True)  # no 2 cities have the same name
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='cities')  # auto name: country_id
    lastUpdate = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.city


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
class Address(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='cities')  # auto name: city_id
    addGu = models.CharField(max_length=50, null=False)
    addDong = models.CharField(max_length=50, null=False)
    addDetail = models.CharField(max_length=100, null=False)
    postcode = models.CharField(max_length=10, null=False)
    phone = models.CharField(max_length=15)
    lat = models.DecimalField(max_digits=11, decimal_places=8, default=0, null=False)
    lng = models.DecimalField(max_digits=11, decimal_places=8, default=0, null=False)
    lastUpdate = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.addDetail


# APT(
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     name VARCHAR(125) NOT NULL UNIQUE,
#     addressID INT, → ADDRESS ID
#     desc VARCHAR(500),
#     createDate DATETIME,
#     lastUpdate DATETIME
# );
class Apt(models.Model):
    # ID is by default
    # id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, null=False, unique=True)
    # foreign key
    address = models.ForeignKey(Address, on_delete=models.CASCADE,
                                related_name='addresses')  # auto generate db column: address_id

    desc = models.CharField(max_length=500, null=True)
    createDate = models.DateTimeField(auto_now=True)
    lastUpdate = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# Household(
#     id,
#     aptID, → APT ID
#     addDong VARCHAR(10),
#     houseNum VARCHAR(10),
#     status INT, //0: occupied, 1: available
#     createDate DATETIME,
#     lastUpdate DATETIME
# );
class Household(models.Model):
    # ID is by default
    # id = models.AutoField(primary_key=True)
    # foreign key
    apt = models.ForeignKey(Apt, on_delete=models.CASCADE,
                                related_name='apts')  # auto generate db column: apt_id
    #
    addDong = models.CharField(max_length=10, null=True)
    houseNum = models.CharField(max_length=10, null=True)

    STATUS_CHOICES = (
        (0, "occupied"),
        (1, "available")
    )
    status = models.IntegerField(choices=STATUS_CHOICES, null=False, blank=False)
    #
    createDate = models.DateTimeField(auto_now=True)
    lastUpdate = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.apt

# Status( //Waiting, approval, eviction
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     name VARCHAR(50) NOT NULL,
#     desc VARCHAR(256),

#     createDate DATETIME,
#     lastUpdate DATETIME
# )
class Status(models.Model):
    # ID is by default
    # id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, null=False, blank=False)
    desc = models.CharField(max_length=256, null=True)
    #
    createDate = models.DateTimeField(auto_now=True)
    lastUpdate = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

