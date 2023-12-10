# -*- coding: utf-8 -*-

#  Copyright (c) 2023 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.urls import path
from Partial4x4 import views

app_name = 'Partial4x4'

# base = /4x4/

urlpatterns = [
    path('view/auto/',
         views.ShowPart4x4AutoView.as_view(),
         name='auto'),

    path('view/<nr>/',
         views.ShowPart4x4View.as_view(),
         name='show'),
]


# end of file

