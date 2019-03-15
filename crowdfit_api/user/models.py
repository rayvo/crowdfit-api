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
        return self.email
