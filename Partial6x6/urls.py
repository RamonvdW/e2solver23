# -*- coding: utf-8 -*-

#  Copyright (c) 2023 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.urls import path
from Partial6x6 import views

app_name = 'Partial6x6'

# base = /6x6/

urlpatterns = [
    path('view/auto/',
         views.ShowPart6x6AutoView.as_view(),
         name='auto-show'),

    path('view/<nr>/',
         views.ShowPart6x6View.as_view(),
         name='show'),

    path('quart6/auto/',
         views.Quart6AutoView.as_view(),
         name='auto-show-quart6'),

    path('quart6/<nr>/',
         views.Quart6View.as_view(),
         name='show-quart6'),
]


# end of file

