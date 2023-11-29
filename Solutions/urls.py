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

    path('view6x6/auto/',
         views.Show6x6AutoView.as_view(),
         name='auto-show-6x6'),

    path('view6x6/<nr>/',
         views.Show6x6View.as_view(),
         name='show-6x6'),

    path('half6/auto/',
         views.Half6AutoView.as_view(),
         name='auto-show-half6'),

    path('half6/<nr>/',
         views.Half6View.as_view(),
         name='show-half6'),

    path('quart6/auto/',
         views.Quart6AutoView.as_view(),
         name='auto-show-quart6'),

    path('quart6/<nr>/',
         views.Quart6View.as_view(),
         name='show-quart6'),
]


# end of file

