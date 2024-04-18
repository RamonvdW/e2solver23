# -*- coding: utf-8 -*-

#  Copyright (c) 2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.contrib import admin
from Ring3.models import Ring3


class Ring3Admin(admin.ModelAdmin):

    search_fields = ('nr',)


admin.site.register(Ring3, Ring3Admin)


# end of file
