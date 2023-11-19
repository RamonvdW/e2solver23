# -*- coding: utf-8 -*-

#  Copyright (c) 2023 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.urls import path
from Solutions import views

app_name = 'Solutions'

# base = /solutions/

urlpatterns = [
    path('view/auto/',
         views.ShowAutoView.as_view(),
         name='auto-show'),

    path('view/<nr>/',
         views.ShowView.as_view(),
         name='show'),

    path('view4x4/auto/',
         views.Show4x4AutoView.as_view(),
         name='auto-show-4x4'),

    path('view4x4/<nr>/',
         views.Show4x4View.as_view(),
         name='show-4x4'),
]


# end of file

