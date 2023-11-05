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
import debug_toolbar

urlpatterns = [
    path('__debug__/', include('debug_toolbar.urls')),
    path('pieces2x2/', include('Pieces2x2.urls')),
    path('pieces4x4/', include('Pieces4x4.urls')),
    path('corner-solutions/', include('CornerSolutions.urls')),
    path('admin/', admin.site.urls),
]


# end of file
