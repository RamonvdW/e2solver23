# -*- coding: utf-8 -*-

#  Copyright (c) 2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.urls import path
from Ring2 import views

app_name = 'Ring2'

# base = /ring2/

urlpatterns = [
    path('view/<nr>/',
         views.ShowRing2View.as_view(),
         name='show'),
]


# end of file
