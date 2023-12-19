# -*- coding: utf-8 -*-

#  Copyright (c) 2023 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.http import Http404
from django.urls import reverse
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

    @staticmethod
    def _get_progress(processor):
        objs = EvalProgress.objects.filter(processor=processor).order_by('eval_size', 'eval_loc')
        for obj in objs:
            obj.updated_str = obj.updated.strftime("%Y-%m-%d %H:%M")
            obj.done_count = obj.todo_count - obj.left_count
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
