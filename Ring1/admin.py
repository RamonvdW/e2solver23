# -*- coding: utf-8 -*-

#  Copyright (c) 2023-2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.contrib import admin
from Ring1.models import Ring1, Corner1, Corner2, Corner3, Corner4, Corner12, Corner34


class CornerAdmin(admin.ModelAdmin):

    list_filter = ('seed',)


admin.site.register(Ring1, CornerAdmin)
admin.site.register(Corner1, CornerAdmin)
admin.site.register(Corner2, CornerAdmin)
admin.site.register(Corner3, CornerAdmin)
admin.site.register(Corner4, CornerAdmin)
admin.site.register(Corner12, CornerAdmin)
admin.site.register(Corner34, CornerAdmin)


# end of file
