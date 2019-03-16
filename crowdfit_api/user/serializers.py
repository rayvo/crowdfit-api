""""
@author: moon
@date: 2019.02.27
"""

from django.contrib.auth import get_user_model

# for custom user
User = get_user_model()

from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from crowdfit_api.user.models import Country, City, Address, Apt, Household, Status


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
class UserSerializer(serializers.HyperlinkedModelSerializer):
    # password = serializers.CharField(
    #     style={'input_type': 'password'}
    # )
    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'password', 'nickname', 'fullname', 'birthday', 'gender', 'phone', "bloodType")
        extra_kwargs = {'password': {'write_only': True, 'required': True}}

    validate_password = make_password  # for hashing password


# City (
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     city VARCHAR(50),
#     countryID INT, → COUNTRY ID
#     lastUpdate DATETIME
# )
class CitySerializers(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ('id', 'city', 'country')


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
        fields = ('id', 'name', 'desc', 'address', 'addresses')


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
        fields = ('id', 'addDong', 'houseNum', 'status', 'apt', 'apts')
        extra_kwargs = {'lastUpdate': {'read_only': True}}


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
        fields = ('id', 'name', 'desc')
        extra_kwargs = {'lastUpdate': {'read_only': True}}
