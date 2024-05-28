"""
Django settings for FirstApp project.

Generated by 'django-admin startproject' using Django 4.1.4.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-(0gq5bjv$#you+lz*p%&wtbu8@r@a*yx*8y9uo_hny&%@*czsp'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

CELERY_BROKER_URL = 'amqp://localhost'


# Application definition

INSTALLED_APPS = [
    'crispy_forms',
    'crispy_bootstrap5',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'base.apps.BaseConfig',
    'captcha',
    'dbbackup',
    'django.contrib.gis',
    'leaflet',
    'django_filters',
    'django_tables2',
    'easyaudit',
]

AUTH_USER_MODEL = 'base.CustomUser'

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'base.middleware.Custom404Middleware',
    'easyaudit.middleware.easyaudit.EasyAuditMiddleware',
]

ROOT_URLCONF = 'FirstApp.urls'

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

WSGI_APPLICATION = 'FirstApp.wsgi.application'


DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'tesisfarma',
        'USER': 'postgres',
        'PASSWORD': 'laura9891',
        'HOST': 'localhost',
        'PORT': '5433',
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'es-es'

TIME_ZONE = 'America/Havana'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# Para autenticarse con el Email
AUTHENTICATION_BACKENDS = ['base.backend.EmailBackend']

RECAPTCHA_PUBLIC_KEY = '6LctYx4mAAAAACutRGWR1n_aghykJPZsVGudVMqU'
RECAPTCHA_PRIVATE_KEY = '6LctYx4mAAAAAGd_V2kKnlmezWGetZJqGchugiZO'
SILENCED_SYSTEM_CHECKS = ['captcha.recaptcha_test_key_error']

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

DEFAULT_CHARSET = 'utf-8'


# Emailing settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_FROM = 'testtesisfarma@gmail.com'
EMAIL_HOST_USER = 'testtesisfarma@gmail.com'
EMAIL_HOST_PASSWORD = 'pooa tvdz yaln xpmz'
EMAIL_PORT = 587
EMAIL_USE_TLS = True


# Backup de la bd 
DBBACKUP_STORAGE = 'django.core.files.storage.FileSystemStorage'
DBBACKUP_STORAGE_OPTIONS = {'location': 'C:/Users/laumi/Downloads/example/FirstApp/backup_bd'}      


# Para el MAPA
GDAL_LIBRARY_PATH = r'C:\OSGeo4W\bin\gdal308'
GEOS_LIBRARY_PATH = r'C:\OSGeo4W\bin\geos_c'

LEAFLET_CONFIG = {
    'DEFAULT_CENTER': (23.113592, -82.366596),  # Coordenadas de La Habana-Cuba
    'DEFAULT_ZOOM': 12,
    'MIN_ZOOM': 3,
    'MAX_ZOOM': 18,
}


EASY_AUDIT_WATCH_MODEL_EVENTS = True
EASY_AUDIT_WATCH_AUTH_EVENTS = True
EASY_AUDIT_WATCH_REQUEST_EVENTS = True