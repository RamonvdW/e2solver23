# -*- coding: utf-8 -*-

#  Copyright (c) 2023-2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.http import Http404
from django.urls import reverse
from django.views.generic import TemplateView
from django.templatetags.static import static
from BasePieces.models import BasePiece
from BasePieces.pieces_1x1 import INTERNAL_BORDER_SIDES
from Pieces2x2.models import Piece2x2, TwoSide
from Solutions.models import Solution8x8
from WorkQueue.models import ProcessorUsedPieces
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
        piece = SimpleNamespace(nr=0, is_empty=True)
        if note:
            piece.note = '2x2: ' + note.replace(' ', '\n').replace(')\n', ')\n1x1: ').replace('max\n', 'max ').replace(',', ', ')
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


def _sol_add_stats_1x1(sol, neighbours):
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

        p2x2 = _get_2x2(getattr(sol, field_nr), getattr(sol, field_note, None))

        if not p2x2.is_empty:
            side_is_open = [None, ]
            for other_nr in neighbours[nr]:
                if other_nr > 0:
                    field_nr = 'nr%s' % other_nr
                    check_nr = getattr(sol, field_nr)
                else:
                    check_nr = 0
                side_is_open.append(check_nr == 0)
            # for

            for base_nr, base_rot, out_sides, in_sides in (
                    (p2x2.nr1, p2x2.rot1, (1, 4), (2, 3)),
                    (p2x2.nr2, p2x2.rot2, (1, 2), (3, 4)),
                    (p2x2.nr3, p2x2.rot3, (3, 4), (1, 2)),
                    (p2x2.nr4, p2x2.rot4, (2, 3), (1, 4))):

                base = nr2base[base_nr]
                for side in in_sides:
                    s1 = base.get_side(side, base_rot)
                    s1_used[s1] += 1
                # for
                for side in out_sides:
                    s1 = base.get_side(side, base_rot)
                    if side_is_open[side]:
                        s1_open[s1] += 1
                    else:
                        s1_used[s1] += 1
                # for
            # for
    # for

    sol.s1_counts = []
    for s1, s_max in s1_max.items():
        s_open = s1_open[s1]
        s_used = s1_used[s1]

        if s1 == 'X':
            # special handling for the border
            s_used = s_open
            s_open = 64 - s_open
            s_left = s_open
        else:
            s_left = s_max - s_used - s_open
        s_trouble = s_left < s_open
        tup = (s1, s_open, s_used, s_max, s_left, s_trouble)
        sol.s1_counts.append(tup)
    # for
    sol.s1_counts.sort()


def _sol_add_stats_2x2(sol: Solution8x8, neighbours):

    empty_locs = []
    unused_nrs = list(range(1, 256+1))

    for p in sol.p2x2s:
        if p.is_empty:
            empty_locs.append(p.loc)
        else:
            for nr in (p.nr1, p.nr2, p.nr3, p.nr4):
                try:
                    unused_nrs.remove(nr)
                except ValueError:
                    print('Double used nr: %s' % nr)
    # for
    sol.unused = unused_nrs

    # print('empty_locs: %s' % repr(empty_locs))
    # print('unused_nrs: %s' % repr(unused_nrs))

    s2_open = dict()        # [side_nr] = count
    for p in sol.p2x2s:
        if not p.is_empty:
            nrs = neighbours[p.loc]
            side_nrs = []

            # side1
            if nrs[0] in empty_locs:
                side_nrs.append(p.side1)

            # side2
            if nrs[1] in empty_locs:
                side_nrs.append(p.side2)

            # side3
            if nrs[2] in empty_locs:
                side_nrs.append(p.side3)

            # side4
            if nrs[3] in empty_locs:
                side_nrs.append(p.side4)

            for side_nr in side_nrs:
                try:
                    s2_open[side_nr] += 1
                except KeyError:
                    s2_open[side_nr] = 1
    # for

    two2nr = dict()                 # [two sides] = two side nr
    side_nr_is_border = dict()      # [two side nr] = True/False
    side_nr2reverse = dict()        # [two side nr] = reverse two side nr
    for two in TwoSide.objects.all():
        two2nr[two.two_sides] = two.nr
        side_nr_is_border[two.nr] = ((two.two_sides[0] in INTERNAL_BORDER_SIDES) or
                                     (two.two_sides[1] in INTERNAL_BORDER_SIDES))
    # for
    for two_sides, nr in two2nr.items():
        two_rev = two_sides[1] + two_sides[0]
        rev_nr = two2nr[two_rev]
        side_nr2reverse[nr] = rev_nr
    # for

    #side_border = two2nr['XX']

    qset = Piece2x2.objects.filter(nr1__in=unused_nrs, nr2__in=unused_nrs, nr3__in=unused_nrs, nr4__in=unused_nrs)

    sol.s2_counts = []
    for side_nr, c_open in s2_open.items():
        is_border = side_nr_is_border[side_nr]
        rev_nr = side_nr2reverse[side_nr]

        # all rotation variants exist, so just count 1 side
        c_left = qset.filter(side1=rev_nr).count()  #, side3=side_border).count()

        tup = (side_nr, c_open, c_left, is_border)
        sol.s2_counts.append(tup)
    # for

    sol.s2_counts.sort()


def _fill_sol(sol):
    sol.nr = sol.pk

    neighbours = _calc_neighbours()

    _sol_add_stats_1x1(sol, neighbours)

    sol.p2x2s = []
    for nr in range(1, 64 + 1):
        field_nr = 'nr%s' % nr
        field_note = 'note%s' % nr

        p2x2 = _get_2x2(getattr(sol, field_nr), getattr(sol, field_note, None))
        p2x2.loc = nr
        sol.p2x2s.append(p2x2)
    # for

    _sol_add_stats_2x2(sol, neighbours)

    for nr in range(8, 66 + 1, 8):
        sol.p2x2s[nr - 1].break_after = True
    # for


def _analyze_chains(sol):

    two2nr = dict()                 # [two sides] = two side nr
    side_nr2reverse = dict()        # [two side nr] = reverse two side nr
    for two in TwoSide.objects.all():
        two2nr[two.two_sides] = two.nr
    # for
    for two_sides, nr in two2nr.items():
        two_rev = two_sides[1] + two_sides[0]
        rev_nr = two2nr[two_rev]
        side_nr2reverse[nr] = rev_nr
    # for

    qset = Piece2x2.objects.filter(nr1__in=sol.unused, nr2__in=sol.unused, nr3__in=sol.unused, nr4__in=sol.unused)

    chains = []

    # left to right
    for nr1, nr8 in ((9, 16), (17, 24), (25, 32), (33, 40), (41, 48), (49, 56)):
        # 1
        p1 = Piece2x2.objects.get(nr=getattr(sol, 'nr%s' % nr1))
        p2_exp_s4 = side_nr2reverse[p1.side2]

        # 2
        p2_sides2 = list(qset.filter(side4=p2_exp_s4).distinct('side2').values_list('side2', flat=True))
        p3_exp_s4 = [side_nr2reverse[s] for s in p2_sides2]

        # 3
        p3_sides2 = list(qset.filter(side4__in=p3_exp_s4).distinct('side2').values_list('side2', flat=True))
        p4_exp_s4 = [side_nr2reverse[s] for s in p3_sides2]

        # 4
        p4_sides2 = list(qset.filter(side4__in=p4_exp_s4).distinct('side2').values_list('side2', flat=True))
        p5_exp_s4 = [side_nr2reverse[s] for s in p4_sides2]

        # 8
        p8 = Piece2x2.objects.get(nr=getattr(sol, 'nr%s' % nr8))
        p7_exp_s2 = side_nr2reverse[p8.side4]

        # 7
        p7_sides4 = list(qset.filter(side2=p7_exp_s2).distinct('side4').values_list('side4', flat=True))
        p6_exp_s2 = [side_nr2reverse[s] for s in p7_sides4]

        # 6
        p6_sides4 = list(qset.filter(side2__in=p6_exp_s2).distinct('side4').values_list('side4', flat=True))
        p5_exp_s2 = [side_nr2reverse[s] for s in p6_sides4]

        # 4
        p5_count = qset.filter(side2__in=p5_exp_s2, side4__in=p5_exp_s4).count()

        chain = (nr1, nr8, len(p2_sides2), len(p3_sides2), len(p4_sides2), p5_count, len(p6_sides4), len(p7_sides4))
        chains.append(chain)
    # for

    return chains


class ShowView(TemplateView):

    template_name = TEMPLATE_VIEW

    def get_context_data(self, **kwargs):
        """ called by the template system to get the context data for the template """
        context = super().get_context_data(**kwargs)

        try:
            nr = int(kwargs['nr'][:10])      # afkappen voor de veiligheid
        except ValueError:
            raise Http404('Not found')

        context['solution'] = sol = Solution8x8.objects.get(pk=nr)
        _fill_sol(sol)
        # context['chains'] = _analyze_chains(sol)

        context['based_on'] = '6x6 nr %s' % sol.based_on_6x6

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


class ShowAutoView(TemplateView):

    template_name = TEMPLATE_VIEW

    def get_context_data(self, **kwargs):
        """ called by the template system to get the context data for the template """
        context = super().get_context_data(**kwargs)

        sol = Solution8x8.objects.order_by('pk').last()
        if sol:
            context['solution'] = sol
            _fill_sol(sol)
            # context['chains'] = _analyze_chains(sol)

            #context['based_on'] = '6x6 nr %s' % sol.based_on_6x6

            nr = sol.pk
            if nr > 100:
                context['url_prev100'] = reverse('Solutions:show', kwargs={'nr': nr-100})
            if nr > 10:
                context['url_prev10'] = reverse('Solutions:show', kwargs={'nr': nr-10})
            if nr > 1:
                context['url_prev1'] = reverse('Solutions:show', kwargs={'nr': nr-1})

        context['auto_reload'] = True

        context['title'] = 'Solution'

        return context


class ShowWorkView(TemplateView):

    template_name = TEMPLATE_VIEW

    def get_context_data(self, **kwargs):
        """ called by the template system to get the context data for the template """
        context = super().get_context_data(**kwargs)

        try:
            used = ProcessorUsedPieces.objects.get(processor=kwargs['processor'])
        except ProcessorUsedPieces.DoesNotExist:
            raise Http404('Used pieces not found')

        sol = Solution8x8()

        for loc in range(1, 64+1):
            loc_str = 'loc%s' % loc
            p2x2_nr = getattr(used, loc_str)

            nr_str = 'nr%s' % loc
            setattr(sol, nr_str, p2x2_nr)
        # for

        context['solution'] = sol
        _fill_sol(sol)

        context['title'] = 'Work %s' % used.processor

        return context


# end of file
