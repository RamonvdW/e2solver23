# -*- coding: utf-8 -*-

#  Copyright (c) 2023-2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.contrib import admin
from WorkQueue.models import Work, ProcessorUsedPieces


class WorkAdmin(admin.ModelAdmin):

    list_filter = ('done', 'doing', 'priority', 'processor', 'job_type', 'location')


class ProcessorUsedPiecesAdmin(admin.ModelAdmin):

    list_filter = ('processor',)


admin.site.register(Work, WorkAdmin)
admin.site.register(ProcessorUsedPieces, ProcessorUsedPiecesAdmin)

# end of file
