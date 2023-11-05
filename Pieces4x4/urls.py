# -*- coding: utf-8 -*-

#  Copyright (c) 2023 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.urls import path
from Pieces4x4 import views

app_name = 'Pieces4x4'

# base = /pieces4x4/

urlpatterns = [
    path('view/<nr>/',
         views.ShowPiecesView.as_view(),
         name='show-pieces'),
]


# end of file

