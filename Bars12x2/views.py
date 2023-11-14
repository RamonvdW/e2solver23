# -*- coding: utf-8 -*-

#  Copyright (c) 2023 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.http import Http404
from django.urls import reverse
from django.views.generic import TemplateView
from django.templatetags.static import static
from Bars12x2.models import Bar12x2
from Pieces2x2.models import Piece2x2


TEMPLATE_VIEW = 'bars12x2/show.dtl'


class ShowView(TemplateView):

    template_name = TEMPLATE_VIEW

    rot2transform = {
        # rotations are counter-clockwise, but CSS rotation are clockwise
        0: 'rotate(0deg)',
        1: 'rotate(270deg)',
        2: 'rotate(180deg)',
        3: 'rotate(90deg)',
    }

    def _get_piece2x2(self, nr):
        piece = Piece2x2.objects.get(nr=nr)

        piece.img1 = static('pieces/%s.png' % piece.nr1)
        piece.img2 = static('pieces/%s.png' % piece.nr2)
        piece.img3 = static('pieces/%s.png' % piece.nr3)
        piece.img4 = static('pieces/%s.png' % piece.nr4)

        piece.transform1 = self.rot2transform[piece.rot1]
        piece.transform2 = self.rot2transform[piece.rot2]
        piece.transform3 = self.rot2transform[piece.rot3]
        piece.transform4 = self.rot2transform[piece.rot4]

        return piece

    def get_context_data(self, **kwargs):
        """ called by the template system to get the context data for the template """
        context = super().get_context_data(**kwargs)

        try:
            nr = int(kwargs['nr'][:8])      # afkappen voor de veiligheid
        except ValueError:
            raise Http404('Not found')

        nr = int((nr - 1) / 10)
        nr = 1 + nr * 10

        if nr > 100:
            context['url_prev100'] = reverse('Bars12x2:show', kwargs={'nr': nr - 100})
        if nr > 10:
            context['url_prev10'] = reverse('Bars12x2:show', kwargs={'nr': nr - 10})
        context['url_next10'] = reverse('Bars12x2:show', kwargs={'nr': nr + 10})
        context['url_next100'] = reverse('Bars12x2:show', kwargs={'nr': nr + 100})
        context['url_next1000'] = reverse('Bars12x2:show', kwargs={'nr': nr + 1000})

        context['bars'] = bars = Bar12x2.objects.filter(nr__gte=nr, nr__lt=nr+10).order_by('nr')
        for bar in bars:
            bar.p1 = self._get_piece2x2(bar.p1)
            bar.p2 = self._get_piece2x2(bar.p2)
            bar.p3 = self._get_piece2x2(bar.p3)
            bar.p4 = self._get_piece2x2(bar.p4)
            bar.p5 = self._get_piece2x2(bar.p5)
            bar.p6 = self._get_piece2x2(bar.p6)
        # for

        return context


# end of file
