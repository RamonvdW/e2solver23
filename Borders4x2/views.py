# -*- coding: utf-8 -*-

#  Copyright (c) 2023 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.http import Http404
from django.urls import reverse
from django.views.generic import TemplateView
from django.templatetags.static import static
from Borders4x2.models import Border4x2


TEMPLATE_VIEW = 'border4x2/show.dtl'


class ShowPiecesView(TemplateView):

    template_name = TEMPLATE_VIEW

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
            nr = int(kwargs['nr'][:12])      # afkappen voor de veiligheid
        except ValueError:
            raise Http404('Not found')

        # maak blokjes van 10
        nr = int((nr - 1) / 10)
        nr = 1 + nr * 10

        context['pieces'] = pieces = Border4x2.objects.filter(nr__gte=nr, nr__lt=nr+10).order_by('nr')
        for piece in pieces:
            base = [piece.nr1, piece.nr2, piece.nr3, piece.nr4, piece.nr5, piece.nr6, piece.nr7, piece.nr8]
            piece.check_bad = len(set(base)) != 16

            piece.img1 = static('pieces/%s.png' % piece.nr1)
            piece.img2 = static('pieces/%s.png' % piece.nr2)
            piece.img3 = static('pieces/%s.png' % piece.nr3)
            piece.img4 = static('pieces/%s.png' % piece.nr4)
            piece.img5 = static('pieces/%s.png' % piece.nr5)
            piece.img6 = static('pieces/%s.png' % piece.nr6)
            piece.img7 = static('pieces/%s.png' % piece.nr7)
            piece.img8 = static('pieces/%s.png' % piece.nr8)

            piece.transform1 = self.rot2transform[piece.rot1]
            piece.transform2 = self.rot2transform[piece.rot2]
            piece.transform3 = self.rot2transform[piece.rot3]
            piece.transform4 = self.rot2transform[piece.rot4]
            piece.transform5 = self.rot2transform[piece.rot5]
            piece.transform6 = self.rot2transform[piece.rot6]
            piece.transform7 = self.rot2transform[piece.rot7]
            piece.transform8 = self.rot2transform[piece.rot8]
        # for

        if nr > 100:
            context['url_prev100'] = reverse('Borders4x2:show-pieces', kwargs={'nr': nr-100})
        if nr > 10:
            context['url_prev10'] = reverse('Borders4x2:show-pieces', kwargs={'nr': nr-10})
        context['url_next10'] = reverse('Borders4x2:show-pieces', kwargs={'nr': nr+10})
        context['url_next100'] = reverse('Borders4x2:show-pieces', kwargs={'nr': nr+100})
        context['url_next1000'] = reverse('Borders4x2:show-pieces', kwargs={'nr': nr+1000})

        return context


# end of file
