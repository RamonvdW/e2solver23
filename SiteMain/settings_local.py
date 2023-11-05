# -*- coding: utf-8 -*-

#  Copyright (c) 2023 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

"""
    This is a template file.
    Replace with your settings / credential valid for your own system.
"""

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'dit draait alleen lokaal dus niet echt nodig'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['localhost']

INTERNAL_IPS = ALLOWED_HOSTS        # checked by debug toolbar

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'OPTIONS': {'options': '-c search_path=your_db_schema'},
        'NAME': 'your_db_name',
        'USER': 'your_db_user',
        'PASSWORD': 'your_db_password',
        'HOST': 'localhost',
        'PORT': '5432'
    }
}

# end of file

