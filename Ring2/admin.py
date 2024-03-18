# -*- coding: utf-8 -*-

#  Copyright (c) 2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.contrib import admin
from Ring2.models import Ring2


class Ring2Admin(admin.ModelAdmin):

    list_filter = ('is_processed', 'based_on_ring1')

    search_fields = ('nr',)


admin.site.register(Ring2, Ring2Admin)


# end of file
