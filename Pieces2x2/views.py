# -*- coding: utf-8 -*-

#  Copyright (c) 2023 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.http import Http404
from django.urls import reverse
from django.views.generic import TemplateView
from django.templatetags.static import static
from Pieces2x2.models import Piece2x2, TwoSideOptions
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
        hue = int(count * (120 / 289))
        return 120 - hue        # low number = green, higher number = red

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

        x = 1
        y = 1
        for loc in range(1, 64+1):
            squares[(x, y)].loc = loc

            segment = calc_segment(loc, 1)
            count = segment2count[segment]
            squares[(x, y-1)].count = count
            squares[(x, y-1)].hue = self._calc_hue(count)

            segment = calc_segment(loc, 2)
            count = segment2count[segment]
            squares[(x+1, y)].count = count
            squares[(x+1, y)].hue = self._calc_hue(count)

            segment = calc_segment(loc, 3)
            count = segment2count[segment]
            squares[(x, y+1)].count = count
            squares[(x, y+1)].hue = self._calc_hue(count)

            segment = calc_segment(loc, 4)
            count = segment2count[segment]
            squares[(x-1, y)].count = count
            squares[(x-1, y)].hue = self._calc_hue(count)

            x += 2
            if x > 16:
                x = 1
                y += 2
        # for

        context['squares'] = sq_list = list()
        for y in range(16 + 1):
            for x in range(16 + 1):
                square = squares[(x, y)]
                sq_list.append(square)
            # for
        # for

        return context



# end of file
