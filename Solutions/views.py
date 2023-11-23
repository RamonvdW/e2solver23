# -*- coding: utf-8 -*-

#  Copyright (c) 2023 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.http import Http404
from django.urls import reverse
from django.views.generic import TemplateView
from django.templatetags.static import static
from BasePieces.models import BasePiece
from Pieces2x2.models import Piece2x2, TwoSides
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
        if note:
            piece.note = '2x2: ' + note.replace(' ', '\n1x1: {').replace(',', ', ')
            if ',' in note:
                piece.note += '}'
            else:
                piece.note = piece.note.replace('{', '')
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


def _calc_neighbours():
    neighbours = dict()

    for nr in range(1, 64+1):
        neighbours[nr] = (nr - 8, nr + 1, nr + 8, nr - 1)       # side 1, 2, 3, 4
    # for

    # redo the corners
    neighbours[1] = (0, 1 + 1, 1 + 8, 0)
    neighbours[8] = (0, 0, 8 + 8, 8 - 1)
    neighbours[57] = (57 - 8, 57 + 1, 0, 0)
    neighbours[64] = (64 - 8, 0, 0, 64 - 1)

    # redo for the borders
    for nr in range(2, 7+1):
        neighbours[nr] = (0, nr + 1, nr + 8, nr - 1)
    for nr in range(9, 49+1, 8):
        neighbours[nr] = (nr - 8, nr + 1, nr + 8, 0)
    for nr in range(16, 56+1, 8):
        neighbours[nr] = (nr - 8, 0, nr + 8, nr - 1)
    for nr in range(58, 63+1):
        neighbours[nr] = (nr - 8, nr + 1, 0, nr - 1)

    return neighbours


def _fill_sol(sol):
    neighbours = _calc_neighbours()

    sol.p2x2s = list()

    s1_open = dict()         # ["side"] = count
    s1_used = dict()         # ["side"] = count
    s1_max = dict()          # ["side"] = count

    nr2base = dict()
    for base in BasePiece.objects.all():
        nr2base[base.nr] = base
        for side in (base.side1, base.side2, base.side3, base.side4):
            try:
                s1_max[side] += 1
            except KeyError:
                s1_max[side] = 1
                s1_used[side] = 0
                s1_open[side] = 0
        # for
    # for

    for nr in range(1, 64 + 1):
        field_nr = 'nr%s' % nr
        field_note = 'note%s' % nr

        p2x2 = _get_2x2(getattr(sol, field_nr), getattr(sol, field_note))
        sol.p2x2s.append(p2x2)

        # side_is_open = [None, ]
        # for other_nr in neighbours[nr]:
        #     if other_nr > 0:
        #         field_nr = 'nr%s' % other_nr
        #         check_nr = getattr(sol, field_nr)
        #     else:
        #         check_nr = 0
        #     side_is_open.append(check_nr == 0)
        # # for
        #
        # if not p2x2.is_empty:
        #     for base_nr, base_rot, out_sides, in_sides in (
        #             (p2x2.nr1, p2x2.rot1, (1, 4), (2, 3)),
        #             (p2x2.nr2, p2x2.rot2, (1, 2), (3, 4)),
        #             (p2x2.nr3, p2x2.rot3, (3, 4), (1, 2)),
        #             (p2x2.nr4, p2x2.rot4, (2, 3), (1, 4))):
        #
        #         base = nr2base[base_nr]
        #         for side in in_sides:
        #             s1 = base.get_side(side, base_rot)
        #             s1_used[s1] += 1
        #         # for
        #         for side in out_sides:
        #             s1 = base.get_side(side, base_rot)
        #             if side_is_open[side]:
        #                 s1_open[s1] += 1
        #             else:
        #                 s1_used[s1] += 1
        #         # for
        #     # for
    # for

    # sol.s1_counts = list()
    # for s1, s_max in s1_max.items():
    #     s_open = s1_open[s1]
    #     s_used = s1_used[s1]
    #     s_left = s_max - s_used - s_open*2
    #     tup = (s1, s_open, s_used, s_max, s_left)
    #     sol.s1_counts.append(tup)
    # # for
    # sol.s1_counts.sort()

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

        context['solution'] = sol = Solution4x4.objects.get(pk=nr)
        sol.nr = sol.pk

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

        context['solution'] = sol = Solution6x6.objects.get(pk=nr)
        sol.nr = sol.pk

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

        pks = list(Solution6x6.objects.filter(based_on_4x4=sol.based_on_4x4).order_by('pk').values_list('pk', flat=True))
        idx = pks.index(sol.pk)
        if idx > 0:
            context['url_prev4x4'] = reverse('Solutions:show-6x6', kwargs={'nr': pks[idx-1]})
        if idx < len(pks) - 1:
            context['url_next4x4'] = reverse('Solutions:show-6x6', kwargs={'nr': pks[idx+1]})

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

        sol = Solution4x4.objects.order_by('-pk').first()       # highest first
        if sol:
            sol.nr = sol.pk
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

        sol = Solution6x6.objects.order_by('-pk').first()       # highest first
        if sol:
            sol.nr = sol.pk
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

        pks = list(Solution6x6.objects.filter(based_on_4x4=sol.based_on_4x4).order_by('pk').values_list('pk', flat=True))
        idx = pks.index(sol.pk)
        if idx > 0:
            context['url_prev4x4'] = reverse('Solutions:show-6x6', kwargs={'nr': pks[idx-1]})

        context['title'] = 'Solution 6x6'

        return context


# end of file
