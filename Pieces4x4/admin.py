# -*- coding: utf-8 -*-

#  Copyright (c) 2023 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.contrib import admin
from Pieces4x4.models import FourSides, Piece4x4

admin.site.register(Piece4x4)
admin.site.register(FourSides)

# end of file
