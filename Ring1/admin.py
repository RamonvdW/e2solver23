# -*- coding: utf-8 -*-

#  Copyright (c) 2023-2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.contrib import admin
from Ring1.models import Ring1, Corner1, Corner2, Corner3, Corner4, Corner12, Corner34


class Ring1Admin(admin.ModelAdmin):
    list_filter = ('is_processed', 'processor')


admin.site.register(Ring1, Ring1Admin)
admin.site.register(Corner1)
admin.site.register(Corner2)
admin.site.register(Corner3)
admin.site.register(Corner4)
admin.site.register(Corner12)
admin.site.register(Corner34)

# end of file
