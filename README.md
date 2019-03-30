# crowdfit-api
Install libs

-pip3 install django-cors-headers

-pip install pymysql

-edit the __init__.py file in your project origin dir(the same as settings.py)

ADD:

	import pymysql

	pymysql.install_as_MySQLdb()

-pip install mysqlclient

-pip install django-phonenumber-field

-pip install phonenumbers

-pip install djangorestframework_simplejwt

#install api for phone verification. https://www.twilio.com/

-pip install authy

-pip install Pillow

-Create Database: CREATE DATABASE crowdfitdb CHARACTER SET utf8 COLLATE utf8_general_ci;

-Modify setting file to change the password for your root db

-python manage.py migrate

-python manage.py createsuperuser --email taeyuim@naver.com --username admin
