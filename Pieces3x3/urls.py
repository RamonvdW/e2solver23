# -*- coding: utf-8 -*-

#  Copyright (c) 2023 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.urls import path
from Pieces3x3 import views

app_name = 'Pieces3x3'

# base = /3x3/

urlpatterns = [
    path('view/<nr>/',
         views.ShowView.as_view(),
         name='show'),
]


# end of file

