# -*- coding: utf-8 -*-

#  Copyright (c) 2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.urls import path
from BasePieces import views

app_name = 'BasePieces'

# base = /1x1/

urlpatterns = [
    path('view/',
         views.ShowView.as_view(),
         name='view'),
]


# end of file

