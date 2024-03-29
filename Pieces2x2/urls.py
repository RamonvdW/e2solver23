# -*- coding: utf-8 -*-

#  Copyright (c) 2023-2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.urls import path
from Pieces2x2 import views

app_name = 'Pieces2x2'

# base = /2x2/

urlpatterns = [
    path('view/<nr>/',
         views.ShowView.as_view(),
         name='show'),

    path('options/',
         views.OptionsView.as_view(),
         name='options'),

    path('options/<nr>/',
         views.OptionsView.as_view(),
         name='options-nr'),

    path('options-list/',
         views.OptionsListView.as_view(),
         name='options-list'),
]


# end of file
