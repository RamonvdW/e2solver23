# -*- coding: utf-8 -*-

#  Copyright (c) 2023 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.contrib import admin
from WorkQueue.models import Work


class WorkAdmin(admin.ModelAdmin):

    list_filter = ('done', 'doing', 'priority')


admin.site.register(Work, WorkAdmin)

# end of file
