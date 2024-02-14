# -*- coding: utf-8 -*-

#  Copyright (c) 2023-2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.urls import path
from Ring1 import views

app_name = 'Ring1'

# base = /ring1/

urlpatterns = [
    path('status/',
         views.StatusView.as_view(),
         name='status'),

    path('view/<nr>/',
         views.ShowRing1View.as_view(),
         name='show'),

    path('corner1/<nr>/',
         views.ShowCorner1View.as_view(),
         name='show-c1'),

    path('corner2/<nr>/',
         views.ShowCorner2View.as_view(),
         name='show-c2'),

    path('corner3/<nr>/',
         views.ShowCorner3View.as_view(),
         name='show-c3'),

    path('corner4/<nr>/',
         views.ShowCorner4View.as_view(),
         name='show-c4'),

    path('corner12/<nr>/',
         views.ShowCorner12View.as_view(),
         name='show-c12'),

    path('corner34/<nr>/',
         views.ShowCorner34View.as_view(),
         name='show-c34'),
]


# end of file

