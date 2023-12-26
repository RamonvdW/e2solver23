# -*- coding: utf-8 -*-

#  Copyright (c) 2023 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.http import Http404
from django.urls import reverse
from django.views.generic import TemplateView
from django.templatetags.static import static
from Pieces3x3.models import Piece3x3


TEMPLATE_SHOW = 'pieces3x3/show.dtl'


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
            nr = int(kwargs['nr'][:11])      # afkappen voor de veiligheid
        except ValueError:
            raise Http404('Not found')

        # maak blokjes van 5 rijen van 4 breed = 20
        nr = int((nr - 1) / 20)
        nr = 1 + nr * 20

        if nr > 1000:
            context['url_prev1000'] = reverse('Pieces3x3:show', kwargs={'nr': nr-1000})
        if nr > 100:
            context['url_prev100'] = reverse('Pieces3x3:show', kwargs={'nr': nr-100})
        if nr > 20:
            context['url_prev20'] = reverse('Pieces3x3:show', kwargs={'nr': nr-20})
        context['url_next20'] = reverse('Pieces3x3:show', kwargs={'nr': nr+20})
        context['url_next100'] = reverse('Pieces3x3:show', kwargs={'nr': nr+100})
        context['url_next1000'] = reverse('Pieces3x3:show', kwargs={'nr': nr+1000})

        context['groups'] = groups = list()
        group = list()
        pieces = Piece3x3.objects.filter(nr__gte=nr, nr__lt=nr+20).order_by('nr')
        for piece in pieces:
            piece.img1 = static('pieces/%s.png' % piece.nr1)
            piece.img2 = static('pieces/%s.png' % piece.nr2)
            piece.img3 = static('pieces/%s.png' % piece.nr3)
            piece.img4 = static('pieces/%s.png' % piece.nr4)
            piece.img5 = static('pieces/%s.png' % piece.nr5)
            piece.img6 = static('pieces/%s.png' % piece.nr6)
            piece.img7 = static('pieces/%s.png' % piece.nr7)
            piece.img8 = static('pieces/%s.png' % piece.nr8)
            piece.img9 = static('pieces/%s.png' % piece.nr9)

            piece.transform1 = self.rot2transform[piece.rot1]
            piece.transform2 = self.rot2transform[piece.rot2]
            piece.transform3 = self.rot2transform[piece.rot3]
            piece.transform4 = self.rot2transform[piece.rot4]
            piece.transform5 = self.rot2transform[piece.rot5]
            piece.transform6 = self.rot2transform[piece.rot6]
            piece.transform7 = self.rot2transform[piece.rot7]
            piece.transform8 = self.rot2transform[piece.rot8]
            piece.transform9 = self.rot2transform[piece.rot9]

            group.append(piece)
            if len(group) == 4:
                groups.append(group)
                group = list()
        # for

        return context


# end of file
