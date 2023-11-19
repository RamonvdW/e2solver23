# -*- coding: utf-8 -*-

#  Copyright (c) 2023 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.http import Http404
from django.urls import reverse
from django.views.generic import TemplateView
from django.templatetags.static import static
from Pieces2x2.models import Piece2x2
from Solutions.models import Solution, Solution4x4, Solution6x6
from types import SimpleNamespace

TEMPLATE_VIEW = 'solutions/show.dtl'

rot2transform = {
    # rotations are counter-clockwise, but CSS rotation are clockwise
    0: 'rotate(0deg)',
    1: 'rotate(270deg)',
    2: 'rotate(180deg)',
    3: 'rotate(90deg)',
}


def _get_2x2(nr, note):
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

        piece.transform1 = rot2transform[piece.rot1]
        piece.transform2 = rot2transform[piece.rot2]
        piece.transform3 = rot2transform[piece.rot3]
        piece.transform4 = rot2transform[piece.rot4]

    return piece


def _fill_sol(sol):
    sol.p2x2s = list()
    for nr in range(1, 64 + 1):
        field_nr = 'nr%s' % nr
        field_note = 'note%s' % nr

        p2x2 = _get_2x2(getattr(sol, field_nr), getattr(sol, field_note))
        sol.p2x2s.append(p2x2)
    # for

    for nr in range(8, 66 + 1, 8):
        sol.p2x2s[nr - 1].break_after = True
    # for


class ShowView(TemplateView):

    template_name = TEMPLATE_VIEW

    def get_context_data(self, **kwargs):
        """ called by the template system to get the context data for the template """
        context = super().get_context_data(**kwargs)

        try:
            nr = int(kwargs['nr'][:10])      # afkappen voor de veiligheid
        except ValueError:
            raise Http404('Not found')

        context['solution'] = sol = Solution.objects.get(nr=nr)
        _fill_sol(sol)

        if nr > 100:
            context['url_prev100'] = reverse('Solutions:show', kwargs={'nr': nr-100})
        if nr > 10:
            context['url_prev10'] = reverse('Solutions:show', kwargs={'nr': nr-10})
        if nr > 1:
            context['url_prev1'] = reverse('Solutions:show', kwargs={'nr': nr-1})
        context['url_next1'] = reverse('Solutions:show', kwargs={'nr': nr+1})
        context['url_next10'] = reverse('Solutions:show', kwargs={'nr': nr+10})
        context['url_next100'] = reverse('Solutions:show', kwargs={'nr': nr+100})

        context['url_auto'] = reverse('Solutions:auto-show')

        context['title'] = 'Solution'

        return context


class Show4x4View(TemplateView):

    template_name = TEMPLATE_VIEW

    def get_context_data(self, **kwargs):
        """ called by the template system to get the context data for the template """
        context = super().get_context_data(**kwargs)

        try:
            nr = int(kwargs['nr'][:10])      # afkappen voor de veiligheid
        except ValueError:
            raise Http404('Not found')

        context['solution'] = sol = Solution4x4.objects.get(nr=nr)
        for nr in range(1, 64 + 1):
            # add the missing pieces
            if nr not in (19, 20, 21, 22,
                          27, 28, 29, 30,
                          35, 36, 37, 38,
                          43, 44, 45, 46):
                nr_str = 'nr%s' % nr
                setattr(sol, nr_str, 0)
        # for
        _fill_sol(sol)

        nr = sol.nr
        if nr > 100:
            context['url_prev100'] = reverse('Solutions:show-4x4', kwargs={'nr': nr-100})
        if nr > 10:
            context['url_prev10'] = reverse('Solutions:show-4x4', kwargs={'nr': nr-10})
        if nr > 1:
            context['url_prev1'] = reverse('Solutions:show-4x4', kwargs={'nr': nr-1})
        context['url_next1'] = reverse('Solutions:show-4x4', kwargs={'nr': nr+1})
        context['url_next10'] = reverse('Solutions:show-4x4', kwargs={'nr': nr+10})
        context['url_next100'] = reverse('Solutions:show-4x4', kwargs={'nr': nr+100})

        context['url_auto'] = reverse('Solutions:auto-show-4x4')

        context['title'] = 'Solution 4x4'

        return context


class Show6x6View(TemplateView):

    template_name = TEMPLATE_VIEW

    def get_context_data(self, **kwargs):
        """ called by the template system to get the context data for the template """
        context = super().get_context_data(**kwargs)

        try:
            nr = int(kwargs['nr'][:10])      # afkappen voor de veiligheid
        except ValueError:
            raise Http404('Not found')

        context['solution'] = sol = Solution6x6.objects.get(nr=nr)
        for nr in range(1, 64 + 1):
            # add the missing pieces
            if nr in (1, 2, 3, 4, 5, 6, 7, 8,
                      9, 16,
                      17, 24,
                      25, 32,
                      33, 40,
                      41, 48,
                      49, 56,
                      57, 58, 59, 60, 61, 62, 63, 64):
                nr_str = 'nr%s' % nr
                setattr(sol, nr_str, 0)
        # for
        _fill_sol(sol)

        context['based_on'] = '4x4 nr %s' % sol.based_on_4x4

        nr = sol.nr
        if nr > 100:
            context['url_prev100'] = reverse('Solutions:show-6x6', kwargs={'nr': nr-100})
        if nr > 10:
            context['url_prev10'] = reverse('Solutions:show-6x6', kwargs={'nr': nr-10})
        if nr > 1:
            context['url_prev1'] = reverse('Solutions:show-6x6', kwargs={'nr': nr-1})
        context['url_next1'] = reverse('Solutions:show-6x6', kwargs={'nr': nr+1})
        context['url_next10'] = reverse('Solutions:show-6x6', kwargs={'nr': nr+10})
        context['url_next100'] = reverse('Solutions:show-6x6', kwargs={'nr': nr+100})

        context['url_auto'] = reverse('Solutions:auto-show-6x6')

        context['title'] = 'Solution 6x6'

        return context


class ShowAutoView(TemplateView):

    template_name = TEMPLATE_VIEW

    def get_context_data(self, **kwargs):
        """ called by the template system to get the context data for the template """
        context = super().get_context_data(**kwargs)

        sol = Solution.objects.order_by('-nr').first()       # highest first
        if sol:
            context['solution'] = sol
            _fill_sol(sol)

        context['auto_reload'] = True

        nr = sol.nr
        if nr > 100:
            context['url_prev100'] = reverse('Solutions:show', kwargs={'nr': nr-100})
        if nr > 10:
            context['url_prev10'] = reverse('Solutions:show', kwargs={'nr': nr-10})
        if nr > 1:
            context['url_prev1'] = reverse('Solutions:show', kwargs={'nr': nr-1})

        context['title'] = 'Solution'

        return context


class Show4x4AutoView(TemplateView):

    template_name = TEMPLATE_VIEW

    def get_context_data(self, **kwargs):
        """ called by the template system to get the context data for the template """
        context = super().get_context_data(**kwargs)

        sol = Solution4x4.objects.order_by('-nr').first()       # highest first
        if sol:
            for nr in range(1, 64+1):
                # add the missing pieces
                if nr not in (19, 20, 21, 22,
                              27, 28, 29, 30,
                              35, 36, 37, 38,
                              43, 44, 45, 46):
                    nr_str = 'nr%s' % nr
                    setattr(sol, nr_str, 0)
            # for
            context['solution'] = sol
            _fill_sol(sol)

        context['auto_reload'] = True

        nr = sol.nr
        if nr > 100:
            context['url_prev100'] = reverse('Solutions:show-4x4', kwargs={'nr': nr-100})
        if nr > 10:
            context['url_prev10'] = reverse('Solutions:show-4x4', kwargs={'nr': nr-10})
        if nr > 1:
            context['url_prev1'] = reverse('Solutions:show-4x4', kwargs={'nr': nr-1})

        context['title'] = 'Solution 4x4'

        return context


class Show6x6AutoView(TemplateView):

    template_name = TEMPLATE_VIEW

    def get_context_data(self, **kwargs):
        """ called by the template system to get the context data for the template """
        context = super().get_context_data(**kwargs)

        sol = Solution6x6.objects.order_by('-nr').first()       # highest first
        if sol:
            for nr in range(1, 64+1):
                # add the missing pieces
                if nr in (1, 2, 3, 4, 5, 6, 7, 8,
                          9, 16,
                          17, 24,
                          25, 32,
                          33, 40,
                          41, 48,
                          49, 56,
                          57, 58, 59, 60, 61, 62, 63, 64):
                    nr_str = 'nr%s' % nr
                    setattr(sol, nr_str, 0)
            # for
            context['solution'] = sol
            _fill_sol(sol)

        context['auto_reload'] = True
        context['based_on'] = '4x4 nr %s' % sol.based_on_4x4

        nr = sol.nr
        if nr > 100:
            context['url_prev100'] = reverse('Solutions:show-6x6', kwargs={'nr': nr-100})
        if nr > 10:
            context['url_prev10'] = reverse('Solutions:show-6x6', kwargs={'nr': nr-10})
        if nr > 1:
            context['url_prev1'] = reverse('Solutions:show-6x6', kwargs={'nr': nr-1})

        context['title'] = 'Solution 6x6'

        return context


# end of file
