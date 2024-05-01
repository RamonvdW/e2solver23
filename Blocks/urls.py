# -*- coding: utf-8 -*-

#  Copyright (c) 2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.urls import path
from Blocks import views

app_name = 'Blocks'

# base = /blocks/

urlpatterns = [
    path('2x1/<nr>/',
         views.Show2x1View.as_view(),
         name='show-2x1'),
]


# end of file
