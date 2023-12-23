# -*- coding: utf-8 -*-

#  Copyright (c) 2023 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.http import Http404
from django.urls import reverse
from django.utils import timezone
from django.views.generic import TemplateView
from django.templatetags.static import static
from Pieces2x2.models import Piece2x2, TwoSideOptions, EvalProgress
from Pieces2x2.helpers import calc_segment
from types import SimpleNamespace


TEMPLATE_SHOW = 'pieces2x2/show.dtl'
TEMPLATE_OPTIONS = 'pieces2x2/options.dtl'


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

        context['groups'] = groups = list()
        group = list()
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
                group = list()
        # for

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

    def _compare_pre(self, processor, prev_processor):
        segment2count = dict()       # [segment] = int
        prev_segment2count = dict()  # [segment] = int
        for segment in range(256):
            segment2count[segment] = 0
            prev_segment2count[segment] = 0
        # for
        for option in TwoSideOptions.objects.filter(processor=processor):
            segment2count[option.segment] += 1
        # for
        for option in TwoSideOptions.objects.filter(processor=prev_processor):
            prev_segment2count[option.segment] += 1
        # for

        segments = list(segment2count.keys())
        segments.sort()
        compare = list()
        for segment in segments:
            count1 = segment2count[segment]
            count2 = prev_segment2count[segment]
            if count1 != count2:
                tup = (segment, count1, count2, count1 - count2)
                compare.append(tup)
        # for
        return compare

    def _make_squares(self, segment2count, highlight_segments):
        # initialize matrix
        squares = dict()    # [(x,y)] = SimpleNamespace
        for y in range(16+1):
            transform = ''
            if y & 1 == 1:  # odd row
                transform = 'rotate(90deg)'

            for x in range(16+1):
                squares[(x, y)] = SimpleNamespace(break_after=False, transform=transform)
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

            segment = calc_segment(loc, 2)
            count = segment2count[segment]
            squares[(x+1, y)].count = count
            squares[(x+1, y)].highlight = segment in highlight_segments
            squares[(x+1, y)].hue = self._calc_hue(count)

            segment = calc_segment(loc, 3)
            count = segment2count[segment]
            squares[(x, y+1)].count = count
            squares[(x, y+1)].highlight = segment in highlight_segments
            squares[(x, y+1)].hue = self._calc_hue(count)

            segment = calc_segment(loc, 4)
            count = segment2count[segment]
            squares[(x-1, y)].count = count
            squares[(x-1, y)].highlight = segment in highlight_segments
            squares[(x-1, y)].hue = self._calc_hue(count)

            x += 2
            if x > 16:
                x = 1
                y += 2
        # for

        # pack the matrix into an array
        sq_list = list()
        for y in range(16 + 1):
            for x in range(16 + 1):
                square = squares[(x, y)]
                sq_list.append(square)
            # for
        # for

        return sq_list

    def _get_segments(self, progress):
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

        elif progress.eval_size in (25, 36, 48):
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
        # for
        return objs

    def get_context_data(self, **kwargs):
        """ called by the template system to get the context data for the template """
        context = super().get_context_data(**kwargs)

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
                context['compare'] = self._compare_pre(processor, processors[idx - 1])
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

        try:
            highlight_segments = [segment for segment, _, _, _ in context['compare']]
        except KeyError:
            highlight_segments = list()
        context['squares'] = self._make_squares(segment2count, highlight_segments)

        context['progress'] = self._get_progress(processor)

        context['auto_reload'] = True

        return context


# end of file
