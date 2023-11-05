# -*- coding: utf-8 -*-

#  Copyright (c) 2023 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.http import Http404
from django.urls import reverse
from django.views.generic import TemplateView
from django.templatetags.static import static
from BasePieces.hints import HINT_NRS
from Pieces4x4.models import Piece4x4


TEMPLATE_VIEW = 'cornersolutions/show.dtl'


class ShowView(TemplateView):

    template_name = TEMPLATE_VIEW

    def get_context_data(self, **kwargs):
        """ called by the template system to get the context data for the template """
        context = super().get_context_data(**kwargs)

        try:
            nr = int(kwargs['nr'][:12])      # afkappen voor de veiligheid
        except ValueError:
            raise Http404('Not found')

        hint2, hint4, hint1, hint3 = HINT_NRS

        for p1 in Piece4x4.objects.filter(nr11=hint1).iterator(chunk_size=10):
            base1 = [p1.nr1, p1.nr2, p1.nr3, p1.nr4, p1.nr5, p1.nr6, p1.nr7, p1.nr8,
                     p1.nr9, p1.nr10, p1.nr11, p1.nr12, p1.nr13, p1.nr14, p1.nr15, p1.nr16]

            # check = len(set(base1))
            # if check != 16:
            #     print(repr(base1))
            #     continue

            context['p1'] = p1.nr

            for p2 in (Piece4x4
                       .objects
                       .filter(nr11=hint2)
                       .exclude(nr1=p1.nr1)
                       .exclude(nr2__in=base1)
                       .exclude(nr3__in=base1)
                       .exclude(nr4__in=base1)
                       .exclude(nr5__in=base1)
                       .exclude(nr6__in=base1)
                       .exclude(nr7__in=base1)
                       .exclude(nr8__in=base1)
                       .exclude(nr9__in=base1)
                       .exclude(nr10__in=base1)
                       .exclude(nr12__in=base1)
                       .exclude(nr13__in=base1)
                       .exclude(nr14__in=base1)
                       .exclude(nr15__in=base1)
                       .exclude(nr16__in=base1)
                       .iterator(chunk_size=100)):

                context['p2'] = p1.nr
                break
            # for

            break
        # for

        if nr > 1:
            context['url_prev'] = reverse('CornerSolutions:show', kwargs={'nr': nr-1})
        context['url_next'] = reverse('CornerSolutions:show', kwargs={'nr': nr+1})

        return context


# end of file
