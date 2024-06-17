# -*- coding: utf-8 -*-

#  Copyright (c) 2023-2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.http import Http404
from django.urls import reverse
from django.utils import timezone
from django.views.generic import TemplateView
from django.templatetags.static import static
from Pieces2x2.models import Piece2x2, TwoSideOptions, EvalProgress
from Pieces2x2.helpers import calc_segment
from Ring1.models import Ring1
from WorkQueue.models import Work, ProcessorUsedPieces
from types import SimpleNamespace
import time

TEMPLATE_SHOW = 'pieces2x2/show.dtl'
TEMPLATE_OPTIONS = 'pieces2x2/options.dtl'
TEMPLATE_OPTIONS_LIST = 'pieces2x2/options-list.dtl'

piece2x2_cache = dict()

twoside_count_cache = dict()    # [processor] = (count, stamp)

ring1_seed_cache = dict()       # [ring1_nr] = seed


class ShowView(TemplateView):

    template_name = TEMPLATE_SHOW

    rot2transform = {
        # rotations are counter-clockwise, but CSS rotation are clockwise
        0: 'rotate(0deg)',
        1: 'rotate(270deg)',
        2: 'rotate(180deg)',
        3: 'rotate(90deg)',
    }

    def get_context_data(self, **kwargs):
        """ called by the template system to get the context data for the template """
        context = super().get_context_data(**kwargs)

        try:
            nr = int(kwargs['nr'][:8])      # afkappen voor de veiligheid
        except ValueError:
            raise Http404('Not found')

        # maak blokjes van 5 rijen van 4 breed = 20
        nr = int((nr - 1) / 20)
        nr = 1 + nr * 20

        if nr > 1000:
            context['url_prev1000'] = reverse('Pieces2x2:show', kwargs={'nr': nr-1000})
        if nr > 100:
            context['url_prev100'] = reverse('Pieces2x2:show', kwargs={'nr': nr-100})
        if nr > 20:
            context['url_prev20'] = reverse('Pieces2x2:show', kwargs={'nr': nr-20})
        context['url_next20'] = reverse('Pieces2x2:show', kwargs={'nr': nr+20})
        context['url_next100'] = reverse('Pieces2x2:show', kwargs={'nr': nr+100})
        context['url_next1000'] = reverse('Pieces2x2:show', kwargs={'nr': nr+1000})

        context['groups'] = groups = []
        group = []
        pieces = Piece2x2.objects.filter(nr__gte=nr, nr__lt=nr+20).order_by('nr')
        for piece in pieces:
            piece.img1 = static('pieces/%s.png' % piece.nr1)
            piece.img2 = static('pieces/%s.png' % piece.nr2)
            piece.img3 = static('pieces/%s.png' % piece.nr3)
            piece.img4 = static('pieces/%s.png' % piece.nr4)

            piece.transform1 = self.rot2transform[piece.rot1]
            piece.transform2 = self.rot2transform[piece.rot2]
            piece.transform3 = self.rot2transform[piece.rot3]
            piece.transform4 = self.rot2transform[piece.rot4]

            group.append(piece)
            if len(group) == 4:
                groups.append(group)
                group = []
        # for

        if len(group):
            groups.append(group)

        return context


class OptionsView(TemplateView):

    template_name = TEMPLATE_OPTIONS

    @staticmethod
    def _calc_hue(count):
        if count == 289:
            # hanging out at maximum
            return 200  # blue

        # max_count = 289
        # count2hue_multiplier = 120 / max_count
        hue = int(count * (100 / 289))
        return 100 - hue        # low number = green, higher number = red

    @staticmethod
    def _compare_pre(used):
        segment2count = dict()       # [segment] = int
        prev_segment2count = dict()  # [segment] = int
        for segment in range(256):
            segment2count[segment] = 0
            prev_segment2count[segment] = 0
        # for
        for option in TwoSideOptions.objects.filter(processor=used.processor):
            segment2count[option.segment] += 1
        # for
        for option in TwoSideOptions.objects.filter(processor=used.created_from):
            prev_segment2count[option.segment] += 1
        # for

        if used.from_ring1 > 0:
            for segment in (102, 103, 104, 105, 106, 107, 108,
                            10, 11, 12, 13, 14, 15,
                            58, 59, 60, 61, 62, 63,
                            158, 159, 160, 161, 162, 163, 164,
                            9, 17, 25, 33, 41, 49, 57,
                            110, 118, 126, 134, 142, 150,
                            116, 124, 132, 140, 148, 156,
                            16, 24, 32, 40, 48, 56, 64):
                prev_segment2count[segment] = 1

        segments = list(segment2count.keys())
        segments.sort()
        compare = []
        for segment in segments:
            count1 = segment2count[segment]
            count2 = prev_segment2count[segment]
            if count1 != count2:
                tup = (segment, count1, count2, count1 - count2)
                compare.append(tup)
        # for
        return compare

    def _make_squares(self, segment2count, highlight_segments, processor):
        # get segments that are being worked on
        work_segments = list(EvalProgress.objects.filter(processor=processor).values_list('segment', flat=True))

        # initialize matrix
        squares = dict()    # [(x,y)] = SimpleNamespace
        for y in range(16+1):
            transform = ''
            if y & 1 == 1:  # odd row
                transform = 'rotate(90deg)'

            for x in range(16+1):
                squares[(x, y)] = SimpleNamespace(break_after=False, transform=transform, working=False)
            # for
            squares[(16, y)].break_after = True
        # for

        # fill in each loc with surrounding segments
        x = 1
        y = 1
        for loc in range(1, 64+1):
            squares[(x, y)].loc = loc

            segment = calc_segment(loc, 1)
            count = segment2count[segment]
            squares[(x, y-1)].count = count
            squares[(x, y-1)].highlight = segment in highlight_segments
            squares[(x, y-1)].hue = self._calc_hue(count)
            squares[(x, y-1)].working = segment in work_segments

            segment = calc_segment(loc, 2)
            count = segment2count[segment]
            squares[(x+1, y)].count = count
            squares[(x+1, y)].highlight = segment in highlight_segments
            squares[(x+1, y)].hue = self._calc_hue(count)
            squares[(x+1, y)].working = segment in work_segments

            segment = calc_segment(loc, 3)
            count = segment2count[segment]
            squares[(x, y+1)].count = count
            squares[(x, y+1)].highlight = segment in highlight_segments
            squares[(x, y+1)].hue = self._calc_hue(count)
            squares[(x, y+1)].working = segment in work_segments

            segment = calc_segment(loc, 4)
            count = segment2count[segment]
            squares[(x-1, y)].count = count
            squares[(x-1, y)].highlight = segment in highlight_segments
            squares[(x-1, y)].hue = self._calc_hue(count)
            squares[(x-1, y)].working = segment in work_segments

            x += 2
            if x > 16:
                x = 1
                y += 2
        # for

        # pack the matrix into an array
        sq_list = []
        for y in range(16 + 1):
            for x in range(16 + 1):
                square = squares[(x, y)]
                sq_list.append(square)
            # for
        # for

        return sq_list

    @staticmethod
    def _get_segments(progress):
        loc = progress.eval_loc
        if progress.eval_size == 4:
            """
                      s0          s1
                    +----+      +----+
                s2  | p0 |  s3  | p1 |  s4
                    +----+      +----+
                      s5          s6
                    +----+      +----+
                s7  | p2 |  s8  | p3 |  s9
                    +----+      +----+
                     s10         s11
            """
            locs = (loc + 0, loc + 1,
                    loc + 8, loc + 9)

            side_nrs = {0: (0, 3, 5, 2),
                        1: (1, 4, 6, 3),
                        2: (5, 8, 10, 7),
                        3: (6, 9, 11, 8)}

            s_nrs = (3, 5, 6, 8)

        elif progress.eval_size == 9:
            """
                      s0          s1          s2 
                    +----+      +----+      +----+
                s3  | p0 |  s4  | p1 |  s5  | p2 |  s6 
                    +----+      +----+      +----+
                      s7          s8          s9
                    +----+      +----+      +----+
                s10 | p3 |  s11 | p4 |  s12 | p5 |  s13
                    +----+      +----+      +----+
                      s14         s15        s16
                    +----+      +----+      +----+
                s17 | p6 |  s18 | p7 |  s19 | p8 |  s20
                    +----+      +----+      +----+
                      s21         s22         s23
            """
            locs = (loc + 0, loc + 1, loc + 2,
                    loc + 8, loc + 9, loc + 10,
                    loc + 16, loc + 17, loc + 18)

            side_nrs = {0: (0, 4, 7, 3),
                        1: (1, 5, 8, 4),
                        2: (2, 6, 9, 5),
                        3: (7, 11, 14, 10),
                        4: (8, 12, 15, 11),
                        5: (9, 13, 16, 12),
                        6: (14, 18, 21, 17),
                        7: (15, 19, 22, 18),
                        8: (16, 20, 23, 19)}

            s_nrs = (8, 12, 15, 11,
                     4, 5,
                     7, 14,
                     9, 16,
                     18, 19)

        elif progress.eval_size == 16:
            loc = progress.eval_loc
            locs = (loc + 0, loc + 1, loc + 2, loc + 3,
                    loc + 8, loc + 9, loc + 10, loc + 11,
                    loc + 16, loc + 17, loc + 18, loc + 19,
                    loc + 24, loc + 25, loc + 26, loc + 27)

            side_nrs = {0: (0, 5, 9, 4),
                        1: (1, 6, 10, 5),
                        2: (2, 7, 11, 6),
                        3: (3, 8, 12, 7),
                        4: (9, 14, 18, 13),
                        5: (10, 15, 19, 14),
                        6: (11, 16, 20, 15),
                        7: (12, 17, 21, 16),
                        8: (18, 23, 27, 22),
                        9: (19, 24, 28, 23),
                        10: (20, 25, 29, 24),
                        11: (21, 26, 30, 25),
                        12: (27, 32, 36, 31),
                        13: (28, 33, 37, 32),
                        14: (29, 34, 38, 33),
                        15: (30, 35, 39, 34)}

            s_nrs = (5, 6, 7,
                     9, 10, 11, 12,
                     14, 15, 16,
                     18, 19, 20, 21,
                     23, 24, 25,
                     27, 28, 29, 30,
                     32, 33, 34)

        elif progress.eval_size == 96:
            # eval_line3
            if progress.eval_loc == 1:
                # side 1
                # locs = 1, 2, 3, 4, 10, 9, 11, 5, 6, 7, 8, 15, 16, 14, 13, 12, 11, 17, 18, 19, 20, 21, 22, 23, 24
                return (102, 103, 104, 105, 106, 107, 108, 9, 10, 11, 12, 13, 14, 15, 16,
                        110, 111, 112, 113, 114, 115, 116, 17, 18, 19, 20, 21, 22, 23, 24)
            elif progress.eval_loc == 2:
                # side 2
                # locs = 8, 16, 24, 32, 15, 7, 23, 40, 48, 56, 64, 55, 63, 47, 39, 31, 6, 14, 22, 30, 38, 46, 54, 62
                return (16, 24, 32, 40, 48, 56, 64, 108, 116, 124, 132, 140, 148, 156, 164,
                        15, 23, 31, 39, 47, 55, 63, 107, 115, 123, 131, 139, 147, 155, 163)
            elif progress.eval_loc == 3:
                # side 3
                # locs = 57, 58, 59, 60, 50, 49, 51, 61, 62, 63, 64, 55, 56, 54, 53, 52, 41, 42, 43, 44, 45, 46, 47, 48
                return (158, 159, 160, 161, 162, 163, 164, 57, 58, 59, 60, 61, 62, 63, 64,
                        150, 151, 152, 153, 154, 155, 156, 49, 50, 51, 52, 53, 54, 55, 56)
            else:
                # side 4
                # locs = 1, 9, 17, 25, 10, 2, 18, 33, 41, 49, 57, 50, 58, 42, 34, 26, 3, 11, 19, 27, 35, 43, 51, 59
                return (9, 17, 25, 33, 41, 49, 57, 102, 110, 118, 126, 134, 142, 150, 158,
                        10, 18, 26, 34, 42, 50, 58, 103, 111, 119, 127, 135, 143, 151, 159)

        elif progress.eval_size in (20, 25, 32, 36, 48, 64):
            locs = side_nrs = s_nrs = None

        else:
            locs = (progress.eval_loc,)
            side_nrs = {0: (0, 1, 2, 3)}
            s_nrs = (0, 1, 2, 3)

        # calculate the segments
        if side_nrs is not None:
            segments = dict()
            for p_nr, ps_nrs in side_nrs.items():
                segments[ps_nrs[0]] = calc_segment(locs[p_nr], 1)
                segments[ps_nrs[1]] = calc_segment(locs[p_nr], 2)
                segments[ps_nrs[2]] = calc_segment(locs[p_nr], 3)
                segments[ps_nrs[3]] = calc_segment(locs[p_nr], 4)
            # for
            segments_todo = [segments[s_nr] for s_nr in s_nrs]
        else:
            segments_todo = None

        return segments_todo

    def _get_progress(self, processor):
        objs = EvalProgress.objects.filter(processor=processor).order_by('eval_size', 'eval_loc', 'segment')
        for obj in objs:
            obj.updated_str = timezone.localtime(obj.updated).strftime("%Y-%m-%d %H:%M")
            obj.done_count = obj.todo_count - obj.left_count
            obj.segments_todo = self._get_segments(obj)

            # split solve_order into several lines of 50 long each
            obj.solve_lines = []
            while len(obj.solve_order) > 50:
                pos = obj.solve_order.find(',', 50)
                if pos < 0:
                    # no comma found, so take remainder of the line
                    pos = len(obj.solve_order)
                obj.solve_lines.append(obj.solve_order[:pos+1])
                obj.solve_order = obj.solve_order[pos+2:]
            # while
            obj.solve_lines.append(obj.solve_order)
            obj.solve_order = ''
        # for
        return objs

    @staticmethod
    def _find_work(processor):
        work = (Work
                .objects
                .filter(done=False,
                        processor=processor)
                .order_by('-doing',
                          'priority',
                          'start_after',
                          'location'))

        for job in work:
            if job.doing:
                job.status_str = 'doing'
            else:
                job.status_str = 'wait'
        # for

        return work

    @staticmethod
    def _make_sol_loc(loc, sol, seg2sides, unused, is_last=False):
        seg1 = calc_segment(loc, 1)
        seg2 = calc_segment(loc, 2)
        seg3 = calc_segment(loc, 3)
        seg4 = calc_segment(loc, 4)

        try:
            sides1 = seg2sides[seg1]
        except KeyError:
            sides1 = []

        try:
            sides2 = seg2sides[seg2]
        except KeyError:
            sides2 = []

        try:
            sides3 = seg2sides[seg3]
        except KeyError:
            sides3 = []

        try:
            sides4 = seg2sides[seg4]
        except KeyError:
            sides4 = []

        if is_last:
            limit = 289 + 289 + 17 + 17
        else:
            limit = 50

        if len(sides1) + len(sides2) + len(sides3) + len(sides4) < limit:
            p2x2_nrs = {1: [], 2: [], 3: [], 4: []}     # [base_nr] = [nr, nr, ..]
            unused1 = unused[:]
            unused2 = unused[:]
            unused3 = unused[:]
            unused4 = unused[:]
            if loc == 10:
                unused1 = [208]
            elif loc == 15:
                unused2 = [255]
            elif loc == 36:
                unused2 = [139]
            elif loc == 50:
                unused3 = [181]
            elif loc == 55:
                unused4 = [249]
            for p2x2 in Piece2x2.objects.filter(side1__in=sides1, side2__in=sides2, side3__in=sides3, side4__in=sides4,
                                                nr1__in=unused1, nr2__in=unused2, nr3__in=unused3, nr4__in=unused4):
                # print('p2x2=%s' % p2x2.nr)
                if p2x2.nr1 not in p2x2_nrs[1]:
                    p2x2_nrs[1].append(p2x2.nr1)
                if p2x2.nr2 not in p2x2_nrs[2]:
                    p2x2_nrs[2].append(p2x2.nr2)
                if p2x2.nr3 not in p2x2_nrs[3]:
                    p2x2_nrs[3].append(p2x2.nr3)
                if p2x2.nr4 not in p2x2_nrs[4]:
                    p2x2_nrs[4].append(p2x2.nr4)
            # for

            row_nr = int((loc - 1) / 8)
            base_nr = 2 * (loc - 1) + row_nr * 16
            base_nr += 1
            # print('loc=%s, row_nr=%s, base_nr=%s' % (loc, row_nr, base_nr))

            if is_last:
                if len(p2x2_nrs[1]) == 1 and sol[base_nr].is_empty:
                    sol[base_nr].nr = p2x2_nrs[1][0]
                    sol[base_nr].is_empty = False
                    unused.remove(sol[base_nr].nr)
                if len(p2x2_nrs[2]) == 1 and sol[base_nr + 1].is_empty:
                    sol[base_nr + 1].nr = p2x2_nrs[2][0]
                    sol[base_nr + 1].is_empty = False
                    unused.remove(sol[base_nr + 1].nr)
                if len(p2x2_nrs[3]) == 1 and sol[base_nr + 16].is_empty:
                    sol[base_nr + 16].nr = p2x2_nrs[3][0]
                    sol[base_nr + 16].is_empty = False
                    unused.remove(sol[base_nr + 16].nr)
                if len(p2x2_nrs[4]) == 1 and sol[base_nr + 17].is_empty:
                    sol[base_nr + 17].nr = p2x2_nrs[4][0]
                    sol[base_nr + 17].is_empty = False
                    unused.remove(sol[base_nr + 17].nr)
            else:
                if len(p2x2_nrs[1]) == 1 and len(p2x2_nrs[2]) == 1 and len(p2x2_nrs[3]) == 1 and len(p2x2_nrs[4]) == 1:
                    sol[base_nr].nr = p2x2_nrs[1][0]
                    sol[base_nr].is_empty = False
                    unused.remove(sol[base_nr].nr)

                    sol[base_nr + 1].nr = p2x2_nrs[2][0]
                    sol[base_nr + 1].is_empty = False
                    unused.remove(sol[base_nr + 1].nr)

                    sol[base_nr + 16].nr = p2x2_nrs[3][0]
                    sol[base_nr + 16].is_empty = False
                    unused.remove(sol[base_nr + 16].nr)

                    sol[base_nr + 17].nr = p2x2_nrs[4][0]
                    sol[base_nr + 17].is_empty = False
                    unused.remove(sol[base_nr + 17].nr)

    def _make_sol(self, sol, seg2sides, unused, is_last=False):
        if is_last:
            self._make_sol_loc(10, sol, seg2sides, unused, is_last)
            self._make_sol_loc(15, sol, seg2sides, unused, is_last)
            self._make_sol_loc(50, sol, seg2sides, unused, is_last)
            self._make_sol_loc(55, sol, seg2sides, unused, is_last)
            self._make_sol_loc(36, sol, seg2sides, unused, is_last)
            return

        for loc in range(1, 64+1):
            self._make_sol_loc(loc, sol, seg2sides, unused, is_last)
        # for

        if is_last:
            for loc in (55, 10, 15, 50):
                self._make_sol_loc(loc, sol, seg2sides, unused, is_last)
            # for

        if is_last:
            sol[136].nr = 139
            sol[136].is_empty = False

    @staticmethod
    def _add_claims_to_sol(sol, unused, seg2sides, loc, base_nr):
        seg1 = calc_segment(loc, 1)
        seg2 = calc_segment(loc, 2)
        seg3 = calc_segment(loc, 3)
        seg4 = calc_segment(loc, 4)

        sides1 = seg2sides[seg1]
        sides2 = seg2sides[seg2]
        sides3 = seg2sides[seg3]
        sides4 = seg2sides[seg4]

        qset = Piece2x2.objects.filter(side1__in=sides1, side2__in=sides2, side3__in=sides3, side4__in=sides4)

        unused1 = unused
        unused2 = unused
        unused3 = unused
        unused4 = unused

        if not sol[base_nr].is_empty:
            unused1 = [sol[base_nr].nr]

        if not sol[base_nr + 1].is_empty:
            unused2 = [sol[base_nr + 1].nr]

        if not sol[base_nr + 16].is_empty:
            unused3 = [sol[base_nr + 16].nr]

        if not sol[base_nr + 17].is_empty:
            unused4 = [sol[base_nr + 17].nr]

        qset = qset.filter(nr1__in=unused1, nr2__in=unused2, nr3__in=unused3, nr4__in=unused4)

        if sol[base_nr].is_empty:
            nrs = list(qset.distinct('nr1').values_list('nr1', flat=True))
            if len(nrs) == 1:
                sol[base_nr].nr = nrs[0]
                sol[base_nr].has_claim = True
                sol[base_nr].is_empty = False

        if sol[base_nr + 1].is_empty:
            nrs = list(qset.distinct('nr2').values_list('nr2', flat=True))
            if len(nrs) == 1:
                sol[base_nr + 1].nr = nrs[0]
                sol[base_nr + 1].has_claim = True
                sol[base_nr + 1].is_empty = False

        if sol[base_nr + 16].is_empty:
            nrs = list(qset.distinct('nr3').values_list('nr3', flat=True))
            if len(nrs) == 1:
                sol[base_nr + 16].nr = nrs[0]
                sol[base_nr + 16].has_claim = True
                sol[base_nr + 16].is_empty = False

        if sol[base_nr + 17].is_empty:
            nrs = list(qset.distinct('nr4').values_list('nr4', flat=True))
            if len(nrs) == 1:
                sol[base_nr + 17].nr = nrs[0]
                sol[base_nr + 17].has_claim = True
                sol[base_nr + 17].is_empty = False

    def _make_solution(self, processor, used):
        sol = dict()        # [base] = SimpleNamespace
        wrap = 0
        for base in range(1, 256+1):
            sol[base] = SimpleNamespace(is_empty=True, nr=0, do_break=False, has_claims=False)
            wrap += 1
            if wrap == 16:
                wrap = 0
                sol[base].do_break = True
        # for

        unused = list(range(1, 256+1))

        qset = TwoSideOptions.objects.filter(processor=processor)
        seg2sides = dict()      # [seg] = list(two_side)
        for two in qset:
            try:
                seg2sides[two.segment].append(two.two_side)
            except KeyError:
                seg2sides[two.segment] = [two.two_side]
        # for

        for loc in range(1, 64+1):
            # seg1 = calc_segment(loc, 1)
            # seg2 = calc_segment(loc, 2)
            # seg3 = calc_segment(loc, 3)
            # seg4 = calc_segment(loc, 4)
            #
            # if seg1 not in seg2sides:
            #     sides1 = qset.filter(segment=seg1).values_list('two_side', flat=True)
            #     seg2sides[seg1] = list(sides1)
            #
            # if seg2 not in seg2sides:
            #     sides2 = qset.filter(segment=seg2).values_list('two_side', flat=True)
            #     seg2sides[seg2] = list(sides2)
            #
            # if seg3 not in seg2sides:
            #     sides3 = qset.filter(segment=seg3).values_list('two_side', flat=True)
            #     seg2sides[seg3] = list(sides3)
            #
            # if seg4 not in seg2sides:
            #     sides4 = qset.filter(segment=seg4).values_list('two_side', flat=True)
            #     seg2sides[seg4] = list(sides4)

            loc_str = 'loc%s' % loc
            nr = getattr(used, loc_str)
            if nr > 0:
                row_nr = int((loc - 1) / 8)
                base_nr = 2 * (loc - 1) + row_nr * 16
                base_nr += 1
                # print('loc=%s, row_nr=%s, base_nr=%s' % (loc, row_nr, base_nr))
                try:
                    p2x2 = piece2x2_cache[nr]
                except KeyError:
                    p2x2 = Piece2x2.objects.get(nr=nr)
                    piece2x2_cache[nr] = p2x2

                sol[base_nr].nr = p2x2.nr1
                sol[base_nr].is_empty = False
                if p2x2.nr1 in unused:
                    unused.remove(p2x2.nr1)

                sol[base_nr + 1].nr = p2x2.nr2
                sol[base_nr + 1].is_empty = False
                if p2x2.nr2 in unused:
                    unused.remove(p2x2.nr2)

                sol[base_nr + 16].nr = p2x2.nr3
                sol[base_nr + 16].is_empty = False
                if p2x2.nr3 in unused:
                    unused.remove(p2x2.nr3)

                sol[base_nr + 17].nr = p2x2.nr4
                sol[base_nr + 17].is_empty = False
                if p2x2.nr4 in unused:
                    unused.remove(p2x2.nr4)
        # for

        # for seg in seg2sides.keys():
        #     print('seg2sides[%s] = %s' % (seg, repr(seg2sides[seg])))

        keep_going = True
        while keep_going:
            prev_len = len(unused)
            self._make_sol(sol, seg2sides, unused)

            if len(unused) == prev_len:
                keep_going = False
                # final run
                self._make_sol(sol, seg2sides, unused, True)
        # while

        # parse the claims
        for claim in used.claimed_nrs_single.split(', '):
            if claim:
                # nr:loc
                nr, loc = claim.split(':')
                loc = int(loc)

                row_nr = int((loc - 1) / 8)
                base_nr = 2 * (loc - 1) + row_nr * 16
                base_nr += 1

                self._add_claims_to_sol(sol, unused, seg2sides, loc, base_nr)
        # for

        # convert into an array
        out = []
        for base in range(1, 256+1):
            out.append(sol[base])
        # for
        return out

    @staticmethod
    def _get_used(processor):
        try:
            used = ProcessorUsedPieces.objects.get(processor=processor)
        except ProcessorUsedPieces.DoesNotExist:
            # make a new one
            used = ProcessorUsedPieces(processor=processor)

        used_nrs = []
        for nr in range(1, 256+1):
            nr_str = 'nr%s' % nr
            if getattr(used, nr_str, False):
                used_nrs.append(str(nr))
        # for

        used_len = len(used_nrs)

        blocks = []
        while len(used_nrs) > 15:
            blocks.append(", ".join(used_nrs[:15]) + ',')
            used_nrs = used_nrs[15:]
        # while
        blocks.append(", ".join(used_nrs))

        used.claimed_nrs_single = used.claimed_nrs_single.replace(',', ', ')
        used.claimed_nrs_double = used.claimed_nrs_double.replace(',', ', ')

        return blocks, used, used_len

    def get_context_data(self, **kwargs):
        """ called by the template system to get the context data for the template """
        context = super().get_context_data(**kwargs)

        start = time.monotonic()

        processors = list(TwoSideOptions
                          .objects
                          .distinct('processor')
                          .order_by('processor')
                          .values_list('processor', flat=True))
        if len(processors) == 0:
            processors.append(0)

        if 'nr' in kwargs:
            processor = kwargs['nr']
            if processor in ('auto', 'last'):
                processor = processors[-1]
            else:
                processor = int(processor)
        else:
            processor = processors[-1]

        context['processor'] = processor

        try:
            idx = processors.index(processor)
        except ValueError:
            # not in the list
            pass
        else:
            if idx > 0:
                context['url_prev'] = reverse('Pieces2x2:options-nr', kwargs={'nr': processors[idx - 1]})

            if idx < len(processors) - 1:
                context['url_next'] = reverse('Pieces2x2:options-nr', kwargs={'nr': processors[idx + 1]})

        context['url_last'] = reverse('Pieces2x2:options')

        segment2count = dict()  # [segment] = int
        for segment in range(256):
            segment2count[segment] = 0
        # for
        for option in TwoSideOptions.objects.filter(processor=processor):
            segment2count[option.segment] += 1
        # for
        context['total_options'] = sum(segment2count.values())

        context['used_blocks'], used, context['used_count'] = self._get_used(processor)
        context['used'] = used

        context['compare'] = self._compare_pre(used)

        context['work'] = self._find_work(processor)

        try:
            highlight_segments = [segment for segment, _, _, _ in context['compare']]
        except KeyError:
            highlight_segments = []
        context['squares'] = self._make_squares(segment2count, highlight_segments, processor)

        context['solution'] = self._make_solution(processor, used)

        context['progress'] = self._get_progress(processor)

        context['auto_reload'] = True

        context['duration'] = round(time.monotonic() - start, 2)

        context['show_url'] = reverse('Solutions:show-work', kwargs={'processor': processor})

        return context


class OptionsListView(TemplateView):

    template_name = TEMPLATE_OPTIONS_LIST

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['work'] = (ProcessorUsedPieces
                           .objects
                           .order_by('-processor')          # consistent order
                           .exclude(processor=0)
                           .values('processor',
                                   'from_ring1',
                                   'reached_dead_end',
                                   'choices'))

        ongoing1 = Work.objects.filter(doing=True,
                                       done=False,
                                       priority__lt=3).distinct('processor').values_list('processor', flat=True)
        ongoing1 = list(ongoing1)

        ongoing = Work.objects.filter(doing=True,
                                      done=False).distinct('processor').values_list('processor', flat=True)
        ongoing = list(ongoing)

        work2count = dict()     # [processor] = count
        for work in Work.objects.filter(done=False):
            try:
                work2count[work.processor] += 1
            except KeyError:
                work2count[work.processor] = 1
        # for

        age_limit = time.monotonic() - (2 * 60)     # max 2 minutes old
        query_credits = 15

        for proc in context['work']:
            processor_nr = proc['processor']

            proc['url'] = reverse('Pieces2x2:options-nr', kwargs={'nr': processor_nr})
            try:
                count = work2count[processor_nr]
            except KeyError:
                count = 0
            proc['count'] = count

            ring1_nr = proc['from_ring1']
            try:
                seed = ring1_seed_cache[ring1_nr]
            except KeyError:
                try:
                    seed = Ring1.objects.get(nr=ring1_nr).seed
                except Ring1.DoesNotExist:
                    seed = '?'
                ring1_seed_cache[ring1_nr] = seed
            proc['seed'] = seed

            if not proc['reached_dead_end']:
                try:
                    count, stamp = twoside_count_cache[processor_nr]
                except KeyError:
                    count, stamp = '?', 0

                if stamp < age_limit and query_credits > 0:
                    query_credits -= 1
                    count = TwoSideOptions.objects.filter(processor=processor_nr).count()
                    stamp = time.monotonic()
                    twoside_count_cache[processor_nr] = (count, stamp)

                proc['twosides_count'] = count
            else:
                log = proc['choices'].strip()       # removes last \n
                spl = log.split('\n')               # split lines
                if len(spl) > 0:
                    proc['last_log'] = spl[-1]      # last line

            proc['color'] = None
            if proc['processor'] in ongoing1:
                proc['color'] = 'cyan'
            elif proc['processor'] in ongoing:
                proc['color'] = 'skyblue'
        # for

        return context


# end of file
