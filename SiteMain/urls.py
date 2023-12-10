# -*- coding: utf-8 -*-

#  Copyright (c) 2023 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

"""
    URL configuration for the project.
"""

from django.urls import path
from django.contrib import admin
from django.conf.urls import include


urlpatterns = [
    path('__debug__/', include('debug_toolbar.urls')),
    path('2x2/',       include('Pieces2x2.urls')),
    path('4x4/',       include('Partial4x4.urls')),
    path('6x6/',       include('Partial6x6.urls')),
    path('solutions/', include('Solutions.urls')),
    path('admin/',     admin.site.urls),
]


# end of file
