# -*- coding: utf-8 -*-

#  Copyright (c) 2023 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.contrib import admin
from Solutions.models import Solution, Solution4x4, Solution6x6     # State


class AdminSolution6x6(admin.ModelAdmin):

    list_filter = ('is_processed', 'processor',)


class AdminSolution4x4(admin.ModelAdmin):

    list_filter = ('is_processed', 'processor',)


admin.site.register(Solution)
admin.site.register(Solution4x4, AdminSolution6x6)
admin.site.register(Solution6x6, AdminSolution6x6)
# admin.site.register(State)

# end of file
