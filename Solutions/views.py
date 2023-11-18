# -*- coding: utf-8 -*-

#  Copyright (c) 2023 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.http import Http404
from django.urls import reverse
from django.views.generic import TemplateView
from django.templatetags.static import static
from Pieces2x2.models import Piece2x2, TwoSides
from Solutions.models import Solution, P_CORNER, P_BORDER, P_HINTS
from types import SimpleNamespace

TEMPLATE_VIEW = 'solutions/show.dtl'


class ShowView(TemplateView):

    template_name = TEMPLATE_VIEW

    rot2transform = {
        # rotations are counter-clockwise, but CSS rotation are clockwise
        0: 'rotate(0deg)',
        1: 'rotate(270deg)',
        2: 'rotate(180deg)',
        3: 'rotate(90deg)',
    }

    def _get_2x2(self, nr, note):
        if nr == 0:
            piece = SimpleNamespace()

            piece.is_empty = True
            piece.note = note
        else:
            piece = Piece2x2.objects.get(nr=nr)

            piece.is_empty = False

            piece.img1 = static('pieces/%s.png' % piece.nr1)
            piece.img2 = static('pieces/%s.png' % piece.nr2)
            piece.img3 = static('pieces/%s.png' % piece.nr3)
            piece.img4 = static('pieces/%s.png' % piece.nr4)

            piece.transform1 = self.rot2transform[piece.rot1]
            piece.transform2 = self.rot2transform[piece.rot2]
            piece.transform3 = self.rot2transform[piece.rot3]
            piece.transform4 = self.rot2transform[piece.rot4]

        return piece

    def _fill_sol(self, sol):
        sol.p2x2s = list()
        for nr in range(1, 64+1):
            field_nr = 'nr%s' % nr
            field_note = 'note%s' % nr

            p2x2 = self._get_2x2(getattr(sol, field_nr), getattr(sol, field_note))
            sol.p2x2s.append(p2x2)
        # for

        for nr in range(8, 66+1, 8):
            sol.p2x2s[nr - 1].break_after = True
        # for

    def get_context_data(self, **kwargs):
        """ called by the template system to get the context data for the template """
        context = super().get_context_data(**kwargs)

        try:
            nr = int(kwargs['nr'][:10])      # afkappen voor de veiligheid
        except ValueError:
            raise Http404('Not found')

        context['solution'] = sol = Solution.objects.get(nr=nr)
        self._fill_sol(sol)

        if nr > 1000:
            context['url_prev1000'] = reverse('Solutions:show', kwargs={'nr': nr-1000})
        if nr > 100:
            context['url_prev100'] = reverse('Solutions:show', kwargs={'nr': nr-100})
        if nr > 10:
            context['url_prev10'] = reverse('Solutions:show', kwargs={'nr': nr-10})
        if nr > 1:
            context['url_prev1'] = reverse('Solutions:show', kwargs={'nr': nr-1})
        context['url_next1'] = reverse('Solutions:show', kwargs={'nr': nr+1})
        context['url_next10'] = reverse('Solutions:show', kwargs={'nr': nr+10})
        context['url_next100'] = reverse('Solutions:show', kwargs={'nr': nr+100})
        context['url_next1000'] = reverse('Solutions:show', kwargs={'nr': nr+1000})

        return context

# end of file
