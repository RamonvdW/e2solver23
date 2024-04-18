# -*- coding: utf-8 -*-

#  Copyright (c) 2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.urls import path
from Ring3 import views

app_name = 'Ring3'

# base = /ring2/

urlpatterns = [
    path('view/<nr>/',
         views.ShowRing3View.as_view(),
         name='show'),
]


# end of file
