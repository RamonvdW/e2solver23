# -*- coding: utf-8 -*-

#  Copyright (c) 2023 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.contrib import admin
from Pieces2x2.models import TwoSide, TwoSideOptions, Piece2x2, Block2x8


class TwoSideOptionsAdmin(admin.ModelAdmin):

    list_filter = ('processor', 'segment')


admin.site.register(TwoSide)
admin.site.register(TwoSideOptions,TwoSideOptionsAdmin)
admin.site.register(Piece2x2)
admin.site.register(Block2x8)

# end of file
