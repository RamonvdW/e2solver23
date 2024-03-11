# -*- coding: utf-8 -*-

#  Copyright (c) 2023-2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.contrib import admin
from Pieces2x2.models import TwoSide, TwoSideOptions, EvalProgress, Piece2x2


class TwoSideOptionsAdmin(admin.ModelAdmin):

    list_filter = ('processor', 'segment')


class ProgressAdmin(admin.ModelAdmin):

    list_filter = ('eval_size', 'processor')


class Piece2x2Admin(admin.ModelAdmin):

    list_filter = ('is_border', 'has_hint', 'side4')


admin.site.register(TwoSide)
admin.site.register(TwoSideOptions, TwoSideOptionsAdmin)
admin.site.register(EvalProgress, ProgressAdmin)
admin.site.register(Piece2x2, Piece2x2Admin)

# end of file
