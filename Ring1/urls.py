# -*- coding: utf-8 -*-

#  Copyright (c) 2023-2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.urls import path
from Ring1 import views

app_name = 'Ring1'

# base = /ring1/

urlpatterns = [
    path('view/<nr>/',
         views.ShowRing1View.as_view(),
         name='show'),
]


# end of file
