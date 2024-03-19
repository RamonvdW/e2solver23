# -*- coding: utf-8 -*-

#  Copyright (c) 2023-2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

"""
    URL configuration for the project.
"""

from django.urls import path
from django.contrib import admin
from django.conf.urls import include


urlpatterns = [
    path('__debug__/',  include('debug_toolbar.urls')),
    path('1x1/',        include('BasePieces.urls')),
    path('2x2/',        include('Pieces2x2.urls')),
    path('ring1/',      include('Ring1.urls')),
    path('ring2/',      include('Ring2.urls')),
    path('solutions/',  include('Solutions.urls')),
    path('admin/',      admin.site.urls),
]


# end of file
