# -*- coding: utf-8 -*-

#  Copyright (c) 2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.contrib import admin
from Pieces3x3.models import Piece3x3


class Piece3x3Admin(admin.ModelAdmin):

    list_filter = ('is_border', 'has_hint', 'side4')


admin.site.register(Piece3x3, Piece3x3Admin)

# end of file
