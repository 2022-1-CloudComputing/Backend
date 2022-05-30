"""
Django settings for dropbox project.

Generated by 'django-admin startproject' using Django 4.0.4.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

import json
import os
from pathlib import Path

import my_secrets
import requests

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!

SECRET_KEY = my_secrets.DJANGO_SECRET_KEY["django_key"]


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "file",
    "user",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.contrib.auth.middleware.RemoteUserMiddleware",  # RemoteUserMiddleware, congnito
]

# REST_FRAMEWORK = {
#     'DEFAULT_PERMISSION_CLASSES': (
#         'user.api.permissions.DenyAny',
#     ),
#     'DEFAULT_AUTHENTICATION_CLASSES' : (
#         'rest_framework_jwt.authentication.JSONWebTokenAuthentication'    #cognito
#     )
# }

ROOT_URLCONF = "dropbox.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "dropbox.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

# DATABASES = my_secrets.DATABASES
DATABASES = {  # 테스트 위해서 임시로 선언
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "mydatabase",
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# AbstractUser를 상속받아 User 모델을 새로 만들어서 이 모델을 유저모델로 사용하겠음
AUTH_USER_MODEL = "user.User"


# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")  # 개발자가 관리하는 파일들

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")  # 사용자가 업로드한 파일 관리


# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html#usage
AWS_ACCESS_KEY_ID = my_secrets.AWS.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = my_secrets.AWS.get("AWS_SECRET_ACCESS_KEY")
AWS_ACCOUNT_ID = my_secrets.AWS.get("AWS_ACCOUNT_ID")
AWS_REGION = my_secrets.AWS.get("AWS_REGION")
AWS_STORAGE_BUCKET_NAME = my_secrets.AWS.get("AWS_STORAGE_BUCKET_NAME")
AWS_S3_CUSTOM_DOMAIN = "%s.s3.%s.amazonaws.com" % (AWS_STORAGE_BUCKET_NAME, AWS_REGION)
AWS_AUTO_CREATE_BUCKET = True
AWS_S3_SECURE_URLS = False

AWS_S3_OBJECT_PARAMETERS = {"CacheControl": "max-age=86400"}
AWS_DEFAULT_ACL = "public-read"


# https://velog.io/@jongwho/AWS-Cognito-DRF-%EB%A1%9C%EA%B7%B8%EC%9D%B8-%EA%B5%AC%ED%98%84%ED%95%98%EA%B8%B0with-React1
# cognito
COGNITO_REGION = my_secrets.COGNITO.get("COGNITO_REGION")
COGNITO_USER_POOL_ID = my_secrets.COGNITO.get("COGNITO_USER_POOL_ID")
COGNITO_AUDIENCE = my_secrets.COGNITO.get("COGNITO_AUDIENCE")  # None
# COGNITO_POOL_URL = my_secrets.COGNITO.get("COGNITO_POOL_URL")
COGNITO_IDENTITY_POOL_ID = my_secrets.COGNITO.get("COGNITO_IDENTITY_POOL_ID")
COGNITO_APP_CLIENT_ID = my_secrets.COGNITO.get("COGNITO_APP_CLIENT_ID")

# COGNITO_POOL_URL = f'https://cognito-idp.{COGNITO_AWS_REGION}.amazonaws.com/{COGNITO_AWS_USER_POOL}/.well-known/jwks/json'
# jwks = requests.get(COGNITO_POOL_URL).json()
# rsa_keys = {key['kid']: json.dumps(key) for key in jwks['keys']}

# JWT_AUTH = {
#     # Login Handler
#     'JWT_PAYLOAD_GET_USERNAME_HANDLER': 'cognito_auth.utils.jwt_utils.user_info_handler',
#     # Decode Handler
#     'JWT_DECODE_HANDLER': 'cognito_auth.utils.jwt_utils.cognito_jwt_decoder',
#     'JWT_PUBLIC_KEY': rsa_keys,
#     'JWT_ALGORITHM': 'RS256',
#     'JWT_AUDIENCE': COGNITO_AUDIENCE,
#     'JWT_ISSUER': COGNITO_POOL_URL,
#     'JWT_AUTH_HEADER_PREFIX': 'Bearer',
# }
