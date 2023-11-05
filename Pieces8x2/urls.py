# -*- coding: utf-8 -*-

#  Copyright (c) 2023 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.urls import path
from Pieces8x2 import views

app_name = 'Pieces8x2'

# base = /pieces8x2/

urlpatterns = [
    path('view/<nr>/',
         views.ShowPiecesView.as_view(),
         name='show-pieces'),
]


# end of file

