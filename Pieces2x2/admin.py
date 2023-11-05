# -*- coding: utf-8 -*-

#  Copyright (c) 2023 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.contrib import admin
from Pieces2x2.models import TwoSides, Piece2x2

admin.site.register(Piece2x2)
admin.site.register(TwoSides)

# end of file
