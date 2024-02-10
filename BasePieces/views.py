# -*- coding: utf-8 -*-

#  Copyright (c) 2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.views.generic import TemplateView
from django.templatetags.static import static
from types import SimpleNamespace

TEMPLATE_SHOW = 'basepieces/show.dtl'


class ShowView(TemplateView):

    template_name = TEMPLATE_SHOW

    def get_context_data(self, **kwargs):
        """ called by the template system to get the context data for the template """
        context = super().get_context_data(**kwargs)

        context['groups'] = groups = list()
        group = list()
        for nr in range(1, 256+1):
            piece = SimpleNamespace(nr=nr, img=static('pieces/%s.png' % nr))
            group.append(piece)
            if len(group) == 8:
                groups.append(group)
                group = list()
        # for

        return context


# end of file
