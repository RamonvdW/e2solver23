# -*- coding: utf-8 -*-

#  Copyright (c) 2023 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.contrib import admin
from Pieces3x3.models import ThreeSide, Piece3x3


admin.site.register(ThreeSide)
admin.site.register(Piece3x3)

# end of file
