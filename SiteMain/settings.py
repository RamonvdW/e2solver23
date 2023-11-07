# -*- coding: utf-8 -*-

#  Copyright (c) 2023 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

"""
Django settings for SiteMain project.

Generated by 'django-admin startproject' using Django 4.2.6.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'your security key'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = []

INTERNAL_IPS = []


# Application definition
INSTALLED_APPS = [
    'BasePieces',
    'Pieces2x2',
    'Pieces4x4',
    'Borders4x2',
    'BorderSolutions',
    'django.contrib.admin',
    'django.contrib.staticfiles',   # gather static files from modules helper
    'django.contrib.sessions',      # support for database-backed sessions; needed for logged-in user
    'django.contrib.auth',          # authenticatie framework
    'django.contrib.contenttypes',  # permission association to models
    'django.contrib.messages',
    'debug_toolbar',
]


# AuthenticationMiddleware must be after SessionMiddleware
#        MessageMiddleware must be after SessionMiddleware
#
# SecurityMiddleware provides:  (see https://docs.djangoproject.com/en/4.2/ref/middleware/)
# - Strict-Transport-Security header (max-age = settings.SECURE_HSTS_SECONDS)
# - Referrer-Policy header (='same-origin')
# - Cross-Origin-Opener-Policy header (='same-origin')
# - X-Content-Type-Options header (='nosniff')
MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.security.SecurityMiddleware',                # security (https improvements)
    'django.contrib.sessions.middleware.SessionMiddleware',         # manage sessions across requests
    'django.contrib.auth.middleware.AuthenticationMiddleware',      # geeft request.user
    'django.middleware.common.CommonMiddleware',                    # adds Content-Length header to http responses
    'django.middleware.csrf.CsrfViewMiddleware',                    # security (cross-site request forgery)
    'django.contrib.messages.middleware.MessageMiddleware',         # mandatory for admin
    'django.middleware.clickjacking.XFrameOptionsMiddleware',       # security: ask browser to deny (i)frame embedding
]

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
    {
        'NAME': 'default',
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # 'DIRS': [ str(APPS_DIR.path('templates')), ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',  # permission checking
                'django.contrib.messages.context_processors.messages',
            ],
        },
    }
]


# point out location of WSGI application for django runserver command
WSGI_APPLICATION = 'SiteMain.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'OPTIONS': { 'options': '-c search_path=your_db_schema'},   # not needed below PostgreSQL version 15
        'NAME': 'your_db_name',
        'USER': 'your_db_user',
        'PASSWORD': 'your_db_password',
        'HOST': 'localhost',
        'PORT': '5432'
    }
}

# allow the database connections to stay open
CONN_MAX_AGE = None

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators
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
# https://docs.djangoproject.com/en/4.2/topics/i18n/
LANGUAGE_CODE = 'nl-NL'     # provides wanted date/time output format
TIME_ZONE = 'Europe/Amsterdam'
USE_I18N = True

# sla alle datums in de database op als UTC
# dit doet PostgreSQL sowieso, onafhankelijk van deze instelling
# alleen vertalen bij presentatie naar de gebruiker toe
USE_TZ = True


# top-level URL verdeling naar apps
ROOT_URLCONF = 'SiteMain.urls'


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = 'SiteMain/.static'    # relative to project top-dir
STATICFILES_FINDER = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder'
]

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# logging to syslog
# zie https://docs.djangoproject.com/en/3.0/topics/logging/
# en  https://docs.python.org/3/howto/logging-cookbook.html#logging-to-a-single-file-from-multiple-processes
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': "[django] %(asctime)s %(name)s [%(levelname)s] %(message)s",
            'datefmt': "%Y-%b-%d %H:%M:%S"
        }
    },
    'handlers': {
        'syslog': {
            # 'level': 'DEBUG',
            'class': 'logging.handlers.SysLogHandler',
            'formatter': 'verbose',
            'facility': 'user',
            'address': '/dev/log'
        },
        # 'file': {
        #     'level': 'INFO',
        #     'class': 'logging.FileHandler',
        #     'filename': '/tmp/django.log'
        # },
    },
    'loggers': {
        'django': {
            'handlers': ['syslog'],
            'level': 'ERROR'            # Note: WARNING gives 1 log line for every code 404 (resource not found)
        },
        'xmlschema': {
            'handlers': ['syslog'],
            'level': 'WARNING'
        },
        'asyncio': {
            'handlers': ['syslog'],
            'level': 'WARNING'
        },
        '': {
            'handlers': ['syslog'],
            'level': 'INFO'
        }
    }
}


from SiteMain.settings_local import *

# end of file

