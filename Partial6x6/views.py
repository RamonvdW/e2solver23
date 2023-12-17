# -*- coding: utf-8 -*-

#  Copyright (c) 2023 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.http import Http404
from django.urls import reverse
from django.views.generic import TemplateView
from django.templatetags.static import static
from BasePieces.models import BasePiece
from BasePieces.hints import HINT_NRS, CENTER_NR
from Pieces2x2.models import Piece2x2
from Partial6x6.models import Quart6, Partial6x6, NRS_PARTIAL_6X6
from types import SimpleNamespace

TEMPLATE_VIEW = 'partial6x6/show.dtl'

rot2transform = {
    # rotations are counter-clockwise, but CSS rotation are clockwise
    0: 'rotate(0deg)',
    1: 'rotate(270deg)',
    2: 'rotate(180deg)',
    3: 'rotate(90deg)',
}


nr2img = dict()           # [base_nr] = image path
nr2piece2x2 = dict()      # [nr] = Piece2x2


def _get_2x2(nr, note):
    if nr == 0:
        piece = SimpleNamespace()

        piece.is_empty = True
        if note:
            piece.note = '2x2: ' + note.replace(' ', '\n').replace(')\n', ')\n1x1: ').replace('max\n', 'max ').replace(',', ', ')
    else:
        if len(nr2img) == 0:
            for base_nr in range(1, 256+1):
                nr2img[base_nr] = static('pieces/%s.png' % base_nr)
            # for

        try:
            piece = nr2piece2x2[nr]
        except KeyError:
            piece = Piece2x2.objects.get(nr=nr)
            piece.is_empty = False

            piece.img1 = nr2img[piece.nr1]
            piece.img2 = nr2img[piece.nr2]
            piece.img3 = nr2img[piece.nr3]
            piece.img4 = nr2img[piece.nr4]

            piece.transform1 = rot2transform[piece.rot1]
            piece.transform2 = rot2transform[piece.rot2]
            piece.transform3 = rot2transform[piece.rot3]
            piece.transform4 = rot2transform[piece.rot4]

            nr2piece2x2[nr] = piece

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

    sol.nr = sol.pk

    for nr in range(1, 64 + 1):
        # add the missing pieces
        if nr not in NRS_PARTIAL_6X6:
            nr_str = 'nr%s' % nr
            setattr(sol, nr_str, 0)
    # for

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

    hint_nrs = list()
    for nr in range(1, 64 + 1):
        field_nr = 'nr%s' % nr
        field_note = 'note%s' % nr

        p2x2 = _get_2x2(getattr(sol, field_nr), getattr(sol, field_note, None))
        sol.p2x2s.append(p2x2)

        if p2x2.is_empty:
            p2x2.nr = nr
        else:
            for base_nr in (p2x2.nr1, p2x2.nr2, p2x2.nr3, p2x2.nr4):
                if base_nr in HINT_NRS or base_nr == CENTER_NR:
                    hint_nrs.append(base_nr)
            # for

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

    sol.s1_counts = list()
    for s1, s_max in s1_max.items():
        s_open = s1_open[s1]
        s_used = s1_used[s1]
        s_left = s_max - s_used - s_open*2
        tup = (s1, s_open, s_used, s_max, s_left)
        sol.s1_counts.append(tup)
    # for
    sol.s1_counts.sort()

    hint_nrs.sort()
    sol.hint_nrs = ", ".join([str(nr) for nr in hint_nrs])

    for nr in range(8, 66 + 1, 8):
        sol.p2x2s[nr - 1].break_after = True
    # for


class ShowPart6x6View(TemplateView):

    template_name = TEMPLATE_VIEW

    def get_context_data(self, **kwargs):
        """ called by the template system to get the context data for the template """
        context = super().get_context_data(**kwargs)

        try:
            nr = int(kwargs['nr'][:10])      # afkappen voor de veiligheid
        except ValueError:
            raise Http404('Not found')

        sol = Partial6x6.objects.get(pk=nr)
        context['solution'] = sol

        _fill_sol(sol)

        context['based_on'] = '4x4 nr %s' % sol.based_on_4x4

        next_sol = Partial6x6.objects.filter(pk__gt=sol.pk).order_by('pk').first()
        prev_sol = Partial6x6.objects.filter(pk__lt=sol.pk).order_by('pk').last()
        if next_sol:
            context['url_next'] = reverse('Partial6x6:show', kwargs={'nr': next_sol.pk})
        if prev_sol:
            context['url_prev'] = reverse('Partial6x6:show', kwargs={'nr': prev_sol.pk})

        context['url_auto'] = reverse('Partial6x6:auto-show-6x6')

        context['title'] = 'Partial6x6'

        return context


class ShowPart6x6AutoView(TemplateView):

    template_name = TEMPLATE_VIEW

    def get_context_data(self, **kwargs):
        """ called by the template system to get the context data for the template """
        context = super().get_context_data(**kwargs)

        try:
            sol = Partial6x6.objects.latest('pk')
        except Partial6x6.DoesNotExist:
            sol = None

        if sol:
            context['solution'] = sol
            _fill_sol(sol)

            context['based_on'] = '4x4 nr %s' % sol.based_on_4x4

            next_sol = Partial6x6.objects.filter(pk__gt=sol.pk).order_by('pk').first()
            prev_sol = Partial6x6.objects.filter(pk__lt=sol.pk).order_by('pk').last()
            if next_sol:
                context['url_next'] = reverse('Partial6x6:show', kwargs={'nr': next_sol.pk})
            if prev_sol:
                context['url_prev'] = reverse('Partial6x6:show', kwargs={'nr': prev_sol.pk})

        context['auto_reload'] = True

        context['title'] = 'Partial6x6'

        return context


class Quart6View(TemplateView):

    template_name = TEMPLATE_VIEW

    def get_context_data(self, **kwargs):
        """ called by the template system to get the context data for the template """
        context = super().get_context_data(**kwargs)

        try:
            nr = int(kwargs['nr'][:10])      # afkappen voor de veiligheid
        except ValueError:
            raise Http404('Not found')

        quart = Quart6.objects.filter(pk=nr).first()       # highest first
        if quart:
            if quart.type == 10:
                nrs = (18, 10, 11)
            elif quart.type == 15:
                nrs = (14, 15, 23)
            elif quart.type == 50:
                nrs = (51, 50, 42)
            elif quart.type == 55:
                nrs = (47, 55, 54)
            else:
                nrs = (1, 2, 3)

            sol = SimpleNamespace(
                        pk=quart.pk,
                        nr=quart.pk,
                        based_on_4x4=quart.based_on_4x4)

            setattr(sol, 'nr%s' % nrs[0], quart.p1)
            setattr(sol, 'nr%s' % nrs[1], quart.c1)
            setattr(sol, 'nr%s' % nrs[2], quart.p2)

            for nr in range(1, 64+1):
                nr_str = 'nr%s' % nr
                if getattr(sol, nr_str, None) is None:
                    setattr(sol, nr_str, 0)
            # for

            context['solution'] = sol
            _fill_sol(sol)

            context['based_on'] = '4x4 nr %s' % quart.based_on_4x4

            next_sol = Quart6.objects.filter(pk__gt=quart.pk).order_by('pk').first()
            prev_sol = Quart6.objects.filter(pk__lt=quart.pk).order_by('pk').last()
            if next_sol:
                context['url_next'] = reverse('Partial6x6:show-quart6', kwargs={'nr': next_sol.pk})
            if prev_sol:
                context['url_prev'] = reverse('Partial6x6:show-quart6', kwargs={'nr': prev_sol.pk})

        context['url_auto'] = reverse('Partial6x6:auto-show-quart6')

        context['title'] = 'Quart6'

        return context


class Quart6AutoView(TemplateView):

    template_name = TEMPLATE_VIEW

    def get_context_data(self, **kwargs):
        """ called by the template system to get the context data for the template """
        context = super().get_context_data(**kwargs)

        try:
            quart = Quart6.objects.latest('pk')
        except Quart6.DoesNotExist:
            quart = None

        if quart:
            if quart.type == 10:
                nrs = (18, 10, 11)
            elif quart.type == 15:
                nrs = (14, 15, 23)
            elif quart.type == 50:
                nrs = (51, 50, 42)
            elif quart.type == 55:
                nrs = (47, 55, 54)
            else:
                nrs = (1, 2, 3)

            sol = SimpleNamespace(
                        pk=quart.pk,
                        nr=quart.pk,
                        based_on_4x4=quart.based_on_4x4)

            setattr(sol, 'nr%s' % nrs[0], quart.p1)
            setattr(sol, 'nr%s' % nrs[1], quart.c1)
            setattr(sol, 'nr%s' % nrs[2], quart.p2)

            for nr in range(1, 64+1):
                nr_str = 'nr%s' % nr
                if getattr(sol, nr_str, None) is None:
                    setattr(sol, nr_str, 0)
            # for

            context['solution'] = sol
            _fill_sol(sol)

            context['based_on'] = '4x4 nr %s' % quart.based_on_4x4

            next_sol = Quart6.objects.filter(pk__gt=quart.pk).order_by('pk').first()
            prev_sol = Quart6.objects.filter(pk__lt=quart.pk).order_by('pk').last()
            if next_sol:
                context['url_next'] = reverse('Partial6x6:show-quart6', kwargs={'nr': next_sol.pk})
            if prev_sol:
                context['url_prev'] = reverse('Partial6x6:show-quart6', kwargs={'nr': prev_sol.pk})

        context['auto_reload'] = True

        context['title'] = 'Quart6'

        return context

# end of file
