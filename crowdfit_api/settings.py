"""
@author: Haseung Lee
@date: 2019.02.27
"""

import os
import crowdfit_api

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '&f2-y@=xs-h@)1-*w($#*m48vx161imd6ylxchq-kn1i-=p4ls'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: only allow specifc IP's to be allowed as hosts
# 210.105.48.120 is clubfit's public ip server
# 192.168.1.6 is clubfit's private ip server
# 192.168.0.5 is Haseung's local workspace
ALLOWED_HOSTS = [
    '210.105.48.120',
    '192.168.1.6',
    '192.168.0.5',
    '127.0.0.1',
]
# ALLOWED_HOSTS = []
# 192.168.0.x is the local IP gateway for clubfit
# CORS_ORIGIN_WHITELIST = (
#     'localhost:4200',
#     '192.168.0.*'
# )
CORS_ORIGIN_WHITELIST = (
)
# This is to allow certain IP's to pass CORS Policy and access db
CORS_ALLOW_CREDENTIALS = True

# Application definition

INSTALLED_APPS = [
    'corsheaders',
    # Keep corsheader at the top of the list. This is to allow certain IP's to pass CORS Policy and access db
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.sites',
    'django.contrib.staticfiles',

    'rest_framework',  # Using django rest framework
    'rest_framework.authtoken',  # Using Tokens for authentication
    'phonenumber_field',  # A phonenumber field for models
    # user apps
    'crowdfit_api.user',
]

AUTH_USER_MODEL = 'user.CustomUser'  # Using Custom User Model
SITE_ID = 1

# Keep corsheader at the top of the list
# This is to allow certain IP's to pass CORS Policy and access db
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'crowdfit_api.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'crowdfit_api.wsgi.application'

# TODO: Change password from plaintext to os module
# SECURITY WARNING:
# For instructions go to the following link - step 5 - A Note
# https://justinmi.me/blog/2017/04/28/migrating-sql-databases
DATABASES = {
    'default': {
        # 'ENGINE': 'django.db.backends.sqlite3',
        'ENGINE': 'django.db.backends.mysql',

        'OPTIONS': {
            'read_default_file': 'crowdfit_api/dbproperties.cnf',
        },
        # 'NAME': 'crowdfitdb',
        # 'USER': 'root',
        # 'PASSWORD': 'c210120f',
        # 'HOST': '127.0.0.1',
        # 'PORT': '3306'
    }
}
# for using mysql-connector-python
# DATABASES = {
#     'default': {
#         'ENGINE': 'mysql.connector.django',
#         'NAME': 'crowdfitdb',
#         'USER': 'root',
#         'PASSWORD': '123456',
#         'HOST': '127.0.0.1',
#         'PORT': '3306'
#         'OPTIONS': {
#             'autocommit': True,
#         },
#     }
# }
# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 6,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]
# TODO: implement authentication and permission
REST_FRAMEWORK = {

    # 'DATETIME_FORMAT': '%Y-%m-%d %H:%M:%S (%z)',
    #
    'UNAUTHENTICATED_USER': None,
    'DEFAULT_PERMISSION_CLASSES': [
        # 'rest_framework.permissions.IsAuthenticated',
        # 'rest_framework.permissions.IsAuthenticatedOrReadOnly',
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        # https://www.django-rest-framework.org/api-guide/authentication/
        # 'rest_framework_simplejwt.authentication.JWTAuthentication',
        # Basic authentication is generally only appropriate for testing.
        # 'rest_framework.authentication.BasicAuthentication',
        # Token authentication is appropriate for client-server setups, such as native desktop and mobile clients.
        # The curl command line tool may be useful for testing token authenticated APIs. For example:
        # curl -X GET http://127.0.0.1:8000/api/example/ -H 'Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b'
        # Note: If you use TokenAuthentication in production you must ensure that your API is only available over https.
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 30
}

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
]

# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True
# A boolean that specifies if localized formatting of data will be enabled by default or not
USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = '/static/'
