# -*- coding: utf-8 -*-

#  Copyright (c) 2023-2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.contrib import admin
from BasePieces.models import BasePiece, Block

admin.site.register(BasePiece)
admin.site.register(Block)

# end of file
