# crowdfit-api
Install libs

-pip3 install django-cors-headers

-pip install pymysql

-edit the __init__.py file in your project origin dir(the same as settings.py)

ADD:

	import pymysql

	pymysql.install_as_MySQLdb()

-pip install django-phonenumber-field

-pip install phonenumbers

-pip install djangorestframework_simplejwt

-python manage.py migrate
